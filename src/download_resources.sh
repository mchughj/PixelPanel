#!/bin/bash
echo "`date` - downloading resources directory...."
/home/pi/Dropbox-Uploader/dropbox_uploader.sh -f /home/pi/.dropbox_uploader download projects/PixelPanel/resources /home/pi/PixelPanel/ 
chmod a+rw /home/pi/PixelPanel/resources/*
