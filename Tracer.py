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

input_filename = 'symbols_training/symbols.csv'
api_key = 'a7155454-e929-40d6-9397-46ba6115a47e'
device_id = '52:88:60:74:F4:97:F4:7A'
base_url = 'https://developer-api.govee.com/v1/devices/control'

headers = {
    'Govee-API-Key': api_key,
    'Content-Type': 'application/json',
}

def switch(name, value):
    body = {
        'device': device_id,
        'model': 'H6008',
        'cmd': {
            'name': name,
            'value': value
        }
    }
    response = requests.put(base_url, headers=headers, json=body)
    print(response.text)

def change_color(name, r, g, b):
    body = {
        'device': device_id,
        'model': 'H6008',
        'cmd': {
            'name': name,
            'value': {
                'r': r,
                'g': g,
                'b': b
            }
        }
    }
    response = requests.put(base_url, headers=headers, json=body)
    print(response.text)

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

model = load_model('best.h5')

class_names = load_class_names_from_json('class_names.json')

folder_path = 'pics/traces'
for filename in os.listdir(folder_path):
    # print(filename)
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

folder_path = 'pics/real'
for filename in os.listdir(folder_path):
    # print(filename)
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

folder_path = 'pics/processed'
for filename in os.listdir(folder_path):
    # print(filename)
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path) and filename.lower().endswith(('.png')):
        os.remove(file_path)

params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 10
params.maxThreshold = 200
params.filterByArea = True
params.minArea = 500
params.filterByCircularity = True
params.minCircularity = 0.01
params.filterByConvexity = True
params.minConvexity = 0.1
params.filterByInertia = True
params.minInertiaRatio = 0.01
params.filterByColor = True
params.blobColor = 255

detector = cv2.SimpleBlobDetector_create(params)

cap = cv2.VideoCapture(0)

blob_path = []
trace_image = None
imageCount = 0

alpha = 0.4
beta = -50
delta = 0
idleCount = 0
threshold = 50
deltas = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if trace_image is None or trace_image.size == 0:
        trace_image = np.zeros_like(frame)

    frame_flipped = cv2.flip(frame, 1)

    gray_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2GRAY)

    if cv2.waitKey(2) & 0xFF == ord('c'):
        alpha -= 0.1
        print('c')
        print(alpha)
    if cv2.waitKey(2) & 0xFF == ord('d'):
        alpha += 0.1
        print('d')
        print(alpha)
    if cv2.waitKey(2) & 0xFF == ord('g'):
        beta += 10
        print('g')
        print(beta)
    if cv2.waitKey(2) & 0xFF == ord('b'):
        beta -= 10
        print('b')
        print(beta)
    if cv2.waitKey(2) & 0xFF == ord('t'):
        threshold += 10
        print('t')
        print(threshold)
    if cv2.waitKey(2) & 0xFF == ord('y'):
        threshold -= 10
        print('y')
        print(threshold)
    gray_frame = cv2.convertScaleAbs(gray_frame, alpha=alpha, beta=beta)
    ret, gray_frame = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)  # 127 is highest threshhold
    keypoints = detector.detect(gray_frame)
    points = cv2.KeyPoint_convert(keypoints)


    def calculate_euclidean_distance(point1, point2):
        return np.linalg.norm(np.array(point1) - np.array(point2))


    movement_threshold = 2

    if len(points) > 0:
        current_point = points[0]
        #print(f"Processing point: {current_point}")

        if not blob_path or calculate_euclidean_distance(current_point, blob_path[-1]) > movement_threshold:
            blob_path.append(current_point)
            #print(f"Point added to path: {current_point}")

        if len(blob_path) > 1:
            for i in range(1, len(blob_path)):
                cv2.line(frame_flipped, tuple(np.intp(blob_path[i - 1])), tuple(np.intp(blob_path[i])), (0, 0, 0), 25)
                cv2.line(trace_image, tuple(np.intp(blob_path[i - 1])), tuple(np.intp(blob_path[i])), (0, 0, 0), 25)
                cv2.line(gray_frame, tuple(np.intp(blob_path[i - 1])), tuple(np.intp(blob_path[i])), (255, 255, 255),
                         25)

        cv2.imshow('Frame with Tracing', frame_flipped)
        cv2.imshow('Trace Image', trace_image)
        cv2.imshow('Gray Frame with Tracing', gray_frame)
    else:
       # print('hi')
        if len(blob_path) > 1:
            print('TRACED')
            imageCount += 1
            filename = f'pics/real/{imageCount}_frame_image.png'
            cv2.imwrite(f'pics/real/{imageCount}_frame_image.png', frame_flipped)
            cv2.imwrite(f'pics/processed/{imageCount}_grey_image.png', gray_frame)

            preprocessed_img = preprocess_image(filename)

            predictions = model.predict(preprocessed_img)

            class_names = load_class_names_from_json('names.json')
            predicted_class = interpret_predictions(predictions, class_names)
            print(f"Predicted class: {predicted_class}")

            if predicted_class == 'L':
                switch("turn", "on")
            elif predicted_class == 'A':
                change_color("color", 255, 0, 0)
            elif predicted_class == 'B':
                change_color("color", 0, 0, 255)
            elif predicted_class == 'C':
                change_color("color", 0, 255, 0)
            elif predicted_class == 'J':
                change_color("color", 138, 43, 226)
            elif predicted_class == 'H':
                switch("turn", "off")

            trace_image = np.zeros_like(frame_flipped)
            for i in range(1, len(blob_path)):
                cv2.line(trace_image, tuple(np.intp(blob_path[i-1])), tuple(np.intp(blob_path[i])), (0, 0, 0), 15)
            cv2.imwrite(f'pics/traces/{imageCount}_trace_image.png', trace_image)
        trace_image = None
        blob_path = []
        idleCount = 0

    im_with_keypoints = cv2.drawKeypoints(frame_flipped, keypoints, np.array([]), (0, 0, 0),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    gray_frame = cv2.drawKeypoints(gray_frame, keypoints, np.array([]), (0, 0, 0),
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Keypoints", im_with_keypoints)
    cv2.imshow("Proccesed", gray_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        for point in points:
            print(point)
        break

cap.release()
cv2.destroyAllWindows()
