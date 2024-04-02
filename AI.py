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

#import bulb
class_to_label = "Not_Loaded_Yet"
model = tf.keras.models.load_model('model/model.h5')
with open('model/labels.json') as f:
    class_to_label = json.load(f)

def feed(inputPath):
    print(f"Feeding AI:  {inputPath}")
    print("This is the time to make a prediction.")

    img = image.load_img(inputPath, target_size=(64, 64), color_mode='grayscale')  # Adjust size and color mode
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Create a batch
    img_array /= 255.0  # Normalize

    # Make a prediction
    predictions = model.predict(img_array)
    print(predictions)
    predicted_class = np.argmax(predictions, axis=1)
    print(predicted_class)
    predicted_label = class_to_label[str(predicted_class[0])]
    print(predicted_label)



    #bulb.changeLight()
    # #class_names = load_class_names_from_json('class_names.json')
    # print('will make a guess of ' + inputPath)

    # predictions = model.predict(preprocess_image(inputPath))
    # print(f"predictions: {predictions}")
    # class_names = load_class_names_from_json('names.json')

    # predicted_class = interpret_predictions(predictions, class_names)
    # print(f"Predicted class: {predicted_class}")

    # print(class_names)
    # print(predicted_class)

def load_class_names_from_json(file_path):
    with open(file_path, 'r') as file:
        class_ids = json.load(file)
    inverted_class_ids = {v: k for k, v in class_ids.items()}
    return inverted_class_ids


def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded_dims)


def interpret_predictions(predictions, class_names):
    class_idx = np.argmax(predictions[0])
    return class_names[class_idx]







