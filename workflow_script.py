#!/usr/bin/python
import sys, traceback
import cv2
import numpy as np
import argparse
import string
from plantcv import plantcv as pcv
import os
import json

### Parse command-line arguments
def options():
    parser = argparse.ArgumentParser(
        description="Imaging processing with opencv")
    parser.add_argument("-i",
                        "--image",
                        help="Input image file.",
                        required=True)
    parser.add_argument("-o",
                        "--outdir",
                        help="Output directory for image files.",
                        required=False)
    parser.add_argument("-r", "--result", help="result file.", required=False)
    parser.add_argument("-w",
                        "--writeimg",
                        help="write out images.",
                        default=False,
                        action="store_true")
    parser.add_argument(
        "-D",
        "--debug",
        help=
        "can be set to 'print' or None (or 'plot' if in jupyter) prints intermediate images.",
        default=None)
    args = parser.parse_args()
    return args


def createMask(img):
    b_img = pcv.rgb2gray_lab(img, 'b')
    thresh = pcv.threshold.binary(b_img, 135, 255, 'light')
    fill = pcv.fill(thresh, 100)
    seedmask = pcv.dilate(fill, 3, 3)
    roots = pcv.apply_mask(img, pcv.invert(seedmask), 'black')
    l_img = pcv.rgb2gray_lab(roots, 'l')
    thresh_l = pcv.threshold.binary(l_img, 85, 255, 'light')
    mask = pcv.fill(thresh_l, 275)
    mask = pcv.dilate(mask, 3, 2)
    mask = pcv.gaussian_blur(mask, (9,9))
    return (mask)

### Main workflow
def main():
    # Get options
    args = options()

    pcv.params.debug = args.debug  #set debug mode
    pcv.params.outdir = args.outdir  #set output directory
    pcv.params.line_thickness = 4
    pcv.params.text_size = 2
    pcv.params.text_thickness = 4
    pcv.params.dpi = 150
    
    # The result file should exist if plantcv-workflow.py was run
    if os.path.exists(args.result):
        # Open the result file
        results = open(args.result, "r")
        # The result file would have image metadata in it from plantcv-workflow.py, read it into memory
        metadata = json.load(results)
        # Close the file
        results.close()
        #
        plantbarcode = metadata['metadata']['plantbarcode']['value']
        timestamp = metadata['metadata']['timestamp']['value']
        
    print(timestamp)      
    img, pn, fn = pcv.readbayer(args.image)
    mask = createMask(img)
    masked_img = pcv.apply_mask(img, mask, 'black')

    # Find roots in image
    rootr, rooth = pcv.find_objects(img, mask)

    # Filter objects in image based on ROI filter
    dishr, dishh = pcv.roi.circle(mask, 1750, 1300, 400)
    obj, obj_h, obj_mask, _ = pcv.roi_objects(img, dishr, dishh, rootr, rooth)

    pcv.print_image(
        obj_mask, filename=os.path.join(args.outdir, timestamp+'_mask.png')
    )  #   (os.path.join(pn,os.path.splitext(fn)[0]+'_masked.png'))

    if len(np.unique(obj_mask)) > 1:

        # Create skeleton of roots
        skeleton = pcv.morphology.skeletonize(mask=obj_mask)

        # Prune the skeleton
        pruned, seg_img, edge_objects = pcv.morphology.prune(skel_img=skeleton,
                                                             size=10,
                                                             mask=obj_mask)

        if len(edge_objects) > 0:
            # Identify branch points
            branch_pts_mask = pcv.morphology.find_branch_pts(skel_img=pruned,
                                                             mask=obj_mask)

            # Identify tip points
            tip_pts_mask = pcv.morphology.find_tips(skel_img=pruned,
                                                    mask=obj_mask)

            # Identify segments
            segmented_img, labeled_img = pcv.morphology.segment_id(
                skel_img=pruned, objects=edge_objects, mask=obj_mask)

            # Measure path lengths of segments
            labeled_img2 = pcv.morphology.segment_path_length(
                segmented_img=segmented_img, objects=edge_objects)

            if args.writeimg:
                pcv.print_image(labeled_img2,
                                filename=os.path.join(args.outdir,
                                                    timestamp+'_length.png'))

            # Measure angle of roots
            labeled_img4 = pcv.morphology.segment_angle(
                segmented_img=segmented_img, objects=edge_objects)

            if args.writeimg:
                pcv.print_image(labeled_img4,
                                filename=os.path.join(args.outdir,
                                                    timestamp+'_angle.png'))

    pcv.print_results(args.result)

if __name__ == '__main__':
    main()