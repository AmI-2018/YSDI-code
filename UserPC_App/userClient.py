"""
This module contains all the important functions on the user's PC side.

@author: Edoardo Calvi
"""

import requests, os, sqlite3
from shutil import copyfile
from TimeManagement import *
import json
from threading import Thread
import microphone as mic

blacklist = []                          #retrieved from the local server
history = ""                            #path of the sqlite file on the pc
copied = ""                             #path of the copied history (explained in init)
Ts = 0
last_check = 0
rasp_diff = 0

def checkBlacklist(blacklist, url):
    """
    This function checks if the given URL is in blacklist by checking the first part of it, right after 'http://'
    :param blacklist: list of forbidden websites
    :param url: url to be checked
    :return: index in the blacklist if present, -1 otherwise.
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
    This function initializes blacklist and both the history paths.
    In particular, copying the database is needed because it cannot be accessed otherwise while Google Chrome is running.
    Also, I found some functions to find the path dynamically, but they seem to work only on some PCs (not mine), as it
    appears that the location where the database is stored is not the same for everyone.
    :return: -1 if no blacklist was received, 0 otherwise.
    """
    global history
    global copied
    global blacklist
    global Ts
    global last_check
    global rasp_diff
    # My PC:
    history = "C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    # Others:
    # history = os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    copied = os.path.join(history, "YSDI-check")
    history = os.path.join(history, "History")
    info = requests.get(base_url + "/constants").json()
    l = info["blacklist"]
    rasp_time = info["RaspNow"]
    rasp_diff = ChromeCurrentInstant(0) - rasp_time
    if len(l) == 0:
        return -1
    Ts = int(info["samplingTime"])
    blacklist = []
    for elem in l:
        blacklist.append(elem)
    last_check = ChromeCurrentInstant(10)
    return 0

def sample(visits, base_url):
    """
    Sampling of the browser history, consequently sent to the local server.
    :param visits: empty list passed from the outside. It will contain the time-allowed couples.
    :return: 0 if Ok, -1 if failure in transmission, -2 if data was not received correctly, -3 if no new data was found

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
            visits.append([int(tupla[1]) - rasp_diff, False])
        else:
            visits.append([int(tupla[1]) - rasp_diff, True])
    toShip = {"pairsTimeSite" : visits}
    jSn = json.dumps(toShip)
    resp = requests.post(base_url + "/samples/chromeVisits", json=jSn)
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
            instant = ChromeCurrentInstant(0) - rasp_diff
            mic.record(mic.RECORD_SECONDS)
            val = mic.evaluate()
            print(val)
            mappa = {"startingInstant": instant, "currentThreshold": mic.NOISE_THRESHOLD, "len": mic.RECORD_SECONDS, "speaking": val}
            jSn = json.dumps(mappa)
            ret = requests.post(base_url + "/samples/microphone", json=jSn)
            mappa = ret.json()
            if mappa["reTare"]:
                mic.tare()


if __name__ == "__main__":
    audio = audioThread()
    audio.start()
    base_url = "http://192.168.0.47:8080"       #questo sarà IP della raspberry
    #initialize
    while init(base_url)==-1:
        print("Nessuna blacklist")
    #sampling loop
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
                #mappa.append([coppia[0], coppia[1]] )
            print(mappa)
        time.sleep(Ts)