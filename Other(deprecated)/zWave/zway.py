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
"""

import rest
import time


if __name__ == '__main__':

    # the base url
    base_url = 'http://192.168.0.202:8083'

    # login credentials, to be replaced with the right ones
    # N.B. authentication may be disabled from the configuration of the 'Z-Wave Network Access' app
    # from the website available at 'base_url'
    username = 'admin'
    password = 'admin'

    # get z-wave devices
    all_devices = rest.send(url=base_url + '/ZWaveAPI/Data/0', auth=(username, password))
    # without auth, omit the last parameter
    # all_devices = rest.send(url=base_url + '/ZWaveAPI/Data/0')

    # clean up all_devices
    all_devices = all_devices['devices']
    # remove the Z-Way controller from the device list
    all_devices.pop('1')

    # "prototype" and base URL for getting/setting device properties
    device_url = base_url + '/ZWaveAPI/Run/devices[{}].instances[{}].commandClasses[{}]'

    # some useful command classes
    switch_binary = '37'
    sensor_binary = '48'
    sensor_multi = '49'

    # search for devices to be "operated", in this case power outlets, temperature, and motion sensors
    for device_key in all_devices:
        # iterate over device instances
        for instance in all_devices[device_key]['instances']:
            # search for the SwitchBinary (37) command class, i.e., power outlets
            if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
                print('Turning on device %s...' % device_key)
                # turn it on (255)
                url_to_call = (device_url + '.Set(255)').format(device_key, instance, switch_binary)
                rest.send(url=url_to_call, auth=(username, password))
            # search for the SensorMultilevel (49) command class, e.g., for temperature
            if sensor_multi in all_devices[device_key]['instances'][instance]['commandClasses']:
                # debug
                print('Device %s is a sensor multilevel' % device_key)
                # get data from the multilevel class
                url_to_call = device_url.format(device_key, instance, sensor_multi)
                # info from devices is in the response
                response = rest.send(url=url_to_call, auth=(username, password))
                # 1: temperature, 3: luminosity, 5: humidity (numbers must be used as strings)
                val = response['data']['1']['val']['value']
                unit_of_measure = response['data']['1']['scaleString']['value']
                print('The temperature is ' + str(val) + unit_of_measure)
            # search for the SensorBinary (48) command class, e.g., for motion
            if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
                # debug
                print('Device %s is a sensor binary' % device_key)
                # get motion
                url_to_call = device_url.format(device_key, instance, sensor_binary)
                # info from devices is in the response
                response = rest.send(url=url_to_call, auth=(username, password))
                val = response['data']['1']['level']['value']
                print('Motion: ' + str(val))

    # reverse count to off
    for i in range(0, 10):
        time.sleep(1)
        print(10 - i)

    # search for power outlets, again
    for device_key in all_devices:
        # iterate over device instances
        for instance in all_devices[device_key]['instances']:
            # search for the SwitchBinary (37) command class, i.e., power outlets
            if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses'].keys():
                print('Turning off device %s...' % device_key)
                # turn it off (0)
                url_to_call = (device_url + '.Set(0)').format(device_key, instance, switch_binary)
                rest.send(url=url_to_call, auth=(username, password))
