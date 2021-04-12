# imagezmq_stream

## Requirements
Python
Python
PyZMQ 
Numpy 
OpenCV
imutils

pip3 install imagezmq
pip3 install opencv-contrib-python
pip3 install numpy
pip3 install imutils

## How to Run
1. 1 is for REQ/REP messaging
2. 2 is fot PUB/SUB messaging

### Receive image
python3 receive_images.py 1/2 ipaddress

### Send Image
python3 receive_images.py 1/2 ipaddress

### Example 
python3 receive_images.py 1 10.10.4.2

python3 send_images.py 1 10.10.4.2
