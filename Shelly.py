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
    
def get_shelly_status(ip):
    url = f"http://{ip}/rpc/status"
    try:
        response = requests.get(url)
        response.raise_for_status()
        ptint(response.json())  
        return response.json()   
    except requests.RequestException as e:
        print(f"Error fetching device status: {e}")
        return None
