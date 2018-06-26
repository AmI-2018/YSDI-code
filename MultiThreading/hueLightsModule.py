"""
Created on Apr 4, 2014
Updated on May 16, 2018
@author: Dario Bonino
@author: Luigi De Russis
Copyright (c) 2014-2018 Dario Bonino and Luigi De Russis

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License

- - - -
Modified version for AmI-2018 project called YSDI.
"""

import rest
import time

#base_url = 'http://localhost:8080'
base_url = 'http://192.168.0.201'
#username = 'newdeveloper'
username = "fFSt4atQ1zIcis0aAudg4ULMYx9AUiB9VYyDSLfO"
lights_url = base_url + '/api/' + username + '/lights/'
VAL = "1"
ON = False
STATE = 0  # 0 for low, 1 for high (BRIGHTNESS)


def _init(n):
    global ON, STATE
    light = str(n)
        # light = VAL  # to be COMMENTED before exam demo
    url_to_call = lights_url + light + '/state'
    body = '{ "on" : false }'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    ON = False
    STATE = 0


def _turnOn(n):
    global ON, STATE
    light = str(n)
    body = '{ "on" : true, "alert":"none", "hue":10000, "bri":25, "sat":100 }'
        # light = VAL  # to be COMMENTED before exam demo
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    ON = True
    STATE = 0


def _turnOff(n):
    global ON, STATE
    light = str(n)
    body = '{ "on" : false}'
        # light = VAL   # to be COMMENTED before exam demo
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    ON = False
    STATE = 0

def _alarm(n):
    """
    Questa accende la luce, la fa diventare rossa per 2s, poi si rimette nelle condizioni
    iniziali.
    """
    all_the_lights = rest.send(url=lights_url)
    light = str(n)  # to be COMMENTED before exam demo

    initial = {}
    body = '{ "on" : true, "hue":0, "bri":254, "sat":254 }'

    dictionary = all_the_lights[light]
    state = dictionary["state"]
    initial[light] = state["on"]
    brght = state["bri"]

    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})

    time.sleep(0.5)

    for i in range(1, 4):  # to be ADJUSTED before exam demo, select an appropriate number
        body = '{ "on" : true, "hue":0, "sat":254, "bri":10}'
        rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
        time.sleep(0.5)
        body = '{ "on" : true, "hue":0, "sat":254, "bri":254}'
        rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
        time.sleep(0.5)

    #  end of the FOR loop light in all the lights

    if initial[light] == True:
        body = '{ "on" : true, "hue":10000, "sat":100, "bri":' + str(brght) + '}'
    else:
        body = '{ "on" : false, "hue":10000, "sat":100, "bri":' + str(brght) + '}'

    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    time.sleep(0.1)
        #  end of the FOR loop (to be added at line 90)


def _increaseBrightness(n):
    global STATE
    light = str(n)
    url_to_call = lights_url + light + '/state'
    body = '{ "on" : true, "hue":10000, "sat":100, "bri":125}'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    STATE = 1


def _decreaseBrightness(n):
    global STATE
    light = str(n)
    url_to_call = lights_url + light + '/state'
    body = '{ "on" : true, "hue":10000, "sat":100, "bri":25}'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    STATE = 0


def _consistency(n):
    time.sleep(0.1)
    if ON:
        if STATE == 0:
            brght = "25"
        else:
            brght = "125"
        body = '{ "on":true, "hue":10000, "sat":100, "bri":' + brght + '}'
    else:
        body = '{ "on":false}'

    light = str(n)
    url_to_call = lights_url + light + "/state"
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})


#wrappers to be called from outside
def init():
    _init(VAL)
def turnOn():
    _turnOn(VAL)
def turnOff():
    _turnOff(VAL)
def increaseBrightness():
    _increaseBrightness(VAL)
def decreaseBrightness():
    _decreaseBrightness(VAL)
def alarm():
    _alarm(VAL)
def consistency():
    _consistency(VAL)


#il main e solo per debug, must be REMOVED before exam demo
if __name__ == '__main__':
    # the base URL
    #base_url = 'http://192.168.0.201'
    # if you are using the emulator, probably the base_url will be:
    #base_url = 'http://localhost:8080'
    # example username, generated by following https://www.developers.meethue.com/documentation/getting-started
    #username = '1jlyVie2nvwtNwl0hv8KdZOO0okdvNcIIdPXWsdX'
    # if you are using the emulator, the username is:
    #username = 'newdeveloper'

    init()
    time.sleep(1)

    #caso 1
    turnOn()
    time.sleep(2)
    #alarm()
    consistency()
    time.sleep(1)

    #caso 2
    increaseBrightness()
    time.sleep(2)
    #alarm()
    consistency()
    time.sleep(1)

    #caso 3
    turnOff()
    time.sleep(2)
    #alarm()
    consistency()
    time.sleep(1)


    """
    #this is to scout the correct light
    all_the_lights = rest.send(url=lights_url)
    for light in all_the_lights:
        print(str(light) + " :: " + str(all_the_lights[light]))
    """

