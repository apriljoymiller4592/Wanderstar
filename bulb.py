import requests
import time

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


switch("turn", "on")