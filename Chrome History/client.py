import requests
import json
import time
from TimeManagement import *


if __name__ == '__main__':
    # questo sarà l'url dove starà eseguendo l'API di YSDI sulla raspberry
    base_url = "http://192.168.1.66:8080"
    bannati = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]
    lista = [] #verrà usata per il confronto

    while len(lista)!=len(bannati):
        mandare = {"list": bannati}
        shippingJson = json.dumps(mandare)
        risposta = requests.post(base_url + "/blacklists", json=shippingJson)
        ritorno = risposta.json()
        lista = ritorno["blacklist"]
        time.sleep(3)   #per non affossare di richieste
    #qui ho finito l'inizializzazione e sono sicuro sia andata a buon fine
    print(lista)

    lastCheck = 0
    while True:
        if lastCheck == 0 :
            lastCheck = str(ChromeCurrentInstant(60))
        risposta = requests.get(base_url + "/samples/" + lastCheck)
        ritorno = risposta.json()
        lista = ritorno["pairsTimeSite"]
        if len(lista) != 0:
            lastCheck = lista[0][0] #prima coppia istante-sito, e prende l'istante

        #questo fra commenti è solo per debugging
        stampabile = []
        for elem in lista:
            stampabile.append(str(ChromeTimeToDatetime(int(elem[0]))) + " --> " + elem[1])
        print(stampabile)
        #

        time.sleep(5)
