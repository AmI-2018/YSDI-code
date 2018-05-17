from flask import jsonify, Flask, request
import os, sqlite3
import requests
from shutil import copyfile
from TimeManagement import *
import json

app = Flask(__name__)
history = ""
copied = ""
blacklist = []


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

@app.route("/historyModuleInit", methods=["POST"])
def init():
    """
    riceve come json una mappa con chiave la stringa "list" e value la lista di stringhe di siti bannati
    :return: un json con una mappa chiave "pairsTimeSite" e value una lista di coppie datetime-string.
    """

    global history
    global copied
    global blacklist
    #per il mio pc:
    history = "C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    #per gli altri:
    #history = os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    copied = os.path.join(history, "YSDI-check")
    history = os.path.join(history, "History")
    copyfile(history, copied)
    response = json.loads(request.json)
    l = response["list"]
    for elem in l:
        blacklist.append(elem)
    connection = sqlite3.connect(copied)
    cursore = connection.cursor()
    sql = """
        SELECT url, last_visit_time
        FROM urls
        WHERE last_visit_time > ?
        ORDER BY last_visit_time DESC;
        """
    cursore.execute(sql, (ChromeCurrentInstant(60),))
    risultati = cursore.fetchall()
    lista = []
    for tupla in risultati:
        istante = ChromeTimeToDatetime(tupla[1])
        isVisited = checkBlacklist(blacklist, tupla[0])
        if isVisited != -1:
            lista.append([str(istante), tupla[0]])
    toShip = {"pairsTimeSite" : lista}
    connection.close()
    return jsonify(toShip)

@app.route("/historyModuleSample", methods=["POST"])
def sampling():
    """
    riceve un json con una mappa che ha chiave "last" e value una stringa contenente il datetime dell'ultimo istante controllato
    :return: un json con una lista, come sopra
    """
    global copied
    connection = sqlite3.connect(copied)
    copyfile(history, copied)
    response = json.loads(request.json)
    istante = response["last"]
    cursore = connection.cursor()
    sql = """
            SELECT url, last_visit_time
            FROM urls
            WHERE last_visit_time > ?
            ORDER BY last_visit_time DESC;
            """
    cursore.execute(sql, (DatetimeToChromeTime(istante),))
    risultati = cursore.fetchall()
    lista = []
    for tupla in risultati:
        istante = ChromeTimeToDatetime(tupla[1])
        isVisited = checkBlacklist(blacklist, tupla[0])
        if isVisited != -1:
            lista.append([str(istante), tupla[0]])
    toShip = {"pairsTimeSite": lista}
    connection.close()
    return jsonify(toShip)

@app.route("/historyModuleStop")
def terminate():
    global connection
    connection.close()
    mappa = {"value" : "200 OK"}
    return jsonify(mappa)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
    #app.run()