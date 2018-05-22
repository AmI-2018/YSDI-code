from flask import Flask, request
import json

app = Flask(__name__)
blacklist = ["www.facebook.com", "www.google.it", "www.google.com", "github.com"]
samplingTime = 5 #secondi, intero

def consumeData(visits):
    """
    questa sarà la funzione che si occuperà di mettere i dati nel database o nel buffer circolare, o whatever.
    Ora solo stampa. Sarebbe opportuno che le funzioni a cui farà riferimento siano in un altro modulo ancora
    (quelle del DB per esempio)
    :param visits: lista di coppie time-sito
    :return: void
    """
    print(visits)

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
    consumeData(visits)
    mappa = {"length" : str(len(visits))}
    jSn = json.dumps(mappa)
    return jSn

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)