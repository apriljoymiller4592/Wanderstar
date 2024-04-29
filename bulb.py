import json
import time
import webcolors

import requests
import os  # Import os module for file operations

class goveeLight:

    def __init__(self, api_key= 'a7155454-e929-40d6-9397-46ba6115a47e', device_id ='a7155454-e929-40d6-9397-46ba6115a47e'):
        self.colors = ['red','green','blue','purple','turquoise','orange','pink','white']
        self.colorsSize = len(self.colors)
        self.colorsIndex = 0

        self.base_url = 'https://developer-api.govee.com/v1/devices/control'
        print(api_key)
        self.headers = {
            'Govee-API-Key': api_key,
            'Content-Type': 'application/json',
        }
        self.api_key = api_key
        if os.path.isfile('device_mac'):  # Check if file exists
            with open('device_mac', 'r') as f:
                mac = f.read()
            if mac != '':  # Only assign device_id if file is not empty
                self.device_id = mac
                if os.path.isfile('device_model'):  # Check if file exists
                    with open('device_model', 'r') as f:
                        model = f.read()
                    self.device_model = model
        else:
            self.device_id, self.device_model = self.get_devices()
        url = f"https://developer-api.govee.com/v1/devices/state?device={self.device_id}&model={self.device_model}"
        properties = json.loads(requests.request("GET", url, headers=self.headers, data={}).text)['data']['properties']
        for prop in properties:
            if 'powerState' in prop:
                self.powerState = prop['powerState']
            elif 'brightness' in prop:
                self.brightness = prop['brightness']




    def get_devices(self):
        print("getting devices")
        url = "https://developer-api.govee.com/v1/devices"

        payload = "{\"query\":\"\",\"variables\":{}}"
        headers = {
            'Content-Type': 'application/json',
            'Govee-API-Key': self.api_key,
        }
        #get devices
        response = requests.request(
            "GET", url, headers=self.headers, data=payload).text
        print(response)
        devices = json.loads(response)['data']['devices']
        # Extract device ID and model for each device
        device_info = [(device['device'], device['model']) for device in devices]
        with open('device_mac','w') as f:
            f.write(device_info[0][0])  # Corrected
        with open('device_model','w') as f:
            f.write(device_info[0][1])  # Corrected

        return device_info[0][0], device_info[0][1]  # Corrected

    def switch(self):
        if self.powerState == 'on':
            value = 'off'
        else:
            value = 'on'
        body = {
            'device': self.device_id,
            'model': self.device_model,
            'cmd': {
                'name': 'turn',
                'value': value
            }
        }
        response = requests.put(self.base_url, headers=self.headers, json=body)
        print(response.text)
        self.powerState = value

    def change_color(self):
        r = webcolors.name_to_rgb(self.colors[self.colorsIndex])[0]
        g = webcolors.name_to_rgb(self.colors[self.colorsIndex])[1]
        b = webcolors.name_to_rgb(self.colors[self.colorsIndex])[2]
        self.colorsIndex += 1
        self.colorsIndex %= self.colorsSize
        body = {
            'device': self.device_id,
            'model': self.device_model,
            'cmd': {
                'name': 'color',
                'value': {
                    'r': r,
                    'g': g,
                    'b': b
                }
            }
        }
        response = requests.put(self.base_url, headers=self.headers, json=body)
        print(response.text)


    def brighten(self):
        if(self.brightness + 25 < 100):
            self.brightness += 25
        else:
            self.brightness += (100 - self.brightness)
        body = {
            'device': self.device_id,
            'model': self.device_model,
            'cmd': {
                'name': 'brightness',
                'value': self.brightness
            }
        }
        response = requests.put(self.base_url, headers=self.headers, json=body)
        print(response.text)

    def dim(self):
        if(self.brightness - 25 > 0):
            self.brightness -= 25
        else:
            self.brightness = 0
        body = {
            'device': self.device_id,
            'model': self.device_model,
            'cmd': {
                'name': 'brightness',
                'value': self.brightness
            }
        }
        response = requests.put(self.base_url, headers=self.headers, json=body)
        print(response.text)

    def to_string(self):
        return (f"Api key: {self.api_key}\nDevice Id: {self.device_id}\nDevice Model: {self.device_model}"
                f"\nDevice Powerstate: {self.powerState}\nDevice Brightness: {self.brightness}")


if __name__ == '__main__':
    api_key = '511eab0d-6846-4562-988c-5956ceb6a63a'
    lightbulb = goveeLight(api_key)
    lightbulb.dim()
    time.sleep(5)
    lightbulb.dim()
    time.sleep(5)
    lightbulb.brighten()
    time.sleep(5)
    lightbulb.brighten()
    time.sleep(5)
    for i in range(lightbulb.colorsSize * 2):
        lightbulb.change_color()
        time.sleep(5)


