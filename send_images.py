"""
timing_send_images.py -- send image stream.

A test program that uses imagezmq to send image frames from the
client continuously to a receiving program on another device that will display the
images as a video stream.

"""

import sys

import socket
import time
import traceback
from imutils.video import VideoStream
import imagezmq
from cv2 import cv2
from datetime import datetime

# Font for Text on video
font = cv2.FONT_HERSHEY_SIMPLEX

# IP address receiver
if len(sys.argv) == 2 : # If there is no ip address input
    ipAddress = 'tcp://*:6666'
    print ("Sending to = " + ipAddress)
elif len(sys.argv) == 3 : # If there is ip address input
    ipAddress = 'tcp://'+sys.argv[2]+':6666'
    print ("Sending to = " + ipAddress)
else :
    print ("Error on ip address input")
    sys.exit()

# Specify the type messaging and receiver ip address
# 1 for REQ/REP messaging
# 2 for PUB/SUB messaging
if (int(sys.argv[1])) == 1 :
    sender = imagezmq.ImageSender(connect_to=ipAddress)
elif (int(sys.argv[1])) == 2 :
    sender = imagezmq.ImageSender(connect_to='tcp://*:6666', REQ_REP=False)

# send sender hostname with each image
sender_name = socket.gethostname()  

# Opening webcam, you could change to a local video if you want
cap = cv2.VideoCapture('test_video.mp4')
time.sleep(2.0)  # allow camera some time before sending

try:
    while True:  # send images as stream until Ctrl-C
        ret, image = cap.read()
        
        # Put processing of image before sending if you want below here
        # for example, rotation, ROI selection, conversion to grayscale, etc.

        # now = datetime.now() # Get timestamp of when the image is sent
        # current_time = now.strftime("%d/%m/%y %H:%M:%S.%f") # Change datetime to string

        msg = [sender_name, datetime.now().strftime("%d/%m/%y %H:%M:%S.%f")]  # Put sender name and timestamp on one message

        # Send images and timestamp and save the reply from receiver if you are using REQ/REP
        if (int(sys.argv[1])) == 1 :
            reply_from_receiver = sender.send_image(msg, image)  # Send image, sender name, and timestamp at the sametime
        elif (int(sys.argv[1])) == 2 :
            sender.send_image(msg, image)  # Send image, sender name, and timestamp at the sametime
	    
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    cap.release()  # stop the camera thread
    sender.close()  # close the ZMQ socket and context
    sys.exit()
