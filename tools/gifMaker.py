
import argparse
from PIL import Image
from PIL import GifImagePlugin

from PixelImage import AnimatedImageLoader

parser = argparse.ArgumentParser(description='Combine image files into a single animated gif')
parser.add_argument('--dir', type=str, help='Directory to open')
config = parser.parse_args()

# Steps
# 1/  Create the result image.  Name it the [last directory component].gif
# 2/  Open the directory and read in the filenames
# 3/  For numeric ordering of the files
# 4/  Open the file and add as a frame to the gif.

imageObject = AnimatedImageLoader.open(config.file)
print("Filename: {}".format(config.file))
print("Type: {}".format(type(imageObject)))
print("isAnimated: {}".format(imageObject.isAnimated()))
print("nFrames: {}".format(imageObject.getNumFrames()))
print("size: {}".format(imageObject.getFrameSize()))

# Display individual frames from the loaded animated GIF file
for frame in range(0,imageObject.getNumFrames()*2):
    i = imageObject.getNextFrame()
i = imageObject.getNextFrame()
i.show()
print("size: {}".format(i.size))


# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab ignorecase
