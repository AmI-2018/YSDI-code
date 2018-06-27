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
!!!
This version has been modified for a AmI-2018 project called YSDI, by:
Edoardo Calvi       --> most of this code
Matteo Garbarino    --> some tweaks, tested different versions, added 2 global variables useful for the main thread
"""

import rest
import time

#GLOBAL VARS
base_url = 'http://192.168.0.201'                       #hue bridge
username = "fFSt4atQ1zIcis0aAudg4ULMYx9AUiB9VYyDSLfO"   #granted by the bridge
lights_url = base_url + '/api/' + username + '/lights/'
VAL = "1"                                               #N of the hue light we use; this is mandatory when in ladispe
ON = False                                              #current state of the light
STATE = 0                                               # 0 for low, 1 for high (BRIGHTNESS)
#


def _init(n):
    """
    Reset the light to off. It also used to reset colour, brightness, saturation,
    but we later discovered that these changes are not accepted when the light is off.
    It's still here because of code readability.
    :param n: number of the light
    :return: /
    """
    _turnOff(n)


def _turnOn(n):
    """
    Turn on the light while setting other parameters as well, hopefully to reduce interferences
    from other groups as well.
    :param n: number of the light
    :return: /
    """
    global ON, STATE
    light = str(n)
    body = '{ "on" : true, "alert":"none", "hue":10000, "bri":25, "sat":100 }'
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    ON = True
    STATE = 0


def _turnOff(n):
    """
    Turn off the light. No other parameters can be set to increase consistency when it's set to off.
    :param n: number of the light
    :return: /
    """
    global ON, STATE
    light = str(n)
    body = '{ "on" : false}'
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    ON = False
    STATE = 0

def _alarm(n):
    """
    This function performs the blinking of the strobe red light: it saves the initial configuration
    (on/off, brightness), blinks, and resets to the initial condition. The sleep() calls are there because
    it is said in an explicit way on the API that no more than 10 requests per second shall be sent to the bridge.
    :param n: number of the light
    :return: /
    """
    all_the_lights = rest.send(url=lights_url)
    light = str(n)
    dictionary = all_the_lights[light]
    state = dictionary["state"]
    initial = state["on"]
    brght = state["bri"]

    body = '{ "on" : true, "hue":0, "bri":254, "sat":254 }'                 #set it to our first red blink
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    time.sleep(0.5)

    for i in range(1, 4):
        body = '{ "on" : true, "hue":0, "sat":254, "bri":10}'
        rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
        time.sleep(0.5)
        body = '{ "on" : true, "hue":0, "sat":254, "bri":254}'
        rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
        time.sleep(0.5)

    if initial == True:
        body = '{ "on" : true, "hue":10000, "sat":100, "bri":' + str(brght) + '}'
    else:
        body = '{ "on" : false, "hue":10000, "sat":100, "bri":' + str(brght) + '}'
    url_to_call = lights_url + light + '/state'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    time.sleep(0.1)


def _increaseBrightness(n):
    """
    After some tests in the lab we found this value of brightness to be already strong. More was disturbing.
    :param n: number of the light
    :return: /
    """
    global STATE
    light = str(n)
    url_to_call = lights_url + light + '/state'
    body = '{ "on" : true, "hue":10000, "sat":100, "bri":125}'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    STATE = 1


def _decreaseBrightness(n):
    """
    After some tests we found this value of brightness is enough.
    :param n: number of the light
    :return: /
    """
    global STATE
    light = str(n)
    url_to_call = lights_url + light + '/state'
    body = '{ "on" : true, "hue":10000, "sat":100, "bri":25}'
    rest.send('PUT', url_to_call, body, {'Content-Type': 'application/json'})
    STATE = 0


def _consistency(n):
    """
    This function is used because our tests showed that some of our requests were ignored or not received
    by the bridge, thus not behaving as expected even if the functions we used were working fine on the
    simulator. If no other request is sent, this is called, to repeat the state the light should be in.
    :param n: number of the light
    :return: /
    """
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



#main is for debugging reasons
if __name__ == '__main__':
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
    #this is to scout the correct light in ladispe
    all_the_lights = rest.send(url=lights_url)
    for light in all_the_lights:
        print(str(light) + " :: " + str(all_the_lights[light]))
    """
