"""
This is the main module of the project. It starts several threads from its main.

@author: Matteo Garbarino       --> manage all the score system + adjust the lights
@author: Edoardo Calvi          --> almost all of the Flask app + serial communication with Arduino
@author: Oliviero Vouch         --> serial communication with Arduino
"""

from flask import Flask, request, render_template
import json
from threading import Thread
from warn import warning
import db
import time
import socket
import TimeManagement as tm
import zWaveModule as zwm
import hueLightsModule as hlm
import serial

# Global vars
app = Flask(__name__)
micReTare = False
micThreshold = 500    # this holds the mic parameters, since we can no longer call functions on a locally running thread
micRECORD_SECONDS = 5
remaining_seconds = 0
blacklist = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]  # not permitted websites
samplingTime = 5         # seconds
LUX_THRESHOLD_LOW = 200  # threshold in Lux to regulate light
LUX_THRESHOLD_HIGH = 400 # threshold in Lux to regulate light
loop = True              # True --> system is on
standing = False         # True --> user is repeating the studied topic while standing
pause = False            # True --> user is taking a break
should_take_a_break = False #True --> user should take a break
buffer = []              # Buffer for keeping track of recent distractions --> suggest pause
distractionsSeries = 0   # Variable for keeping track of the number of distractions in a row --> alarm
score = 15                # global user score
WEB_TIMEOUT = 10         # duration in seconds of an estimated time needed to read useful info from a web page
TIME_WINDOW = 30         # duration in seconds of the time range analyzed by the program at each loop
MAX_PUNISHMENT = WEB_TIMEOUT//3  # number of "studying" actions to be done after having visited a forbidden website
                                 # before getting points again
BUFFER_SIZE = 5          # size of the buffer for the most recent loops results
SERIES_TRESHOLD = 3      # number of subsequent loops in which the user is distracted before the alarm is called
lastChair = 0            # variable keeping track of the last value for that sensor at the end of the previous loop
lastDesk = 0             #  //
carryWeb = 0             # variable keeping track of the remaining seconds counted as "studying" (i.e. 1) from last data
carryMicr = 0            #  //


# App routes:
@app.route("/constants")
def parametri():
    """
    :return: a json containing forbidden sites and sampling time
    """
    toShip = {"blacklist" : blacklist, "samplingTime" : str(samplingTime), "RaspNow" : tm.ChromeCurrentInstant(0)}
    jSn = json.dumps(toShip)
    return jSn


@app.route("/samples/chromeVisits", methods=["POST"])
def handleSamples():
    """
    :return: a jSon containing the length of the received data
    """
    mappa = json.loads(request.json)
    visits = mappa["pairsTimeSite"]
    db.HistoryInsert(visits)
    mappa = {"length" : str(len(visits))}
    jSn = json.dumps(mappa)
    return jSn

@app.route("/samples/microphone", methods=["POST"])
def handleMicrophone():
    """
    It receives a dictionary with key "startingInstant" and the instant the recording started as value.
    :return: (piggybacking) a json with a request to retare the microphone
    """
    global micThreshold, micReTare, micRECORD_SECONDS
    mappa = json.loads(request.json)
    instant = mappa["startingInstant"]
    micThreshold = mappa["currentThreshold"]
    micRECORD_SECONDS = mappa["len"]
    speaking = mappa["speaking"]
    if speaking:
        db.MicInsert(instant)
    print(micThreshold)
    ret = {"reTare": micReTare}
    if micReTare:
        micReTare = False
    return json.dumps(ret)


@app.route("/constants/tare")
def tare():
    """
    This function is called when a re-taring operation is requested
    :return: success
    """
    global micReTare
    micReTare = True
    jSn = json.dumps({"response": 200})
    return jSn

@app.route("/jsData/report")
def report():
    """
    This is called periodically from the web interface to update the values.
    :return: a json with a dictionary which plenty of info, including debug
    """
    lastH = db.HistoryLast()
    lastMIC = db.MicLast()
    lastCH = str(lastChair)
    last5DSK = db.DeskLast5()
    if pause:
        val1 = 1
    else:
        val1 = 0
    if should_take_a_break:
        val2 = 1
    else:
        val2 = 0
    diz = {"history-last": lastH, "mic-last": lastMIC, "sit": lastCH, "desk-last5": last5DSK, "mic-threshold": str(micThreshold), "score": str(score), "TAB": val2, "pausing": val1, "remainingTime": remaining_seconds}
    jSn = json.dumps(diz)
    return jSn


@app.route("/")
def mainPage():
    return render_template("index.html", myIp=str(actualIp))


@app.route("/functions/stopStudying")
def stop():
    """
    Called when the user stops to study, it's just symbolic.
    :return: modified template
    """
    global loop
    loop = False
    return render_template("index.html", end=1)


@app.route("/arduino", methods=["POST"])
def sitting():
    """
    Called from Arduino Yun when posting data from the chair
    :return: success
    """
    diz = request.json
    db.ChairInsert(diz["value"])
    print("Chair: " + str(diz["value"]))
    jSn = json.dumps({"value": 200})
    return jSn


@app.route("/functions/repeating")
def repeating():
    """
    Called when the user wants to repeat while standing. Beware that this would work better if our microphone
    was sensitive enough.
    :return: updated score
    """
    global standing
    standing = True
    jSn = json.dumps({"newScore": score})
    return jSn


@app.route("/functions/coffee")
def coffee():
    """
    Turn on the coffee machine when requested
    :return: score
    """
    global pause
    global score
    global should_take_a_break
    global remaining_seconds
    should_take_a_break = False
    pause = True
    zwm.turnOnPlug("coffeeMachine")
    hlm.turnOff()
    remaining_seconds = -1
    jSn = json.dumps({"newScore": score})
    return jSn


@app.route("/functions/pausing/<minutes>")
def pausing(minutes):
    """
    This is called for distracting devices and any other break that is not the coffee machine
    :param minutes: -1 --> not limited
    :return: updated score and info about remaining time
    """
    global pause
    global score
    global should_take_a_break
    global remaining_seconds
    should_take_a_break = False
    pause = True
    if int(minutes) != -1:
        score = score - 10*int(minutes)
        remaining_seconds = 60*int(minutes)
        zwm.turnOnPlug("dev1")
    else:
        remaining_seconds = -1
    hlm.turnOff()
    jSn = json.dumps({"newScore": score, "remainingTime": remaining_seconds})
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
    data = db.getSit(toMicroSec(TIME_WINDOW-1), now)
    if not data:   # if empty list (no values retrieved in last 30 sec from the sensor)
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
            pos = TIME_WINDOW - pos
            if pos >= TIME_WINDOW:
                pos = TIME_WINDOW-1  # this brute force solution has revealed to be necessary due to the time data
                # approximations (rounding) that sometimes lead to an index approximated by excess
            elif pos < 0:  # this actually never happened, but for robustness we put this check
                pos = 0
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

        if previousPos < TIME_WINDOW-1:    # completing if incomplete (maybe last val was not in the last cell)
            i = previousPos+1
            while i < TIME_WINDOW:
                chair[i] = previousVal
                i = i + 1

    print('Chair data has been retrieved')
    print(chair)
    print()


def retrieveDesk(desk):                 # DOCUMENTATION FOR THIS FUNCTION IS THE SAME OF retrieveChair(...)
    global lastDesk
    now = tm.ChromeCurrentInstant(0)
    data = db.getDesk(toMicroSec(TIME_WINDOW-1), now)
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
            pos = TIME_WINDOW - pos
            if pos >= TIME_WINDOW:
                pos = TIME_WINDOW-1  # this brute force solution has revealed to be necessary due to the time data
                # approximations (rounding) that sometimes lead to an index approximated by excess
            elif pos < 0:  # this actually never happened, but for robustness we put this check
                pos = 0
            if pos > 0 and tupleNumber == 0:  # if 1st time I insert and I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    desk[i] = lastDesk
                    i = i + 1
                desk[pos] = val
                previousPos = pos
                previousVal = val
            elif pos > (previousPos + 1):  # if not 1st insert and I do not have to do it next to prev, fill up to pos
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

        if previousPos < TIME_WINDOW-1:     # completing if incomplete
            i = previousPos+1
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
    data = db.getHist(toMicroSec(TIME_WINDOW-1), now)
    print(data)
    if not data:
        print("data not found")
        i = 0
        while i < TIME_WINDOW and carryWeb > 0:
            web[i] = carryWeb
            i = i + 1
            carryWeb = carryWeb - 1
        while i < TIME_WINDOW:
            web[i] = 0
            i = i + 1
    else:
        print("data found")
        tupleNumber = 0
        previousPos = 0

        for tupla in data:  # scanning all tuples
            pos = int(toSec(now) - toSec(tupla[0]))
            val = int(tupla[1])
            pos = TIME_WINDOW - pos
            print("Putting in pos: " + str(pos))
            print(str(toSec(now)))
            if pos >= TIME_WINDOW:
                pos = TIME_WINDOW-1  # this brute force solution has revealed to be necessary due to the time data
                # approximations (rounding) that sometimes lead to an index approximated by excess
            elif pos < 0:  # this actually never happened, but for robustness we put this check
                pos = 0
            if pos > 0 and tupleNumber == 0:  # if 1st time I insert and I do not have to do it in head, fill up to pos
                print("Case A")
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
                    web[pos] = carryWeb
                    carryWeb = carryWeb - 1
                else:
                    carryWeb = 0
                    web[pos] = -1  # this value will be used when analyzing the data, it marks a forbidden website

                previousPos = pos

            elif pos > (previousPos + 1):  # if not 1st insert and I do not have to do it next to prev, fill up to pos
                print("Case B")
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
                    web[pos] = carryWeb
                    carryWeb = carryWeb - 1
                else:
                    carryWeb = 0
                    web[pos] = -1  # this value will be used when analyzing the data, it marks a forbidden website
                previousPos = pos

            else:                         # completing if incomplete (maybe last val was not in the last cell)
                print("Case C")
                if val == 1:
                    carryWeb = WEB_TIMEOUT
                    web[pos] = carryWeb
                    carryWeb = carryWeb - 1
                else:
                    carryWeb = 0
                    web[pos] = -1

                previousPos = pos

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW-1:     # completing if incomplete
            print("Case D")
            i = previousPos+1
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
    data = db.getMic(toMicroSec(TIME_WINDOW-1), now)

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
            pos = TIME_WINDOW - pos
            if pos >= TIME_WINDOW:
                pos = TIME_WINDOW-1  # this brute force solution has revealed to be necessary due to the time data
                # approximations (rounding) that sometimes lead to an index approximated by excess
            elif pos < 0:  # this actually never happened, but for robustness we put this check
                pos = 0
            if pos > 0 and tupleNumber == 0:  # if 1st time I insert and I do not have to do it in head, fill up to pos
                i = 0
                while i < pos and i < TIME_WINDOW:
                    if carryMicr > 0:
                        micr[i] = carryMicr
                        carryMicr = carryMicr - 1
                    else:
                        micr[i] = 0
                    i = i + 1
                carryMicr = micRECORD_SECONDS
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            elif pos > (previousPos + 1):  # if not 1st insert and I do not have to do it next to prev, fill up to pos
                i = previousPos + 1
                while i < pos and i < TIME_WINDOW:
                    if carryMicr > 0:
                        micr[i] = carryMicr
                        carryMicr = carryMicr - 1
                    else:
                        micr[i] = 0
                    i = i + 1
                carryMicr = micRECORD_SECONDS
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            else:                         # completing if incomplete (maybe last val was not in the last cell)
                carryMicr = micRECORD_SECONDS
                micr[pos] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                previousPos = pos

            tupleNumber = tupleNumber + 1

        if previousPos < TIME_WINDOW-1:     # completing if incomplete
            i = previousPos+1
            while i < TIME_WINDOW:
                micr[i] = carryMicr
                if carryMicr > 0:
                    carryMicr = carryMicr - 1
                i = i + 1

    print('Mic data has been retrieved')
    print(micr)
    print()


def toSec(micro):        # switching from microseconds to seconds
    return micro//1000000   # integer division is necessary to avoid index out of bound exception with the position


def toMicroSec(sec):     # switching from seconds to microseconds
    return sec*1000000


def analyze(chair, desk, web, micr, result):  # this function combines data from all the sensors and generates result
    # must take into account also standing and pause (and the buffer/var for the distractions/alarm)
    global standing, pause, remaining_seconds
    if pause:
        print("Pause recognized")
        
        standing = False
        i = 0
        while i < TIME_WINDOW:  # do not give points to the users if taking a break
            result[i] = 0
            i = i + 1
        if remaining_seconds == -1 and lastChair == 1:  # if taking a break not timed and come back sitting, exit pause
            remaining_seconds = 0
            pause = False
            zwm.turnOffPlug("coffeeMachine")
            print("Terminating pause")
        elif remaining_seconds > 0:  # if is a timed pause, decrement time if there's some time left
            remaining_seconds = remaining_seconds - TIME_WINDOW
        elif remaining_seconds == 0:  # if the timed pause run out of time, exit from pause
            pause = False
            zwm.turnOffPlug("dev1")
            hlm.alarm()
            warning()
            print("Terminating pause")
    elif standing:
        print("Standing study recognized")
        i = 0
        punishmentCounter = 0
        while i < TIME_WINDOW:
            if web[i] == -1:
                punishmentCounter = MAX_PUNISHMENT  # whenever the user visits a forbidden website, then he has
                                                    # to do MAX_PUNISHMENT number of good actions
            elif (web[i] > 0 or micr[i] > WEB_TIMEOUT*0.80) and punishmentCounter > 0:  # these are the good actions
                # it's balanced in such a way to require more seconds of good actions with respect to the seconds
                # considered from visiting a single good website
                punishmentCounter = punishmentCounter - 1
            if micr[i] > 0 and punishmentCounter == 0:
                result[i] = 1
            else:
                result[i] = 0
            i = i + 1
    else:
        print("Normal study recognized")
        i = 0
        punishmentCounter = 0
        while i < TIME_WINDOW:
            if chair[i] == 0:  # if not sitting, not studying
                result[i] = 0
            else:              # if sitting and ...

                if web[i] == -1:  # check web activity
                    punishmentCounter = MAX_PUNISHMENT  # whenever user visits a forbidden website, then he has
                                                        # to do MAX_PUNISHMENT number of good actions
                elif (web[i] > WEB_TIMEOUT*0.80 or desk[i] > 0) and punishmentCounter > 0:  # these are the good actions
                    # it's balanced in such a way to require more seconds of good actions with respect to the seconds
                    # considered from visiting a single good website
                    punishmentCounter = punishmentCounter - 1

                if punishmentCounter > 0:  # if he has to pay the fee, no points
                    result[i] = 0
                else:                      # otherwise combine the sensors
                    if desk[i] == 1 or web[i] > 0 or micr[i] > 0:     # if writing, speaking or surfing --> ok, studying
                        result[i] = 1
                    else:
                        result[i] = 0

            i = i + 1

    print(result)
    print('Data has been processed')
    print('----------------------------')


def setLast(chair, desk):  # this function takes last values from the data lists and stores them for next loop
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


def update(result):  # Analyzes result and possibly updates the score, recalls user attention or suggests a break

    global standing, distractionsSeries, should_take_a_break, buffer
    # if user came back at their sit, exit from Standing mode:
    if lastChair == 1 and standing:
        standing = False
        print("Exiting from Standing mode")

    # Score part:
    tot = 0
    scoreUpdated = False
    for i in result:  # counts how many seconds have been evaluated as "studying"
        tot = tot + i
    if tot >= TIME_WINDOW/2:  # if at least half of the seconds of the time window were ok, then increment score
        global score
        score = score + 1
        scoreUpdated = True
        print('['+str(score-1)+']->['+str(score)+']')
    else:
        print('[' + str(score) + ']->[' + str(score) + ']')
    print('Score has been updated')

    # Recall user attention if necessary:
    print(pause)
    print("[" + str(distractionsSeries) + "] -> [", end='')
    if ((scoreUpdated == False) and (pause == False)):
        distractionsSeries = distractionsSeries + 1
    else:
        distractionsSeries = 0
    if ((distractionsSeries > SERIES_TRESHOLD) and (pause == False)):
        hlm.alarm()
        warning()
        distractionsSeries = 0
    print(str(distractionsSeries)+"]")
    print("User could have been alarmed")

    # Update buffer and possibly suggest a break:
    if ((len(buffer) >= BUFFER_SIZE) and (pause == False)):
        buffer.pop()  # remove oldest element from the buffer

    if scoreUpdated and (pause == False):
        buffer.insert(0, 1)  # insert new positive outcome in the head of the buffer
    elif pause == False:
        buffer.insert(0, 0)  # insert new negative outcome in the head of the buffer
    else:
        buffer = []
    
    if ((len(buffer) >= BUFFER_SIZE) and (pause == False)):   # only if buffer is full check its status, otherwise we're at the beginning
        tot = 0
        for x in buffer:
            tot = tot + x
        if tot <= BUFFER_SIZE/2:  # if in average the user got distracted too often, maybe it's better to take a break
            should_take_a_break = True
            print("A break has been suggested")
        else:
            should_take_a_break = False
            print("A break hasn't been suggested")
    print(buffer)
    print("Buffer has been updated")
    print('----------------------------')


def updateLight():                  # at each loop cycle the luminosity is checked and, if necessary, light is regulated
    light = zwm.checkLux()
    initialState = hlm.STATE       # just for observing from console: DEBUG variable --> used to print

    if lastChair == 0:             # if they're no more sitting, desk light can be switched off (let's avoid wastes)
        if hlm.ON:
            hlm.turnOff()
    else:
        if light < LUX_THRESHOLD_LOW:  # if light is too low: turn on or, if it's already on, increase brightness
            if hlm.ON:
                hlm.increaseBrightness()
            else:
                hlm.turnOn()
        elif light > LUX_THRESHOLD_HIGH:  # if light too high: decrease brightness if it's high, or turn off otherwise
            if hlm.ON and hlm.STATE == 1:
                hlm.decreaseBrightness()
            elif hlm.ON and hlm.STATE == 0:
                hlm.turnOff()
        else:
            hlm.consistency()

    print("["+str(initialState)+"] -> ["+str(hlm.STATE)+"]")
    print('Lights have been regulated')
    print('----------------------------')


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

        # Set up environment
        db.ClearAll()
        hlm.init()
        # db.init(tm.ChromeCurrentInstant(0))  # JUST FOR TESTING PURPOSES
        # time.sleep(30)  # JUST FOR TESTING PURPOSES

        # Lists initialization
        i = 0
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

            analyze(chair, desk, web, micr, result)

            setLast(chair, desk)

            update(result)

            updateLight()

            time.sleep(TIME_WINDOW)


class writingThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):

        #the actual port on rasp is: /dev/ttyACM0
        ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=10)  # specify serial port and bauderate
        print(ser.name)  # check which port is really used
        while True:
            line = str(ser.read(3))
            # print(line)
            i = line.find("0")
            if i < 0:
                i = line.find("1")
            if i >= 0:
                num = int(line[i:i + 1])
                db.DeskInsert(num)
            time.sleep(1)  # sleep 1 seconds


if __name__ == "__main__":  # this thread will start the other threads and host the web interface

    scoreT = scoreThread()
    scoreT.start()

    writeT = writingThread()
    writeT.start()

    actualIp = socket.gethostbyname(socket.gethostname())
    print(actualIp)

    app.run(host="0.0.0.0", port=8080)
