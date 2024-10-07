#!//usr/bin/python3
'''
PiCamera controlled by a motion detector module and a pair of switches to
record video clips and still images.

The motion detector used produces a high signal when motion is detected. the
two switches are connected to ground, so when pressed, they will pull a pin
low. The GPIO pins used for the switches need to have pull-ups enabled.

The board being used is a section of a µKOB IF MkIV with the switches and 1/8"
audio jack. The switches connect to GPIO21 and GPIO20. The motion detector
plugs into the 1/8" jack, which is connected to GPIO16.

SPDX-Copyright-String: Copyright 2024 AESilky (SilkyDESIGN)
SPDX-License-Identifier: MIT License

'''
from gpiozero import Button, MotionSensor
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from datetime import datetime
import time
import sys

_exit = False
_filming = False

btn_still = Button(21)
btn_video = Button(20)
sns_motion = MotionSensor(16)
scam = Picamera2()
vcam = Picamera2()

config = scam.create_still_configuration()
scam.configure(config)
vid_config = vcam.create_video_configuration()
vcam.configure(vid_config)
encoder = H264Encoder(10000000)

scam.start()

def create_timestamp():
    dt = datetime.fromtimestamp(time.time())
    date_time_str = str("{:04}{:02}{:02}-{:02}{:02}{:02}").format(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
    )
    return date_time_str

def start_video():
    global _filming
    if not _filming:
        _filming = True
        print("Action...")
        vid_name = "mcv-{}.mp4".format(create_timestamp())
        output_path = "~/Videos/{}".format(vid_name)
        output = FfmpegOutput(output_path)
        vcam.start_recording(encoder, output)
        time.sleep(5)
        vcam.stop_recording()
    return

def stop_video():
    global _filming
    if _filming:
        _filming = False
        print("Cut!")
    return

def take_still():
    print("Click")
    pic_name = "mcp-{}.jpg".format(create_timestamp())
    scam.capture_file("~/Pictures/{}".format(pic_name))
    return

def on_hold_still():
    global _exit
    _exit = True
    return

def on_press_video():
    start_video()
    return

def on_release_video():
    stop_video()
    return

def on_motion():
    start_video()
    return

def on_motion_end():
    global _filming
    if _filming:
        time.sleep(1.0)
        stop_video()
    return

btn_still.when_pressed = take_still
btn_video.when_pressed = on_press_video
btn_video.when_released = on_release_video
sns_motion.when_motion = on_motion
sns_motion.when_no_motion = on_motion_end

btn_still.hold_time = 3.0
btn_still.when_held = on_hold_still

# Main
print("Smile :-)")
while True:
    try:
        if _exit:
            print("Shutter-Release Held - Time to exit.")
            break
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("Okay, I'll quit now.")
        break

scam.stop()
sys.exit(0)
