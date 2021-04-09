"""
timing_receive_images.py -- receive and display images, then print FPS stats

A timing program that uses imagezmq to receive and display an image stream
from one or many devices and print timing and FPS statistics.

1. Run this program in its own terminal window on the receiver:
python receive_images.py

2. Run the image sending program on the sender:
python send_images.py

A cv2.imshow() window will appear on the Mac showing the tramsmitted images
as a video stream.

To end the programs, press Ctrl-C in the terminal window of the receiving
program first, so that FPS and timing statistics will be accurate. Then, press
Ctrl-C in each terminal window running a Rasperry Pi image sending program.
"""

import sys

import time
import traceback
from cv2 import cv2
from collections import defaultdict
import imagezmq
from datetime import datetime

# Font for text on video 
font = cv2.FONT_HERSHEY_SIMPLEX

# IP Address Receiver
if len(sys.argv) == 2 : # If there is no ip address input
    ipAddress = 'tcp://*:6666'
    print ("Receiving on = " + ipAddress)
elif len(sys.argv) == 3 : # If there is ip address input
    ipAddress = 'tcp://'+sys.argv[2]+':6666'
    print ("Receiving on = " + ipAddress)
else :
    print ("Error on ip address input")
    sys.exit()

# instantiate image_hub
# Specify the type messaging and receiver ip address
# 1 for REQ/REP messaging
# 2 for PUB/SUB messaging
image_hub = imagezmq.ImageHub()
if (int(sys.argv[1])) == 1 :
    image_hub = imagezmq.ImageHub(open_port=ipAddress)
elif (int(sys.argv[1])) == 2 :
    image_hub = imagezmq.ImageHub(open_port=ipAddress, REQ_REP=False)


image_count = 0 # All images received counts
sender_image_counts = defaultdict(int)  # Image counts per sender
sender_image__start_time = defaultdict(datetime)
sender_image__start_stop = defaultdict(datetime)
first_image = True # Flag for first image received

try:
    while True:  # receive images until Ctrl-C is pressed
	    # Receives Image
        msg_received, image = image_hub.recv_image() 

	    # Get receives time
        received_time_datetime = datetime.now() 

        # Change sent time to datetime & receive time to string
        sent_time_datetime = datetime.strptime(msg_received[1], "%d/%m/%y %H:%M:%S.%f") 
        received_time_str = received_time_datetime.strftime("%d/%m/%y %H:%M:%S.%f")

	    # Difference beetween sent & receives
        delta_datetime = (received_time_datetime - sent_time_datetime).total_seconds()

	    # Put text on images for testing
        cv2.putText(image, "Sent :" + msg_received[1],(5,200), font, 1,(255,0,0),2)
        cv2.putText(image, "Received :" + received_time_str,(5,250), font, 1,(255,0,255),2)
        cv2.putText(image, 'Delta Time =' + str(delta_datetime),(5,300), font, 1,(0,0,255),2)
        
        if sender_image_counts[msg_received[0]] == 0:
            sender_image__start_time[msg_received[0]] = datetime.now()
            first_image = False
        image_count += 1  # global count of all images received
        sender_image_counts[msg_received[0]] += 1  # count images for each RPi name
        cv2.putText(image, 'Image Number =' + str(sender_image_counts[msg_received[0]]),(5,350), font, 1,(0,255,255),2)
        
	    # Calculate FPS while test is running
        time_elasped = (datetime.now() - sender_image__start_time[msg_received[0]]).total_seconds()
        fps_running = sender_image_counts[msg_received[0]] / time_elasped
        cv2.putText(image, 'Time Elasped =' + str(time_elasped),(5,400), font, 1,(255,255,0),2)
        cv2.putText(image, 'Approx FPS =' + str(fps_running),(5,450), font, 1,(0,255,0),2)

        cv2.imshow(msg_received[0], image)  # display images 1 window
        cv2.waitKey(1)
        # other image processing code, such as saving the image, would go here.
        # often the text in "sent_from" will have additional information about
        # the image that will be used in processing the image.

        # Reply the sender mesage
        if (int(sys.argv[1])) == 1 :
            image_hub.send_reply(b"OK")  # REP reply
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program; FPS stats computed below
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    # stop the timer and display FPS information
    print()
    print('Test Program: ', __file__)
    print('Total Number of Images received: {:,g}'.format(image_count))
    if first_image:  # never got images from any sender
        sys.exit()
    print('Number of Images received from each sender:')
    for sender in sender_image_counts:
        print('    ', sender, ': {:,g}'.format(sender_image_counts[sender]))
    image_size = image.shape
    print('Size of last image received: ', image_size)
    uncompressed_size = image_size[0] * image_size[1] * image_size[2]
    print('    = {:,g} bytes'.format(uncompressed_size))
    print('Elasped time: {:,.2f} seconds'.format(time_elasped))
    print('Approximate FPS: {:.2f}'.format(fps_running))
    cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
    image_hub.close()  # closes ZMQ socket and context
    sys.exit()
