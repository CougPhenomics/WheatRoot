python.exe %CONDA_PREFIX%\Scripts\plantcv-workflow.py --dir data\images ^
--adaptor filename ^
--workflow workflow_script.py ^
--type tif ^
--json roots.json ^
--outdir output ^
--meta measurementlabel,other,plantbarcode,timestamp,id ^
--delimiter "(.+)_(.+)_(.{2})_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3})_(\d{1})" ^
--timestampformat "%%Y-%%m-%%d_%%H-%%M-%%S.%%f" ^
--writeimg ^
--create
REM --other "--debug "print"" ^
REM --dates 2019-06-11-07-00-00_2019-06-11-11-00-00

python.exe %CONDA_PREFIX%\Scripts\plantcv-utils.py json2csv -j roots.json -c roots.csv
