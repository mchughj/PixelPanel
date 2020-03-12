#!/usr/bin/env python
import time
import sys
import logging
import argparse
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PixelImage import AnimatedImageLoader

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

parser = argparse.ArgumentParser(description='Display a sprite sheet on a matrix.')
parser.add_argument('file', type=str, metavar='N', help='The sprite file')
parser.add_argument('--speed', type=float, help='Delay between frames', default=0.06)
parser.add_argument('--resize', choices=['nearest','bilinear','bicubic','lanczos','nearest'], help='Type of resize algorithm', default='nearest')
a = parser.parse_args()

if a.file is None:
    parser.print_help()
    sys.exit("Require an image argument")

image = AnimatedImageLoader.open(a.file, a.resize, a.speed)

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)
print ("image x width: {w}".format(w=image.getFrameSize()))

if not image.isAnimated():
    print ("Static image here.  Sitting and spinning")
    while True:
        pass
else:
    frameDisplayStartMillis = 0
    while True:
        currentTimeMillis = int(round(time.time() * 1000))
        elapsedTimeMillis = currentTimeMillis - frameDisplayStartMillis

        durationForFrameMillis = image.getFrameDuration() * 1000
        # logging.debug("currentTimeMillis: %f, frameDisplayStartMillis: %f, elapsedTimeMillis: %f, frameDurationMillis: %f", currentTimeMillis, frameDisplayStartMillis, elapsedTimeMillis, durationForFrameMillis)
        if elapsedTimeMillis < durationForFrameMillis:
            timeToSleepMillis = durationForFrameMillis - elapsedTimeMillis
            time.sleep(timeToSleepMillis / 1000)

        frameDisplayStartMillis = int(round(time.time() * 1000))
        i2 = image.getNextFrame()
        matrix.SetImage(i2)
