# PixelPanel
This repo contains the source code for a 32x32 Pixel Panel that runs on a raspberry PI and utilizes a 32x32 matrix display.  

![PixelPanel In Action](/documentation/PixelPanel1.jpg)

The specific hardware used in this project includes:
 * [32X32 RGB Panel](https://www.adafruit.com/product/1484)
 * [Raspberry PI Hat](https://www.adafruit.com/product/2345)
 * Raspberry PI 2
 
For initial installation follow the instructions found in the [RGB Matrix Hat](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi?view=all) documentation.  This will get the system running for both C and python programs.

# Configuring the Raspberry PI

There is quite a bit of flicker on the panel if you don't tightly control the environment.  Here is a list that worked well from me that was [culled from troubleshooting documentat](https://github.com/hzeller/rpi-rgb-led-matrix#troubleshooting).
1 Make sure that you run the program as sudo.  Setting the options correctly (as I have done in server.py) will have it drop the privileges immediately after the matrix is initialized.
1 Set the boot options to not use a GUI.  sudo raspi-config then choose boot options.
1 Switch off on-board sound (dtparam=audio=off in /boot/config.txt).
1 Add 'isolcpus=3' to the end of the line of /boot/cmdline.txt

# Starting the server

To start the http server instance use:

cd ~/PixelPanel/src/
./start_server.py


Initially I used Dropbox as a mechanism to copy files from random computers into the Raspberry PI.  I used
[Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader) in order to synchronize files.  This 
worked well for a time but after I added the ability to go out and grab a random animated gif and preview 
it I stopped using that functionality.
