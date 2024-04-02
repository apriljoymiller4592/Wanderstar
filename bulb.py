import colour as c
import time

# MAC_ADDRESS: 9C:3F:60:74:F4:C5:9F:4E
# MODEL:: H6009
from pygovee import Govee
from pygovee.Govee import GoveeClient

delay = 2
delayb = 10

mac = "9C:3F:60:74:F4:C5:9F:4E"
model = "H6009"
# String = "WandLight: MAC_ADDRESS: 9C:3F:60:74:F4:C5:9F:4E, MODEL:: H6009"
client: GoveeClient = Govee.GoveeClient(apiKey="306802d6-b755-4826-b6b1-c28b94bbc317")
client.login()
client.get_device_list()

time.sleep(5)

client.device_off(mac, model)
print("off")
time.sleep(delay)

client.device_on(mac, model)
print("device on")
time.sleep(delay)

def changeLight():
    print("Changing Light")
    #client.change_device_color(mac, model, r=15, g=45, b=87)
    #time.sleep(delay)
