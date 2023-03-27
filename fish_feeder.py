#! /usr/bin/python3
from stepper import do_steps, cleanup 
from flask import Flask, current_app, send_file, send_from_directory, request, Response, render_template
from datetime import datetime
import threading
import time
from picamera2 import Picamera2
import os
from pathlib import Path
import re

app = Flask(__name__)

STEPS_PER_REV = 4096.
STATIONS_PER_REV = 12.
cur_step = 0
cur_station = 0

is_moving = False
is_cam_locked = True

def record_video(length_in_seconds):
    global is_moving
    cam = Picamera2();
    config = cam.create_video_configuration({"size": (640,480)})
    cam.configure(config)
    cam.start_and_record_video("/home/pi/fish_feeder/videos/recording-%d.mp4" % (int(time.time())))
    time.sleep(length_in_seconds + 4.0);
    cam.stop_recording();
    cam.close()
    del cam
    is_moving = False
    

def move_carousel(num_to_move,record=True):
    global is_moving;
    if(record):
        cam = Picamera2();
        config = cam.create_video_configuration({"size": (640,480)})
        cam.configure(config)
        cam.start_and_record_video("/home/pi/fish_feeder/videos/feeding-%d.mp4" % (int(time.time())))
        time.sleep(4.0);
    do_steps(num_to_move);
    if(record):
        time.sleep(14.0);
        cam.stop_recording();
        cam.close()
        del cam
    is_moving = False


@app.route('/')
def index():
    global cur_station, cur_step, is_moving
    manual_move = request.args.get("mm")
    manual_move_remote = request.args.get("mmr") 
    if (is_moving):
        return render_template('in_progress.html');
    if (manual_move is not None):
        cur_step = 0
        cur_station = 0
        is_moving = True
        move_thread = threading.Thread(target=move_carousel,args=(30,False))
        move_thread.start()
    if (manual_move_remote is not None):
        cur_step = 0
        cur_station = 0
        is_moving = True
        move_thread = threading.Thread(target=move_carousel,args=(30,))
        move_thread.start()

    paths = sorted(Path("/home/pi/fish_feeder/videos/").iterdir(), key=os.path.getmtime, reverse=True)
    toReturn = []
    testI = 0
    for path in paths:
        testI = testI + 1
        ts = re.findall('[0-9][0-9]+',path.name)[0]
        file_type = re.findall('[a-z][a-z][a-z]+',path.name)[0]
        dt = datetime.fromtimestamp(int(ts));
        toReturn.append([path.name,str(dt) + " " + file_type])
    return render_template('page.html',vid_list=toReturn)

@app.route('/load')
def load():
    global cur_station, cur_step, is_moving
    if (not is_moving):
        cur_station = cur_station + 1
        steps_needed = int(cur_station*(STEPS_PER_REV/STATIONS_PER_REV)-cur_step)
        cur_step = cur_step+steps_needed
        is_moving = True
        move_thread = threading.Thread(target=move_carousel,args=(steps_needed,False))
        move_thread.start()
        return render_template('load.html') 

@app.route('/record')
def record():
    global is_moving
    if(not is_moving):
        is_moving = True;
        record_thread = threading.Thread(target=record_video,args=(60.,))
        record_thread.start()
        return "RECORDING."
    return "RECORDING ALREADY STARTED."

@app.route('/feed')
def test():
    global cur_station, cur_step, is_moving
    if (not is_moving):
        cur_station = cur_station + 1
        steps_needed = int(cur_station*(STEPS_PER_REV/STATIONS_PER_REV)-cur_step)
        cur_step = cur_step+steps_needed
        is_moving = True
        move_thread = threading.Thread(target=move_carousel,args=(steps_needed,))
        move_thread.start()
        return 'test: ' + str(steps_needed)
    else:
        return "ALREADY FEEDING!"

@app.route('/download/<filename>')
def download(filename):
    path = '/home/pi/fish_feeder/videos/'
    return send_from_directory(path,filename);

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
