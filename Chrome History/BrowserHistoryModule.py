from flask import jsonify
import os, getpass, sqlite3
import requests
import json
from shutil import copyfile
import datetime, time

#questo sarà l'url dove starà eseguendo l'API di YSDI sulla raspberry
base_url = ""

def delta():
    ora1 = datetime.datetime.strptime("01-01-1970 00:00", "%d-%m-%Y %H:%M")
    ora2 = datetime.datetime.strptime("01-01-1601 00:00", "%d-%m-%Y %H:%M")
    rit = ora1 - ora2
    return rit

def ChromeTimeToDatetime(timestamp):
    """
    Converte il timestamp della history in un dato di tipo datetime
    :param timestamp: prende il timestamp nel formato di chrome, cioè che parte dal 01-01-1601 alle 00:00 in microsecondi
    :return: dato in formato datetime, cioè che parte dal 01-01-1970 alle 00:00
    """
    detected = datetime.datetime.fromtimestamp(timestamp / 1e6)
    detected = detected - delta()
    return detected

def ChromeCurrentInstant(secondi_indietro):
    """
    Corrente a meno del valore di secondi precedenti in cui guardare l'accaduto.
    Per l'esatto istante corrente, usare secondi_indietro=0.
    :return: istante corrente - secondi_indietro
    """
    seconds = time.mktime(datetime.datetime.now().timetuple()) + (delta().days * 86400) - secondi_indietro
    micros = int(seconds * 1e6)
    return micros

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

if __name__ == '__main__':
    #capire come trovare un percorso valido per tutti. Per me purtroppo è questo, e non mi va il metodo trovato sul sito
    path = "C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    database = os.path.join(path, "History")
    esaminato = os.path.join(path, "YSDI-check")

    #recupera il tempo in cui deve dormire, prima di inviare le analisi più recenti: 10s? E gli facciamo controllare l'history dei 15 precedenti?
    mappa = requests.get(base_url + "/constants/historySamplingTime")
    Ts = int(mappa["value"]) #numero di secondi

    #recupera la blacklist, definita sulla raspberry
    mappa = requests.get(base_url + "/constants/blacklist")
    blacklist = mappa["list"]
    #la blacklist contiene cose con il classico formato di sito semplificato, tipo:
    # www.google.it, www.facebook.com, etc etc.
    #viene verificato in automatico se negli url analizzati ci sono questi come sottostringhe


    #da qui ci dovrà essere un ciclo che ogni tot ricontrolla la browser history. Ho notato che
    #c'è qualche secondo di delay comunque fra quando visito una pagina e quando viene scritta nella browser history
    #quindi magari fare un controllo ogni 10s al massimo

    copyfile(database, esaminato)  # così, sennò non viene lasciato l'accesso mentre chrome è aperto
    connection = sqlite3.connect(esaminato)
    cursore = connection.cursor()
    sql = """
    SELECT url, last_visit_time
    FROM urls
    WHERE last_visit_time > ?
    """
    cursore.execute(sql , (ChromeCurrentInstant(60), ) )
    risultati = cursore.fetchall()

    lista = []
    for tupla in risultati:
        istante = ChromeTimeToDatetime(tupla[1])
        controllo = checkBlacklist(blacklist, tupla[0])
        if controllo != -1:
            lista.append({"host": blacklist[controllo], "datetime": istante})

    toShip = {"pairsHostTime": lista}
    requests.post(base_url + "/historyReadings", json=jsonify(toShip))

    connection.close()

#qui finirà il ciclo