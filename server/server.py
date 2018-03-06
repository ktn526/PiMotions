from flask import Flask, Response, send_file, json, request, copy_current_request_context
from io import BytesIO
import base64
import time
from PIL import Image, ImageChops
import tempfile
import logging
from datetime import datetime
import os
import picamera
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
import threading
import math
from motion_detector import boot_motion, stop_detector, start_detector, set_sensitivity, set_threshold, get_threshold, get_sensitivity
from camera import Camera

RUN_CAM = False
ENTROPY_SAMPLE = []


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
camera = Camera()


def get_temp_path(name):
    tempdir = tempfile.mkdtemp()
    date = datetime.now()
    filename = '{}-{}.jpg'.format(name, date)
    path = os.path.join(tempdir, filename)
    return path

def open_image(path):
    img_str = ''
    with open(path, "rb") as imageFile:
        img_str = 'data:image/jpeg;base64,' + base64.b64encode(imageFile.read())
    return img_str
        

def snap():
    img_str = ''
    camera.start()
    try:
        path = get_temp_path('capture')
        camera.device.capture(path)
        img_str = open_image(path)
    except (ValueError, RuntimeError, TypeError, NameError):
        logging.exception("could not capture image")
    finally:
        camera.stop()
    return  (img_str, path)

@app.route('/take')
def take_picture():
    img_str, _ = snap()
    response = Response(
        response = json.dumps({
            'src': img_str
        }),
        status = 200,
        mimetype='application/json'
    )
    return response

@socketio.on('motion-start')
def check_motion():
    @copy_current_request_context
    def send_motion_event(pixChanged, motion_detected):
        emit('motion-detected', {'pixChanged': pixChanged, 'motion': motion_detected})

    @copy_current_request_context
    def motion_exit(e):
        logging.exception(e)
        emit('motion-detector-exit', {'exit': 'there was an error in the detector'})
    start_detector()
    boot_motion(send_motion_event, motion_exit)

    
@socketio.on('set-threshold')
def set_motion_threshold(threshold):
    set_threshold(threshold)
    emit('threshold', {'threshold': threshold})

@socketio.on('set-sensitivity')
def set_motion_threshold(sensitivity):
    set_sensitivity(sensitivity)
    emit('sensitivity', {'sensitivity': sensitivity})

@socketio.on('stop-cam')
def stop():
    stop_detector()

@socketio.on('disconnect')
def diconnect():
    stop_detector()

@socketio.on('connect')
def connect():
    threshold = get_threshold()
    sensitivity = get_sensitivity()
    emit('threshold', {'threshold': threshold})
    emit('sensitivity', {'sensitivity': sensitivity})
    
    
        

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
