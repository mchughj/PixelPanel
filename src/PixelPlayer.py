
import logging
import random
import time
from os import listdir
import os.path
from PixelImage import AnimatedImageLoader

class PixelPlayer:
  def __init__(self, defaultFrameDuration, resizeType, matrix, resourcePath, lock):
    self.image = None
    self.imageFilename= None
    self.defaultFrameDuration = defaultFrameDuration
    self.resizeType = resizeType
    self.matrix = matrix
    self.runRandom = False
    self.resourcePath = resourcePath
    self.lock = lock

  def loadImage(self, filename):
    with self.lock:
      self.imageFilename = filename
      self.image = AnimatedImageLoader.open(filename, self.resizeType, self.defaultFrameDuration)
      self.runRandom = False
      self.randomTimeDelay = 0
      self.nextRandomTime = 0
      self.frameDisplayStart = int(round(time.time() * 1000))
      logging.debug("image loaded; filename: %s", filename)
      self.matrix.Clear()
      self.matrix.SetImage(self.image.getNextFrame())

  def runRandomFile(self, rTime):
    logging.debug("Going to get all files for random choice")
    onlyfiles = [f for f in listdir(self.resourcePath) if os.path.isfile(os.path.join(self.resourcePath, f))] 
  
    logging.debug("Done getting files")
    f = random.choice(onlyfiles)
    logging.debug("Chose the file; filename: %s", f)

    try:
        self.loadImage(os.path.join(self.resourcePath, f))
    except:
        logging.exception("Unexpectedfile; will recurse")
        self.runRandomFile(rTime)
        return

    self.runRandom = True
    self.randomTimeDelay = rTime
    self.nextRandomTime = time.time() * 1000 + self.randomTimeDelay

  def playNextFrame(self):
    currentTime = int(round(time.time() * 1000))
    elapsedTime = currentTime - self.frameDisplayStart

    if self.runRandom == True and currentTime > self.nextRandomTime:
      self.runRandomFile(self.randomTimeDelay)
      return self.image.getFrameDuration()

    if elapsedTime < self.image.getFrameDuration():
      timeToWait = self.image.getFrameDuration() - elapsedTime
      logging.debug("Not enough time has passed for the frame; frameDisplayStart: %d, currentTime: %d, elapsedTime: %d, sleeping: %d", 
          self.frameDisplayStart, currentTime, elapsedTime, timeToWait)
      return timeToWait

    self.frameDisplayStart = currentTime
    if self.image.isAnimated():
      with self.lock:
        i2 = self.image.getNextFrame()
        self.matrix.SetImage(i2)

    return self.image.getFrameDuration()

  def playContinuous(self):
    logging.info('playContinuous: starting...')
    while True:
      if self.image is None:
        time.sleep(1)
      else:
        timeToSleep = self.playNextFrame()
        time.sleep(timeToSleep)
