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
score = 0
last_score_update = 0


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

@app.route("/jsData/report")
def report():
    hc = db.HistoryCount()
    mc = db.MicCount()
    last = db.getLastSit()
    diz = {"history-count": str(hc), "mic-count": str(mc), "sit": str(last), "score": str(score)}
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


@app.route("/arduino", methods=["POST"])
def sitting():
    diz = request.json
    db.ChairInsert(diz["value"])
    jSn = json.dumps({"value": 200})
    return jSn


@app.route("/functions/repeating")
def repeating():
    jSn = json.dumps({"newScore": score})
    return jSn


class scoreThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global score
        print("start working")
        while loop:
            #print("working")
            time.sleep(10)
            score = score + 1

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

    scoreT = scoreThread()
    scoreT.start()

    actualIp = socket.gethostbyname(socket.gethostname())
    print(actualIp)
    app.run(host="0.0.0.0", port=8080)
