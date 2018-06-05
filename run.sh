#!/bin/bash
cd ~/golden-hour
/usr/local/bin/pipenv run python3.6 main.py  --post-to-twitter --minutes-before-start 60 -i 24

