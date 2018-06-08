from flask import Flask, request, render_template
import json
from threading import Thread
import microphone as mic
import db
import time
import sqlite3
import os.path
import socket

app = Flask(__name__)
blacklist = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]
samplingTime = 5  # secondi, intero
loop = True


@app.route("/constants")
def parametri():
    """
    :return: un jSon che contiene il sampling time e la blacklist
    """
    toShip = {"blacklist" : blacklist, "samplingTime" : str(samplingTime)}
    jSn = json.dumps(toShip)
    return jSn


@app.route("/samples/chromeVisits", methods=["POST"])
def handleSamples():
    """
    :return: un jSon che contiene la lunghezza della lista di samples ricevuti
    """
    mappa = json.loads(request.json)
    visits = mappa["pairsTimeSite"]
    db.HistoryInsert(visits)
    mappa = {"length" : str(len(visits))}
    jSn = json.dumps(mappa)
    return jSn


@app.route("/jsData/tare")
def getTares():
    diz = {"values": {"mic": str(mic.getNoise())}}
    jSn = json.dumps(diz)
    return jSn


@app.route("/constants/tare")
def tare():
    """
    Questa dovrà fare la tara di tutti gli strumenti, su richiesta!
    Per cominciare fa solo quella del microfono
    :return:
    """
    mic.tare()
    jSn = json.dumps({"response": 200})
    return jSn

@app.route("/jsData/visits")
def testLadispe0406():
    hc = db.HistoryCount()
    mc = db.MicCount()
    diz = {"history-count": str(hc), "mic-count": str(mc)}
    jSn = json.dumps(diz)
    return jSn


@app.route("/")
def mainPage():
    return render_template("index.html", myIp=str(actualIp))


@app.route("/functions/stopStudying")
def stop():
    global loop
    loop = False
    return render_template("index.html", end=1)


@app.route("/functions/updateScore")
def update():
    newScore = db.getScore()
    jSn = json.dumps({"newScore": newScore})
    return jSn


@app.route("/functions/repeating")
def repeating():
    newScore = db.getScore()
    jSn = json.dumps({"newScore": newScore})
    return jSn


class scoreThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        print("start working")
        while loop:
            #print("working")
            time.sleep(1)


class audioThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        db.ClearAll()
        while True:
            mic.record(mic.RECORD_SECONDS)
            val = mic.evaluate()
            if val == True:
                db.MicInsert()


if __name__ == "__main__":
    tare()
    print("Fine tara")
    audio = audioThread()
    audio.start()

    score = scoreThread()
    score.start()

    actualIp = socket.gethostbyname(socket.gethostname())
    print(actualIp)
    app.run(host="0.0.0.0", port=8080)
