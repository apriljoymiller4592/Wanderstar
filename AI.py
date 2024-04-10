import cv2
import os
import requests
import time
import keras
import numpy as np
import json
import csv
import sys
# import tensorflow
from keras.models import load_model
from keras.applications.mobilenet_v2 import preprocess_input
from keras.preprocessing import image
import tensorflow as tf
import Slides
import bulb

class_to_label = "Not_Loaded_Yet"
model = tf.keras.models.load_model('model/trythis.h5')

print(tf.__version__)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def feed(inputPath):

    img = image.load_img(inputPath, target_size=(224, 224), color_mode='rgb')  # Adjust size and color mode
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Create a batch
    img_array /= 255.0  # Normalize

    # Make a prediction
    predictions_main = model.predict(img_array)

    class_index = np.argmax(predictions_main, axis=1)
    with open('model/labels.json') as f:
        class_to_label = json.load(f)
    predicted_label = class_to_label[str(class_index[0])]

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])

    if np.max(predictions) < 0.9:
        #print("Poopy prediction")
        pass
    else:
        print(f"Feeding AI:  {inputPath}")
        print("This is the time to make a prediction.")
        print(f"Predicted class: {predicted_label}, Confidence: {np.max(predictions_main)}")

        if predicted_label == 'Z':
            bulb.switch("turn", "on")
        elif predicted_label == 'Circle':
            bulb.change_color("color", 255, 0, 0)
        elif predicted_label == 'Triangle':
            bulb.change_color("color", 0, 255, 0)





