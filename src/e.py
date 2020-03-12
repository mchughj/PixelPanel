
import argparse
from PIL import Image
from PIL import GifImagePlugin

from PixelImage import AnimatedImageLoader

parser = argparse.ArgumentParser(description='Test program for images')
parser.add_argument('--file', type=str, help='File to open', default="../resources/wizard.gif")
config = parser.parse_args()

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
