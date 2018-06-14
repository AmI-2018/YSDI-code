from flask import Flask, request, render_template
import json
from threading import Thread
import microphone as mic
import db
import time
import sqlite3
import os.path
import socket
import TimeManagement as tm
import zWaveModule as zwm
import hueLightsModule as hlm

# Global vars
app = Flask(__name__)
blacklist = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]
samplingTime = 5  # secondi, intero
loop = True
score = 0
last_score_update = 0
TIME_WINDOW = 30
lastChair = 0
lastDesk = 0
lastWeb = 0
carryMicr = 0

# App routes:
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


# Functions:
def retrieve(chair, desk, web, mic):
    print('----------------------------')
    retrieveChair(chair)
    retrieveDesk(desk)
    retrieveWeb(web)
    retrieveMic(mic)
    print('All data have been retrieved')
    print('----------------------------')


def retrieveChair(chair):
    now = tm.ChromeCurrentInstant(0)
    data = db.getSit(toMicroSec(TIME_WINDOW), now)
    if not data:
        i = 0
        while i < TIME_WINDOW:
            chair[i] = 0
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(tupla[0]) - toSec(now))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                global lastChair
                while i < pos and i < TIME_WINDOW:
                    chair[i] = lastChair
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                chair[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1):  # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    chair[i] = previousVal
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                chair[pos] = val
                previousPos = pos
                previousVal = val
            else:
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                chair[pos] = val
                previousPos = pos
                previousVal = val

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:  # completing if uncomplete
            i = previousPos
            while i < TIME_WINDOW:
                chair[i] = previousVal
                i = i + 1

    print('Chair data have been retrieved')
    print(chair)
    print()

def retrieveDesk(desk):
    now = tm.ChromeCurrentInstant(0)
    data = db.getDesk(toMicroSec(TIME_WINDOW), now)
    if not data:
        i = 0
        while i < TIME_WINDOW:
            desk[i] = 0
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(tupla[0]) - toSec(now))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                global lastDesk
                while i < pos and i < TIME_WINDOW:
                    desk[i] = lastDesk
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                desk[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1):  # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    desk[i] = previousVal
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                desk[pos] = val
                previousPos = pos
                previousVal = val
            else:
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                desk[pos] = val
                previousPos = pos
                previousVal = val

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:  # completing if uncomplete
            i = previousPos
            while i < TIME_WINDOW:
                desk[i] = previousVal
                i = i + 1

    print('Desk data have been retrieved')
    print(desk)
    print()


def retrieveWeb(web):
    now = tm.ChromeCurrentInstant(0)
    data = db.getHist(toMicroSec(TIME_WINDOW), now)
    if not data:
        i = 0
        while i < TIME_WINDOW:
            web[i] = 0
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(tupla[0]) - toSec(now))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                global lastWeb
                while i < pos and i < TIME_WINDOW:
                    web[i] = lastWeb
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                web[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1):  # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    web[i] = previousVal
                    i = i + 1
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                web[pos] = val
                previousPos = pos
                previousVal = val
            else:
                # print('putting in pos: ' + str(pos) + ' value: ' + str(val))
                web[pos] = val
                previousPos = pos
                previousVal = val

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:  # completing if uncomplete
            i = previousPos
            while i < TIME_WINDOW:
                web[i] = previousVal
                i = i + 1

    print('Web data have been retrieved')
    print(web)
    print()

def retrieveMic(micr):  # TO BE REDEFINED
    now = tm.ChromeCurrentInstant(0)
    data = db.getMic(toMicroSec(TIME_WINDOW), now)
    global carryMicr

    if not data:
        i = 0
        while carryMicr > 0:
            micr[i] = 1
            carryMicr = carryMicr - 1
            i = i + 1
        while i < TIME_WINDOW:
            micr[i] = 0
            i = i + 1
    else:
        previousPos = 0
        i = 0

        while carryMicr > 0:
            micr[i] = 1
            carryMicr = carryMicr - 1
            previousPos = previousPos + 1

        for tupla in data: # scanning all tuples
            pos = int(toSec(tupla[0])-toSec(now))

            if pos > (previousPos+1):  # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos+1
                while i < pos and i<TIME_WINDOW:
                    micr[i] = 0
                    i = i + 1
                previousPos = pos
                carryMicr = mic.RECORD_SECONDS
                while previousPos<pos+mic.RECORD_SECONDS and previousPos < TIME_WINDOW:
                    micr[previousPos] = 1
                    previousPos = previousPos + 1
                    carryMicr = carryMicr -1
            else:
                carryMicr = mic.RECORD_SECONDS
                previousPos = previousPos + 1
                while previousPos < pos + mic.RECORD_SECONDS and previousPos < TIME_WINDOW:
                    micr[previousPos] = 1
                    previousPos = previousPos + 1
                    carryMicr = carryMicr - 1

        if previousPos<TIME_WINDOW:  # completing if uncomplete
            i=previousPos
            while i<TIME_WINDOW:
                micr[i]=0
                i=i+1

    print('Mic data have been retrieved')
    print(micr)
    print()


def toSec(micro):
    return micro/1000000


def toMicroSec(sec):
    return sec*1000000


def analise(chair, desk, web, micr, result):
    i = 0
    while i < TIME_WINDOW:
        if chair[i] == 0:
            result[i] = 0;
        else:
            if micr[i] == 1 and web[i] != 0:
                result[i] = 1
            if desk[i] == 1:
                result[i] == 1
            if web[i] == 1:
                result[i] = 1
        i = i+1
    print(result)
    print('Data have been processed')
    print('----------------------------')


def update(result):
    tot = 0
    for i in result:
        tot = tot + i
    if tot >= TIME_WINDOW/2:
        global score
        score = score + 1
        print('['+str(score-1)+']->['+str(score)+']')
    else:
        print('[' + str(score) + ']->[' + str(score) + ']')
    print('Score has been updated')
    print('----------------------------')


def setLast(chair, desk, web, micr):
    global lastChair
    global lastDesk
    global lastWeb

    lastChair = chair[TIME_WINDOW-1]
    lastDesk = desk[TIME_WINDOW - 1]
    lastWeb = web[TIME_WINDOW - 1]
    # microphone carry is already set in retrieveMic(...)

    print('[C]->[' + str(lastChair) + '] , '+'[D]->[' + str(lastDesk) + '] , '+'[W]->[' + str(lastWeb) + '] , '
          + '[M]->[' + str(carryMicr) + ']')
    print('All ending data have been stored')
    print('----------------------------')


def updateLight():
    print('5')


# Threads:
class scoreThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global score
        global TIME_WINDOW

        chair = []
        desk = []
        web = []
        micr = []
        result = []

        db.ClearAll()

        i=0

        # lists initialization
        while i < TIME_WINDOW:
            chair.append(0)
            desk.append(0)
            web.append(0)
            micr.append(0)
            result.append(0)
            i = i+1

        print("start working")
        while loop:

            retrieve(chair, desk, web, micr)

            analise(chair, desk, web, micr, result)

            update(result)

            setLast(chair, desk, web, micr)

            updateLight()

            time.sleep(TIME_WINDOW)

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
