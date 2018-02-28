import time
import datetime
from io import BytesIO
from picamera import PiCamera
from threading import Thread
import math

THRESHOLD = 200
SENSITIVITY = 7000

CAMERA_WIDTH = 100
CAMERA_HEIGHT = 100
CAMERA_HFLIP = True
CAMERA_VFLIP = True
CAMERA_ROTATION = 0
CAMERA_FRAMERATE = 35


class MotionDetector:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def capture_image(self):
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        im = Image.open(stream)
        im_buffer = im.load()
        return im, im_buffer

    def stop(self):
        # set thread indicator to stop thread
        self.stopped = True

def pix_diff(x,y, im_buff_1, im_buff_2):
    pix_abs = abs(im_buff_1[x,y][1] - buffer2[x,y][1])
    if pix_abs > THRESHOLD:
        return True
    
def checkForMotion(im_buffer_1, im_buffer_2):
    motion_detected = False
    changed_pixels = sum([pix_diff(x,y,im_buffer_1, im_buffer_2) for x,y in zip(xrange(0, CAMERA_WIDTH), xrange(0,CAMERA_HEIGHT))])
    if changed_pixels > SENSITIVITY:
        return True, changed_pixels, SENSITIVITY
    else:
        return False, changed_pixels, SENSITIVITY

def main(md, cb):
    im_1, im_1_buffer = md.capture_image()
    while True:
        im_2, im_2_buffer = md.capture_image
        motionDetected, pixChanges, sensitivity = checkForMotion(im_1_buffer, im_2_buffer)
        if motionDetected:
            cb(pixChanges,sensitivity)
        im_1, im_1_buffer = im_2, im_2_buffer
        
def boot_motion(cb, exit_func):
    try:
        md = MotionDetector().start()
        time.sleep(2.0)
        main(md, cb)
    finally:
        exit_func()

