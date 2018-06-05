#!/bin/bash

yesterday=$(date -d "yesterday 13:00" '+%Y-%m-%d')

echo Uploading Golden hour for $yesterday
filename=golden-hour/output/timelapse_"$yesterday"_000.mp4
echo Filename: $filename 
/usr/local/bin/youtube-upload --title "timelapse $yesterday"  golden-hour/output/timelapse_"$yesterday"_000.mp4
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
echo removing $filename
rm $filename

