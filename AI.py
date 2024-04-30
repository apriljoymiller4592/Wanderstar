
import cv2
import os
import requests
import time
import keras
import numpy as np
import json
import csv
import sys
from keras.models import load_model
from keras.applications.mobilenet_v2 import preprocess_input
from keras.preprocessing import image
import tensorflow as tf

import Music
import Slides
import bulb
import Shelly as shelly 
import Slides as slides
import threading
import httparduinoclient as arduino 

import webbrowser
from datetime import datetime
import time

class_to_label = "Not_Loaded_Yet"
model = tf.keras.models.load_model('model/model18best.h5')
 
shelly_ip1 = "10.42.0.233"
shelly_ip2 = "10.42.0.144"
light_on = False
shelly_on1 = False
shelly_on2 = False

def feed(inputPath,bulb):
    global light_on
    global shelly_on1
    global shelly_on2
    
    img = image.load_img(inputPath, target_size=(224, 224), color_mode='grayscale')  # Adjust size and color mode
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Create a batch
    img_array = img_array.astype('float32') / 255.0

    # Make a prediction
    predictions_main = model.predict(img_array)

    class_index = np.argmax(predictions_main, axis=1)

    with open('model/labels.json') as f:
        class_to_label = json.load(f)
    predicted_label = class_to_label[str(class_index[0])]

    if (np.max(predictions_main) < 0.9 or predicted_label == "Junk"
            or predicted_label == ''):
        pass
    else:
        print(f"Feeding AI:  {inputPath}")
        print("This is the time to make a prediction.")
        print(f"Predicted class: {predicted_label}, Confidence: {np.max(predictions_main)}")
        

        if predicted_label == 'Square':
            bulb.switch()
        elif predicted_label == "Right Arrow":
            bulb.brighten()
        elif predicted_label == "Left Arrow":
            bulb.dim()
        elif predicted_label == "Z":
            bulb.change_color()
        elif predicted_label == 'Squiggle':
            #slides.show_slides()
            print("hi")
        elif predicted_label == "Triangle":
            shelly.turn_on_or_off(shelly_ip1, "on")
            if shelly_on1 == False:
              shelly.turn_on_or_off(shelly_ip1, "on")
              shelly_on1 = True
            else:
              shelly.turn_on_or_off(shelly_ip1, "off")
              shelly_on = False    
        elif predicted_label == "U":
            shelly.turn_on_or_off(shelly_ip2, "on")
            if shelly_on2 == False:
              shelly.turn_on_or_off(shelly_ip2, "on")
              shelly_on2 = True
            else:
              shelly.turn_on_or_off(shelly_ip2, "off")
              shelly_on = False  
        elif predicted_label == 'Star':
             url = "https://youtu.be/dQw4w9WgXcQ?si=7Ygd8pnqiUF1tA2a"
             webbrowser.open(url)
             time.sleep(30)
        elif predicted_label == 'Circle':
            print("Open box")
            arduino.moveActuator()
        elif predicted_label == 'Z':
            #slides.next_slide()
            print("hi")
