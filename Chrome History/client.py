from flask import Flask, jsonify
import requests
import json
import time, datetime
from TimeManagement import *


if __name__ == '__main__':
    # questo sarà l'url dove starà eseguendo l'API di YSDI sulla raspberry
    base_url = "http://192.168.1.66:8080"
    local_url = "http://127.0.0.1:5000"
    bannati = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]
    mandare = {"list": bannati}
    testJ = json.dumps(mandare)
    risposta = requests.post(base_url + "/historyModuleInit", json=testJ)
    ritorno = risposta.json()
    lista = ritorno["pairsTimeSite"]
    print(lista)
    if len(lista)==0:
        t=str(datetime.datetime.now())
    else:
        t = StringToDatetime(lista[0][0])
        t = str(t + datetime.timedelta(seconds=1))
    while True:
        time.sleep(5)
        mandare = {"last":t}
        testJ = json.dumps(mandare)
        risposta = requests.post(base_url + "/historyModuleSample", json=testJ)
        ritorno = risposta.json()
        lista = ritorno["pairsTimeSite"]
        if len(lista) != 0:
            t = StringToDatetime(lista[0][0])
            t = str(t + datetime.timedelta(seconds=1))
        print(str(lista))
