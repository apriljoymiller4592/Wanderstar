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
#import Slides
import bulb

print(tf.__version__)

class_to_label = "Not_Loaded_Yet"
#model = tf.keras.models.load_model('model/model6')
model = tf.saved_model.load('model/model6')

infer = model.signatures['serving_default']

converter = tf.lite.TFLiteConverter.from_saved_model('model/model6')
#converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)


interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_tensor = tf.random.normal([1, 224, 224, 3], dtype=tf.float32)
output = infer(input_tensor)

def feed(inputPath):
    img = image.load_img(inputPath, target_size=(224, 224), color_mode='rgb')  # Adjust size and color mode
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Create a batch
    img_array = img_array.astype('float32') / 255.0

    # Make a prediction
#    predictions_main = model.predict(img_array)

    # Flag to signify valid or invalid gesture
    poopy_prediction = False
    '''
    #input_details = interpreter.get_input_details()
    #output_details = interpreter.get_output_details()

    input_tensor = tf.convert_to_tensor(img_array)
    output = infer(input_tensor)

    interpreter.set_tensor(input_tensor[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output[0]['index'])
'''
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Set the tensor to point to the input data to be inferred
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()

    # Get the prediction results
    predictions = interpreter.get_tensor(output_details[0]['index'])
    class_index = np.argmax(predictions, axis=1)

    with open('model/labels.json') as f:
        class_to_label = json.load(f)
    predicted_label = class_to_label[str(class_index[0])]

    if np.max(predictions) < 0.95:
        print("Poopy prediction")
        poopy_prediction = True
        pass
    else:
        print(f"Feeding AI:  {inputPath}")
        print("This is the time to make a prediction.")
        print(f"Predicted class: {predicted_label}, Confidence: {np.max(predictions)}")

        if predicted_label == 'Z':
            bulb.switch("turn", "on")
            bulb.change_color("color", 0, 255, 0)
        elif predicted_label == 'Circle':
            PRESENTATION_ID = "1CricEs7HjbHiU-u3Tjz1jwQGpd2yq_AN61BhtI3YG24"
            viewer = Slides.GoogleSlidesViewer(PRESENTATION_ID)
        elif predicted_label == 'Triangle':
            bulb.change_color("color", 0, 0, 255)
        elif predicted_label == "Junk" or poopy_prediction:
            bulb.change_color("color", 255, 0, 0)


