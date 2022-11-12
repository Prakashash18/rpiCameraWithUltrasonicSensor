from modelarts.session import Session
from modelarts.model import Predictor
import cv2 as cv

import RPi.GPIO as GPIO 
import time
import os

import threading

from threading import Thread
from datetime import datetime
from collections import deque

import pyttsx3

engine = pyttsx3.init()
engine.say("Hello There, I am CAS System")
engine.runAndWait()


GPIO.setmode(GPIO.BCM)

TRIG=23
ECHO=24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False) 

# parameters required for Huawei ModelArts SDK

access_key="YOUR_ACCESS_KEY_HERE"
secret_key="YOUR_SECRET_KEY_HERE"
project_id="YOUR_PROJECT_ID_HERE"
region_name="YOUR_REGION_NAME_HERE"
service_id="YOUR_SERVICE_ID_HERE"

session = Session(access_key=access_key, secret_key=secret_key, project_id=project_id, region_name=region_name)

#inference time !!!!

predictor_instance = Predictor(session, service_id=service_id)


#global lock
#to protect frame read and write among threads
lock = threading.Lock()

def thread_function(name):
	engine.say(name)
	engine.runAndWait()



class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = datetime.now()
        return self

    def increment(self):
        self._num_occurrences += 1

    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        return self._num_occurrences / elapsed_time if elapsed_time > 0 else 0

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True

class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            with lock:
                cv.imwrite('test.png', self.frame)
                cv.imshow("CAS System", self.frame)
            # predict_result = predictor_instance.predict(data="test.png", data_type="images")
            # print(predict_result)
            if cv.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True


video_getter = VideoGet().start()
time.sleep(1)
video_shower = VideoShow(video_getter.frame).start()
cps = CountsPerSec().start()

while(True):

	if video_getter.stopped or video_shower.stopped:
		video_shower.stop()
		video_getter.stop()
		break

	GPIO.output(TRIG, True)
	time.sleep(0.00001) #10 microsecond delay
	GPIO.output(TRIG, False)

	#read wave
	while GPIO.input(ECHO)==0:
	        pulse_start = time.time()

	while GPIO.input(ECHO)==1:
	        pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start

	distance = 34300 * pulse_duration/2

	distance = round(distance,2)

	print("Distance: ",distance, "cm")

	frame = video_getter.frame
	# frame = putIterationsPerSec(frame, cps.countsPerSec())
	video_shower.frame = frame
	cps.increment()

	if distance < 200:
		x = threading.Thread(target=thread_function, args=("Object Detected. Processing !",))
		x.start()
		print("Put into queue")
		print("Detect frame in another thread")
		with lock:
			predict_result = predictor_instance.predict(data="test.png", data_type="images")
			print(predict_result)
			scores = predict_result['detection_scores']
			classes = predict_result['detection_classes']

		for score in scores:
			if float(score) > 0.7:
				x = threading.Thread(target=thread_function, args=("Fast Moving Object Approaching",))
				x.start()
			else:
				x = threading.Thread(target=thread_function, args=("It's safe",))
				x.start()

		x = threading.Thread(target=thread_function, args=("It's safe",))
		x.start()
