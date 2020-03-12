#!/usr/bin/env python3
import time
import sys
import argparse
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import random
import requests
import shutil
import os
import os.path

from threading import Lock, Thread

from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import partial
import logging
import urllib.parse

from PixelPlayer import PixelPlayer

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

parser = argparse.ArgumentParser(description='Server for pixel panel')
parser.add_argument('--port', type=int, help='Port to listen on', default=8080)
parser.add_argument('--defaultFrameDuration', type=float, help='Default seconds between frames when no specific data in file', default=0.06)
parser.add_argument('--resize', choices=['nearest','bilinear','bicubic','lanczos','nearest'], help='Type of resize algorithm', default='nearest')

config = parser.parse_args()

resourcePath = "/home/pi/PixelPanel/resources/"
tmpResourcePath = "/home/pi/PixelPanel/resources/tmp/"

# Used to synchronize between threads
lock = Lock()

#
# class RGBMatrixOptions:
#   pass
#
#class RGBMatrix:
#  def __init__(self, options):
#    pass
#
#  def SetImage(self, i):
#    pass
#

# Configuration for the RGB matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat' 

matrix = RGBMatrix(options = options)

class MyHandler(BaseHTTPRequestHandler):
  def __init__(self, pixelPlayer, *args, **kwargs):
    self.pixelPlayer = pixelPlayer
    super(MyHandler, self).__init__(*args, **kwargs)

  def send(self, s):
    self.wfile.write(bytes(s,"utf-8"))

  def showPlayUI(self):
    logging.info("showPlayUI; resourcePath: %s", resourcePath)
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<head>")
    self.send("<style>")
    self.send("table, th, td {")
    self.send("  border: 1px solid black;")
    self.send("  border-collapse: collapse;")
    self.send("}")
    self.send("</style>")
    self.send("</head>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Currently playing filename: ")
    if self.pixelPlayer.imageFilename is None:
      self.send("NONE!")
    else:
      self.send(self.pixelPlayer.imageFilename)
    self.send("<br><br>")
    self.send("Show <a href=\"/preview\">preview UI</a>.")
    self.send("<br><br>")

    self.send("Play <a href=\"random?time=13\">Random</a>.");
    self.send("<br><br>")

    self.send("Resources<br>")
    self.send("<table style=\"width:50%\">")
    self.send("<tr><th>Filename</th><th>Play</th></tr>")
    onlyfiles = [f for f in os.listdir(resourcePath) if os.path.isfile(os.path.join(resourcePath, f))] 
    onlyfiles.sort()
    for filename in onlyfiles:
      self.send("<tr><td>")
      self.send(filename)
      self.send("</td><td>")
      urlEncodedArgs = urllib.parse.urlencode({'file' :filename })
      self.send("<a href=\"/play?{args}\">Play</a>".format(args=urlEncodedArgs))
      self.send("</td>")
    self.send("</table>")
    self.send("</html>")


  def showPreviewUI(self):
    logging.info("showPreviewUI!")
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<head>")
    self.send("</head>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Currently playing filename: ")
    if self.pixelPlayer.imageFilename is None:
      self.send("NONE!")
    else:
      self.send(self.pixelPlayer.imageFilename)
    self.send("<br><br>")
    self.send("File to test:<br>")
    self.send("<form method=\"get\" action=\"preview\">URL: <input size=\"127\" type=\"text\" name=\"URL\">  <input type=\"submit\" value=\"Submit\"></form>")
    self.send("</html>")


  def play(self, filename):
    fullFilename = os.path.join(resourcePath, filename)
    logging.debug("Going to play file: %s", fullFilename)

    self.pixelPlayer.loadImage(fullFilename)
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Starting file!  <a href=\"/\">Return</a>")
    self.send("</html>")

  def random(self, time):
    time_delay = int(time)
    logging.debug("Going to play random; time: %d", time_delay)
    self.pixelPlayer.runRandomFile(time_delay*1000)
    logging.debug("Done instructing to play random")
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Starting random run!  <a href=\"/\">Return</a>")
    self.send("</html>")
    logging.debug("Done with response to play random")

  def preview(self, url):
    index = url.rfind('/')
    filename = url[index+1:]

    logging.debug("Going to preview: %s", url)
    logging.debug("Index: %d", index)
    logging.debug("Save it into file: %s", filename)

    # Open the url image, set stream to True, this will return the stream content.
    response = requests.get(url, stream=True)

    tFilename = tmpResourcePath + filename

    # Open a local file with wb ( write binary ) permission.
    logging.debug("Saving temporary file into: %s", filename)
    with open(tFilename, 'wb') as local_file:
      # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
      response.raw.decode_content = True
     
      # Copy the response stream raw data to local image file.
      shutil.copyfileobj(response.raw, local_file)

    # Remove the image url response object.
    del response

    self.pixelPlayer.loadImage(tFilename)

    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Previewing file: " + url )
    self.send("<BR>")
    self.send("Saved as: " + tFilename )
    self.send("<BR>")

    self.send("<br><br>")
    self.send("If you like the results then consider moving the temporary file into the resources directory.<br>")
    self.send("<form method=\"get\" action=\"movetmp\">Tmp Filename: <input size=\"127\" type=\"text\" name=\"tmpfilename\" value=\"" + filename + "\">")
    self.send("<br>Final Filename: <input size=\"127\" type=\"text\" name=\"finalfilename\" value=\"" + filename + "\">")
    self.send("<BR><input type=\"submit\" value=\"Submit\"></form>")

    self.send("<a href=\"/preview\">Preview another</a> or <a href=\"/\">Main menu</a>")

    self.send("</html>")

    logging.debug("Done with response to preview")

  def movetmp(self, tmpFilename, finalFilename):
    tmpFilename = os.path.join(tmpResourcePath, tmpFilename)
    finalFilename = os.path.join(resourcePath, finalFilename)

    logging.debug("Going to move: %s", tmpFilename)
    logging.debug("Save it into file: %s", finalFilename)

    shutil.copyfile(tmpFilename, finalFilename)
    os.system( "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload " + finalFilename + " Projects/PixelPanel/resources")

    self.pixelPlayer.loadImage(finalFilename)

    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.send("<html>")

    self.send("<h1>Pixel Server</h1>")
    self.send("Copied file into: " + finalFilename )
    self.send("<BR>")
    self.send("Playing file now! <BR><BR><a href=\"/\">Return</a>")
    self.send("</html>")
    logging.debug("Done with response to movetmp")

  def do_GET(self):
    logging.debug("received a GET request; path: %s", self.path)
    try:
      if self.path == "/":
        self.showPlayUI()
      elif self.path == "/favicon.ico":
        self.send_error(404)
      elif self.path.startswith("/play?"):
        args = urllib.parse.parse_qs(self.path[6:])
        self.play(args["file"][0])
      elif self.path == ("/preview"):
        self.showPreviewUI()
      elif self.path.startswith("/preview?"):
        args = urllib.parse.parse_qs(self.path[9:])
        self.preview(args["URL"][0])
      elif self.path.startswith("/movetmp?"):
        args = urllib.parse.parse_qs(self.path[9:])
        self.movetmp(args["tmpfilename"][0], args["finalfilename"][0])
      elif self.path.startswith("/random?"):
        args = urllib.parse.parse_qs(self.path[8:])
        self.random(args["time"][0])
      else:
        logging.debug("Unexpected request")

    except:
      logging.exception("Error in handling request")
      self.send_error(404,'File Not Found: %s' % self.path)

    logging.debug("Done with request")

def main():
  logging.info('Starting thread for matrix player...')
  p = PixelPlayer(config.defaultFrameDuration, config.resize, matrix, resourcePath, lock)
  t = Thread(target=p.playContinuous)
  t.setDaemon(True)
  t.start()

  try:
    handler = partial(MyHandler, p)
    server = HTTPServer(('', config.port), handler)
    logging.info('Starting httpserver...')
    server.serve_forever()
  except KeyboardInterrupt:
    logging.info('^C received, shutting down server')
    server.socket.close()
  logging.info('Stopping...')

if __name__ == '__main__':
  main()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab ignorecase
