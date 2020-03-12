# PixelPanel
This repo contains the source code for a 32x32 Pixel Panel that runs on a raspberry PI and utilizes a 32x32 matrix display.  

![PixelPanel In Action](/documentation/PixelPanel1.jpg)

The specific hardware used in this project includes:
 * [32X32 RGB Panel](https://www.adafruit.com/product/1484)
 * [Raspberry PI Hat](https://www.adafruit.com/product/2345)
 * Raspberry PI 2
 
For initial installation follow the instructions found [Here](https://learn.adafruit.com/raspberry-pi-rgb-led-matrix-webapp?view=all).

To start the http server instance use:

cd ~/PixelPanel/src/
./start_server.py


Initially I used Dropbox as a mechanism to copy files from random computers into the Raspberry PI.  I used
[Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader) in order to synchronize files.  This 
worked well for a time but after I added the ability to go out and grab a random animated gif and preview 
it I stopped using that functionality.
