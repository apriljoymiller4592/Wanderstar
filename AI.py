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
#import Slides
import bulb
import Shelly as shelly
from Music import MusicPlayer
import threading
import httparduinoclient as arduino
print(tf.__version__)

class_to_label = "Not_Loaded_Yet"
model = tf.keras.models.load_model('model/model18best.h5')
#model = tf.saved_model.load('model/model6')

shelly_ip1 = "192.168.1.116"
shelly_ip2 = "192.168.1.117"

#music, stop_event = Music.music_player(False)

#stop_music_event = threading.Event()
#music_thread = threading.Thread(target=music.listen(stop_music_event), args=(stop_music_event,))

#music.listen(stop_event)

#music.play_song(stop_music_event)



'''infer = model.signatures['serving_default']

converter = tf.lite.TFLiteConverter.from_saved_model('model/model8')
#converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)


interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_tensor = tf.random.normal([1, 224, 224, 3], dtype=tf.float32)
output = infer(input_tensor)
'''
def feed(inputPath):
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
            bulb.switch("turn", "on")
        elif predicted_label == 'Squiggle':
            PRESENTATION_ID = "1CricEs7HjbHiU-u3Tjz1jwQGpd2yq_AN61BhtI3YG24"
            #viewer = Slides.GoogleSlidesViewer(PRESENTATION_ID)
        elif predicted_label == 'Triangle':
            bulb.switch("turn", "off")
        elif predicted_label == 'Right Arrow':
            shelly.turn_on_or_off(shelly_ip1, "on")
        elif predicted_label == 'Left Arrow':
            shelly.turn_on_or_off(shelly_ip1, "off")
        elif predicted_label == 'U':
            shelly.turn_on_or_off(shelly_ip2, "on")
        elif predicted_label == 'Upside Down U':
            shelly.turn_on_or_off(shelly_ip2, "off")
        elif predicted_label == 'Star':
            player = MusicPlayer()
            time.sleep(1)
            player.play_pause()
        elif predicted_label == 'Circle':
            print("Open box")
            arduino.moveActuator()
        elif predicted_label == 'Z':
            PRESENTATION_ID = "1CricEs7HjbHiU-u3Tjz1jwQGpd2yq_AN61BhtI3YG24"
            #viewer = Slides.GoogleSlidesViewer(PRESENTATION_ID).next()
