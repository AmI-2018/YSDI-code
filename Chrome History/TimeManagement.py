import datetime, time

def delta():
    """
    :return: intervallo di tempo fisso che intercorre fra il formato standard e quello di chrome
    """
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

def DatetimeCurrentInstant():
    return str(datetime.datetime.now())
