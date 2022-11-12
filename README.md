## About this Project

This code is tested on a Raspberry Pi 4. It uses an ultrasonic sensor to detect if someone is nearby, takes a photo using the webcam attached and uploads the image to Huawei's ModelArts server using their SDK. 

The model is an ExeML Object Detection Model and will return the prediction results.

The model was trained to detect fast moving objects like PMD's and Bicycles. Thus the speaker will provide a feedback to the user.

<hr>

## Hardware

* RPi 4 Kit
* Webcam or RPi Camera
* HCSR04 Ultrasonic Sensor
* Speakers

## Software
* Huawei ModelArts SDK and service ID of a trained model deployed using real-time services.

<hr>

## Steps to setup

