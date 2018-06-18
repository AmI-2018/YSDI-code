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
blacklist = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]  # not permitted websites
samplingTime = 5         # seconds
loop = True              # True --> system is on
standing = False         # True --> user is repeating the studied topic while standing
score = 0
WEB_TIMEOUT = 10         # duration in seconds of an estimated time needed to read useful info from a web page
TIME_WINDOW = 30         # duration in seconds of the time range analyzed by the program at each loop
lastChair = 0            # variable keeping track of the last value for that sensor at the end of the previous loop
lastDesk = 0             #  //
carryWeb = 0             # variable keeping track of the remaining seconds counted as "studying" (i.e. 1) from last data
carryMicr = 0            #  //

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
def retrieve(chair, desk, web, mic):      # function receiving lists where data are going to be stored in
    print('----------------------------')
    retrieveChair(chair)
    retrieveDesk(desk)
    retrieveWeb(web)
    retrieveMic(mic)
    print('All data has been retrieved')
    print('----------------------------')


def retrieveChair(chair):                # function receiving list for chair data and filling it taking them from the DB
    global lastChair
    now = tm.ChromeCurrentInstant(0)
    data = db.getSit(toMicroSec(TIME_WINDOW), now)
    if not data:   # if empty list (no values retrieved in last 30 sec fro the sensor)
        i = 0
        while i < TIME_WINDOW:
            chair[i] = lastChair   # then assign value of previous loop (if they were sitting, nothing changed)
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0
        previousVal = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(now) - toSec(tupla[0]))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert and I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    chair[i] = lastChair
                    i = i + 1
                chair[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1): # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    chair[i] = previousVal
                    i = i + 1
                chair[pos] = val
                previousPos = pos
                previousVal = val
            else:                        # else we have to put it in first pos OR in the one next to the prev (no fill)
                chair[pos] = val
                previousPos = pos
                previousVal = val

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:    # completing if incomplete (maybe last val was not in the last cell)
            i = previousPos
            while i < TIME_WINDOW:
                chair[i] = previousVal
                i = i + 1

    print('Chair data has been retrieved')
    print(chair)
    print()


def retrieveDesk(desk):                 # DOCUMENTATION FOR THIS FUNCTION IS THE SAME OF retrieveChair(...)
    global lastDesk
    now = tm.ChromeCurrentInstant(0)
    data = db.getDesk(toMicroSec(TIME_WINDOW), now)
    if not data:
        i = 0
        while i < TIME_WINDOW:
            desk[i] = lastDesk
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0
        previousVal = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(now) - toSec(tupla[0]))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    desk[i] = lastDesk
                    i = i + 1
                desk[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1): # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    desk[i] = previousVal
                    i = i + 1
                desk[pos] = val
                previousPos = pos
                previousVal = val
            else:                         # completing if incomplete (maybe last val was not in the last cell)
                desk[pos] = val
                previousPos = pos
                previousVal = val

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:     # completing if incomplete
            i = previousPos
            while i < TIME_WINDOW:
                desk[i] = previousVal
                i = i + 1

    print('Desk data has been retrieved')
    print(desk)
    print()


def retrieveWeb(web):                       # DOCUMENTATION FOR THIS FUNCTION IS THE SAME OF retrieveChair(...)
    global carryWeb                         # the only addition is the carry, there could be remaining "studying" sec
                                            # from previous loop
    now = tm.ChromeCurrentInstant(0)
    data = db.getHist(toMicroSec(TIME_WINDOW), now)
    if not data:
        i = 0
        while i < TIME_WINDOW and carryWeb > 0:
            web[i] = carryWeb
            i = i + 1
            carryWeb = carryWeb - 1
        while i < TIME_WINDOW:
            web[i] = 0
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(now) - toSec(tupla[0]))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    if carryWeb > 0:
                        web[i] = carryWeb
                        carryWeb = carryWeb - 1
                    else:
                        web[i] = 0
                    i = i + 1
                if val == 1:
                    carryWeb = WEB_TIMEOUT
                else:
                    carryWeb = 0
                web[pos] = carryWeb
                if carryWeb > 0:
                    carryWeb = carryWeb - 1
                previousPos = pos

            elif pos > (previousPos + 1): # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    if carryWeb > 0:
                        web[i] = carryWeb
                        carryWeb = carryWeb - 1
                    else:
                        web[i] = 0
                    i = i + 1
                if val == 1:
                    carryWeb = WEB_TIMEOUT
                else:
                    carryWeb = 0
                web[pos] = carryWeb
                if carryWeb > 0:
                    carryWeb = carryWeb - 1
                previousPos = pos

            else:                         # completing if incomplete (maybe last val was not in the last cell)
                if val == 1:
                    carryWeb = WEB_TIMEOUT
                else:
                    carryWeb = 0
                web[pos] = carryWeb
                if carryWeb > 0:
                    carryWeb = carryWeb - 1
                previousPos = pos

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:     # completing if incomplete
            i = previousPos
            while i < TIME_WINDOW:
                web[i] = carryWeb
                if carryWeb > 0:
                    carryWeb = carryWeb - 1
                i = i + 1

    print('Web data has been retrieved')
    print(web)
    print()


def retrieveMic(micr):                      # DOCUMENTATION FOR THIS FUNCTION IS THE SAME OF retrieveWeb(...)
    global carryMicr
    now = tm.ChromeCurrentInstant(0)
    data = db.getMic(toMicroSec(TIME_WINDOW), now)

    if not data:
        i = 0
        while i < TIME_WINDOW and carryMicr > 0:
            micr[i] = carryMicr
            i = i + 1
            carryMicr = carryMicr - 1
        while i < TIME_WINDOW:
            micr[i] = 0
            i = i + 1
    else:
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(now) - toSec(tupla[0]))
            val = int(tupla[1])

            if pos > 0 and tupleNumber == 0:  # if 1st time I insert I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    if carryMicr > 0:
                        micr[i] = carryMicr
                        carryMicr = carryMicr - 1
                    else:
                        micr[i] = 0
                    i = i + 1
                if val == 1:
                    carryMicr = mic.RECORD_SECONDS
                else:
                    carryMicr = 0
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            elif pos > (previousPos + 1): # if not 1st time I insert I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    if carryMicr > 0:
                        micr[i] = carryMicr
                        carryMicr = carryMicr - 1
                    else:
                        micr[i] = 0
                    i = i + 1
                if val == 1:
                    carryMicr = mic.RECORD_SECONDS
                else:
                    carryMicr = 0
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            else:                         # completing if incomplete (maybe last val was not in the last cell)
                if val == 1:
                    carryMicr = mic.RECORD_SECONDS
                else:
                    carryMicr = 0
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW:     # completing if incomplete
            i = previousPos
            while i < TIME_WINDOW:
                micr[i] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                i = i + 1

    print('Mic data has been retrieved')
    print(micr)
    print()


def toSec(micro):        # switching from microseconds to seconds
    return micro/1000000


def toMicroSec(sec):     # switching from seconds to microseconds
    return sec*1000000


def analise(chair, desk, web, micr, result):  # this function combines data from all the sensors and generates result
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
    print('Data has been processed')
    print('----------------------------')


def update(result):                          # this function analyzes result and, if it's the case, updates the score
    tot = 0
    for i in result:  # counts how many seconds have been evaluated as "studying"
        tot = tot + i
    if tot >= TIME_WINDOW/2:  # if at least half of the seconds of the time window were ok, then increment score
        global score
        score = score + 1
        print('['+str(score-1)+']->['+str(score)+']')
    else:
        print('[' + str(score) + ']->[' + str(score) + ']')
    print('Score has been updated')
    print('----------------------------')


def setLast(chair, desk, web, micr): # this function takes last values from the data lists and stores them for next loop
    global lastChair
    global lastDesk

    lastChair = chair[TIME_WINDOW-1]
    lastDesk = desk[TIME_WINDOW - 1]
    # web carry is already set in retrieveWeb(...)
    # microphone carry is already set in retrieveMic(...)

    print('[C]->[' + str(lastChair) + '] , '+'[D]->[' + str(lastDesk) + '] , '+'[W]->[' + str(carryWeb) + '] , '
          + '[M]->[' + str(carryMicr) + ']')
    print('All termination data has been stored')
    print('----------------------------')


def updateLight():                  # at each loop cycle the luminosity is checked and, if necessary, light is regulated
    print('5')


# Threads:
class scoreThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):                  # this thread will handle data, evaluate the score and check/set lights
        global score
        global TIME_WINDOW

        # sensors data will be stored in lists (1 per sensor) with TIME_WINDOW elements each one representing 1 second
        # with value 0 if in the second the user didn't study (according to our measurements)
        # with value 1 if instead they did study
        chair = []
        desk = []
        web = []
        micr = []
        result = []

        db.ClearAll()

        i = 0

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


class audioThread(Thread):          # this thread will manage the microphone
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        db.ClearAll()
        while True:
            mic.record(mic.RECORD_SECONDS)
            val = mic.evaluate()
            if val == True:
                db.MicInsert()


if __name__ == "__main__":          # this thread will host the web interface
    tare()
    print("Fine tara")
    audio = audioThread()
    audio.start()

    scoreT = scoreThread()
    scoreT.start()

    actualIp = socket.gethostbyname(socket.gethostname())
    print(actualIp)
    app.run(host="0.0.0.0", port=8080)
