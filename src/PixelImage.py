from PIL import Image
from PIL import GifImagePlugin
import logging
import time

def convertResizeType(resizeTypeAsString):
  if resizeTypeAsString == 'nearest':
    return Image.NEAREST
  elif resizeTypeAsString == 'bilinear':
    return Image.BILINEAR
  elif resizeTypeAsString == 'bicubic':
    return Image.BICUBIC
  elif resizeTypeAsString == 'lanczos':
    return Image.LANCZOS

  return Image.NEAREST


class AnimatedImage():
    def __init__(self, image, resizeType):
        self.image = image
        self.currentFrame = 0

        if type(resizeType) == str:
            self.resizeType = convertResizeType(resizeType)
        else:
            self.resizeType = resizeType

    def getNextFrame(self):
        if self.currentFrame == self.getNumFrames():
            self.currentFrame = 0

        result = self.getFrameNumber(self.currentFrame)
        self.currentFrame += 1

        if False:
            result.show()
            time.sleep(10)
            logging.debug("Palette")
            p = result.getpalette()
            for i in range(256):
                logging.debug( "Color %d: %d, %d, %d", i, p[i*3], p[i*3+1],p[i*3+2])

            index = result.getpixel((0,0))
            r = p[index*3]
            g = p[index*3+1]
            b = p[index*3+2]
            logging.debug( "PRE! Looking at the top left pixel; index: %d, color: %d,%d, %d", index, r,g,b)
        result = result.convert('RGBA')

        # If the frame is not 32x32 then center the final frame in a 32 x 32 image
        s = result.size
        if s[0] != 32 or s[1] != 32:
            r = Image.new('RGBA', (32,32))
            offsetX = int(( 32 - s[0] ) / 2)
            offsetY = int(( 32 - s[1] ) / 2)
            # logging.debug("AnimatedImage getNextFrame will be resized; whichFrame: %d, size: %s, offsetX: %d, offsetY: %d", self.currentFrame, s, offsetX, offsetY)
            r.paste(result,(offsetX, offsetY))
            result = r

        # Manually convert any transparent pixel into a black pixel
        data = result.getdata()
        newData = []
        for item in data:
            if item[3] == 0:
                newData.append( (0,0,0,0) )
            else:
                newData.append( ( item[0], item[1], item[2], 0 ) )
        result.putdata(newData)

        # Final conversion into an RGB image which is supported by the Panel.
        return result.convert('RGB')

    def getFrameSize(self):
        return self.size

class AnimatedFrameImage(AnimatedImage):
    def __init__(self, image, resizeType, frameDuration):
        AnimatedImage.__init__(self, image, resizeType)
        self.rawImage = self.image
        self.frameDuration = frameDuration

        if self.image.size[1] != 32:
            d = self.image.size[1] / 32
            newWidth = int(self.image.size[0]/d)
            newHeight = 32

            # Sometimes the image is a single frame and just slightly taller than wide.  
            # This would result in an image which is something like (40, 32).  We don't want 
            # this as the single image frame would be chopped off.  This compresses into a single
            # frame with a width of 32 and a shorter height.
            if newWidth > 32 and newWidth < 64:
                d = newWidth / 32
                newHeight = int(32 / d)
                newWidth = 32
                logging.debug("image has odd size; not going for: (%d, 32), instead: (32, %d)", newWidth, newHeight)

            logging.debug("image resizing; prior size: %s, new size: (%d, %d)", self.image.size, newWidth, newHeight)
            self.image = self.image.resize((newWidth,newHeight),self.resizeType)
            self.numberFrames = int(newWidth/32)
        else:
            # If the width of the image is not a multiple of 32 then I'm going
            # to assume that this is a single frame that needs to be scaled down.
            #
            #  Not enabling this as I haven't found a situation in which it is true!
            if False and self.image.size[0] % 32 != 0:
                d = self.image.size[0] / 32
                newHeight = int(self.image.size[1]/d)
                logging.debug("assuming image is one frame and widder than tall; prior size: %s, new size: (32, %d)", self.image.size, newHeight)
                self.image = self.image.resize((32, newHeight),self.resizeType)
                self.numberFrames = 1
            else:
                self.numberFrames = int(self.image.size[0]/32)

        logging.debug("animated frame image; size: %s, numberFrames: %d", self.image.size, self.numberFrames)

        self.size = (32,32)

    def isAnimated(self):
        return self.numberFrames > 1

    def getNumFrames(self):
        return self.numberFrames

    def getFrameNumber(self, whichFrame):
        frameOffset = whichFrame * 32
        return self.image.crop((frameOffset,0,frameOffset+32,32))

    def getFrameDuration(self):
        return self.frameDuration
        
class AnimatedGifImage(AnimatedImage):
    def __init__(self, image, resizeType):
        AnimatedImage.__init__(self, image, resizeType)
        self.size = self.image.size
        if self.size[0] != 32 or self.size[1] != 32:
          self.resizeNeeded = True
          if self.size[0] > self.size[1]:
            self.resized = (32, int(self.size[1] / (self.size[0] / 32)))
          else:
            self.resized = (int(self.size[0] / (self.size[1] / 32)), 32)
        else:
          self.resizeNeeded = False
          self.resized = (0, 0)
        logging.debug("AnimatedGifImage init; is_animated: %s, n_frames: %d, size: %s, resizeNeeded: %s, resized: %s", self.image.is_animated, self.image.n_frames, self.size, self.resizeNeeded, self.resized)

    def isAnimated(self):
        return self.image.is_animated

    def getNumFrames(self):
        return self.image.n_frames

    def getFrameNumber(self, whichFrame):
        self.image.seek(whichFrame)
        if self.resizeNeeded == False:
          return self.image
        else:
          # logging.debug("AnimatedGifImage getFrameNumber; whichFrame: %d, size: %s, resized: %s", whichFrame, self.image.size, self.resized)
          resize = self.image.resize((self.resized[0], self.resized[1]), self.resizeType)
          return resize

    def getFrameDuration(self):
        return max(self.image.info['duration'] / 1000, 0.06)
        
class AnimatedImageLoader(object):
    def open(filename, resizeType, defaultFrameDuration):
        i = Image.open(filename)
        t = type(i)
        if t == GifImagePlugin.GifImageFile:
            logging.debug("image file type detected; filename: %s, type: GIF, rawType: %s", filename, t)
            return AnimatedGifImage(i, resizeType)
        else:
            logging.debug("image file type detected; filename: %s, type: AnimatedFrame, rawType: %s", filename, t)
            return AnimatedFrameImage(i, resizeType, defaultFrameDuration)
