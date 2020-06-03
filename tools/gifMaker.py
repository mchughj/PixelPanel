
# Simple program to convert a directory containing a bunch of numbered images into 
# an animated gif.  I've found that these are quite common but don't want to extend
# various programs to deal with that.  
#
# Resulting image is named based on the last component of the path unless an optional
# command line arg is given.
#
# This program assumes that every image in the directory has a numeric name and 
# indicates the ordering. It assumes all files are .png files and ignores any
# .gif files within the directory too in case you are placing the output gif in
# the directory and want to run the script multiple times.

import argparse
import os
import sys

from PIL import Image

parser = argparse.ArgumentParser(description='Combine image files into a single animated gif')
parser.add_argument('--dir', type=str, help='Directory to open', required=True)
parser.add_argument('--output', type=str, help='Name of file to write the result to.  If not specified then one will be inferred')
config = parser.parse_args()

dir = os.path.normpath(config.dir)
outputFilename = os.path.basename(dir) + ".gif"
if config.output:
    outputFilename = config.output

print("Locating files in directory: {}".format(dir))

if not os.path.isdir(dir):
    print("Directory does not exist")
    sys.exit(0)

files = os.listdir(dir)
pngFiles = [x for x in files if x.find(".png") != -1]
pngFiles.sort(key=lambda x: int(x[:x.find(".")]))
print("Found files, number: {}".format(len(pngFiles)))

# Do a pass over all the files to look for the size of the 
# images.  This enables us to recenter each image as we open
# it and process it for the final .gif.
maxWidth = 0
maxHeight = 0
defaultBackgroundColor = 0
for f in pngFiles:
    filename = os.path.join(dir, f)
    i = Image.open(filename)
    if maxWidth < i.size[0]:
        maxWidth = i.size[0]
    if maxHeight < i.size[1]:
        maxHeight = i.size[1]

print("maximum dimensions: ({},{})".format(maxWidth, maxHeight))

images = []
for f in pngFiles:
     filename = os.path.join(dir, f)
     i = Image.open(filename)

     actualFrame = Image.new(mode = 'RGB', size=(maxWidth, maxHeight), color=defaultBackgroundColor)
     offsetX = int((maxWidth - i.size[0]) / 2)
     offsetY = int((maxHeight - i.size[1]) / 2)
     actualFrame.paste(i, (offsetX, offsetY))
     images.append(actualFrame)

print("Saving the file; name: {}".format(outputFilename))
try:
    images[0].save(outputFilename, save_all=True, append_images=images[1:], optimize=False, duration=10)
except:
    e = sys.exc_info()[0]
    print("Unable to save file: {}".format(str(e)))

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab ignorecase