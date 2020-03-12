#!/bin/bash
echo "`date` - starting server...." | tee -a /home/pi/PixelPanel/logs/server.txt
python3 /home/pi/PixelPanel/src/server.py 2>&1 | tee -a /home/pi/PixelPanel/logs/server.txt
echo "`date` - server ended...." | tee -a /home/pi/PixelPanel/logs/server.txt
