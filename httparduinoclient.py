import requests

arduino_ip = '10.42.0.117'

url = f'http://{arduino_ip}/'

try:
    # Send the HTTP GET request
    response = requests.get(url)

    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Error: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
