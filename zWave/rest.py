"""
Created on April 20, 2016
Update on May 31, 2017

@author: Luigi De Russis

Copyright (c) 2016-2017 Luigi De Russis
 
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

from requests import request, RequestException


def send(method='GET', url=None, data=None, headers={}, auth=None):
    # the response dictionary, initially empty
    response_dict = dict()
    
    # check that the URL is not empty
    if url is not None:
        # try to call the URL
        result = None
        try:
            # get the result
            if auth is not None:
                # HTTP Basic Auth is needed
                result = request(method, url, data=data, headers=headers, auth=auth)
            else:
                # without HTTP Basic Auth
                result = request(method, url, data=data, headers=headers)
        except RequestException as e:
            # print the error
            print(e)
        
        # check result
        if result is not None:
            # consider the response content as JSON and put it in the dictionary
            try:
                response_dict = result.json()
            except ValueError as ve:
                # no JSON, return the plain result
                response_dict = result

    return response_dict
