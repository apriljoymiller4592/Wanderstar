import time
import requests

def turn_on_or_off(ip, value):
    url = f"http://{ip}/relay/0?turn={value}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Device turned on/off successfully.")
    else:
        print("Failed to turn on the device.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return response
