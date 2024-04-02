import requests
import time

api_key = '306802d6-b755-4826-b6b1-c28b94bbc317'
device_id = '9C:3F:60:74:F4:C5:9F:4E'
base_url = 'https://developer-api.govee.com/v1/devices/control'

headers = {
    'Govee-API-Key': api_key,
    'Content-Type': 'application/json',
}

def switch(name, value):
    body = {
        'device': device_id,
        'model': 'H6009',
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
        'model': 'H6009',
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


switch("turn", "off")