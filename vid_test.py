#! /usr/bin/python3
from picamera2 import Picamera2
import time
from pprint import pprint

cam = Picamera2()
cam.create_video_configuration(main={"size": (640,480)})

pprint(cam.sensor_modes)
cam.start_and_record_video("py-test.mp4");

time.sleep(10.0)
cam.stop_recording();
