"""
questo modulo contiene tutte le funzioni più importanti lato userPC.
Nel main c'è il modo in cui devono essere collegate
"""

import requests, os, sqlite3
from shutil import copyfile
from TimeManagement import *
import json
from threading import Thread
import microphone as mic

blacklist = []
history = ""
copied = ""
Ts = 0
last_check = 0

def checkBlacklist(blacklist, url):
    """
    Funzione per verificare se un URL è in blacklist
    :param blacklist: la lista di siti proibiti
    :param url: url da controllare
    :return: indice nella lista del sito visitato
    """
    i = url.find("://") + 3
    subs = url[i : len(url)-1]
    i = subs.find("/")
    if i != -1:
        fin = subs[0:i]
    else:
        fin = subs
    #print(fin + " " + subs)
    i=0
    l = len(blacklist)
    while i<l:
        if fin == blacklist[i]:
            return i
        i = i + 1
    return -1

def init(base_url):
    """
    Funzione per inizializzare la blacklist ed i percorsi history e copied
    :return: -1 se non ricevo una blacklist, 0 se tutto ok
    """
    global history
    global copied
    global blacklist
    global Ts
    global last_check
    # per il mio pc:
    history = "C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    # per gli altri:
    # history = os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    copied = os.path.join(history, "YSDI-check")
    history = os.path.join(history, "History")
    info = requests.get(base_url + "/constants").json()
    l = info["blacklist"]
    if len(l) == 0:
        return -1
    Ts = int(info["samplingTime"])
    blacklist = []
    for elem in l:
        blacklist.append(elem)
    last_check = ChromeCurrentInstant(60)
    return 0

def sample(visits, base_url):
    """
    Fa il sampling della browser history e lo invia al server.
    :param visits: lista, passata vuota, in cui saranno contenute le coppie tempo-sito
    :return: 0 se Ok, -1 se connection fail, -2 se non è arrivato il sample di là
    """
    global copied
    global last_check
    copyfile(history, copied)
    connection = sqlite3.connect(copied)
    if connection is None:
        return -1
    cursore = connection.cursor()
    sql = """
                SELECT url, last_visit_time
                FROM urls
                WHERE last_visit_time > ?
                ORDER BY last_visit_time DESC;
                """
    cursore.execute(sql, (last_check,))
    risultati = cursore.fetchall()
    if len(risultati) == 0:
        return -3
    connection.close()
    for tupla in risultati:
        isVisited = checkBlacklist(blacklist, tupla[0])
        if isVisited != -1:
            visits.append([tupla[1], False])
        else:
            visits.append([tupla[1], True])
    #print(visits)
    toShip = {"pairsTimeSite" : visits}
    jSn = json.dumps(toShip)
    resp = requests.post(base_url + "/samples/chromeVisits", json=jSn)
    #print(resp)
    ritorno = resp.json()
    if int(ritorno["length"])!=len(visits):
        return -2
    last_check = ChromeCurrentInstant(0) + 1
    return 0


class audioThread(Thread):          # this thread will manage the microphone
    def __init__(self):
        Thread.__init__(self)
        mic.tare()
    def run(self):
        while True:
            #print(mic.NOISE_THRESHOLD)
            instant = ChromeCurrentInstant(0)
            mic.record(mic.RECORD_SECONDS)
            val = mic.evaluate()
            print(val)
            mappa = {"startingInstant": instant, "currentThreshold": mic.NOISE_THRESHOLD, "speaking": val}
            jSn = json.dumps(mappa)
            ret = requests.post(base_url + "/samples/microphone", json=jSn)
            mappa = ret.json()
            if mappa["reTare"]:
                mic.tare()
            # mic.reproduce()


if __name__ == "__main__":
    audio = audioThread()
    audio.start()
    base_url = "http://192.168.1.66:8080"       #questo sarà IP della raspberry
    #inizializzo
    while init(base_url)==-1:
        print("Nessuna blacklist")
    #ciclo di sampling
    while True:
        visits = []
        check = sample(visits, base_url)
        if check == -1:
            print("Nessun database")
        elif check == -2:
            print("Trasmissione fallita")
        elif check == -3:
            print("Nessun nuovo dato")
        else:
            mappa = []
            for coppia in visits:
                mappa.append([str(ChromeTimeToDatetime(coppia[0])), coppia[1] ])
            print(mappa)
        time.sleep(Ts)