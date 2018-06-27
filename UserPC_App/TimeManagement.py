"""
@author: Edoardo Calvi

This file contains useful functions that are called in the main modules of the project:
it handles the chrome time-format, which is tricky because not standard, but also easy to manipulate
because it's just an integer.
It's the same file in both MultiThreading and UserPC_App.
"""

import datetime
import time


def delta():
    """
    :return: fixed time interval between the Chrome time format and the standard one
    """
    ora1 = datetime.datetime.strptime("01-01-1970 00:00", "%d-%m-%Y %H:%M")
    ora2 = datetime.datetime.strptime("01-01-1601 00:00", "%d-%m-%Y %H:%M")
    rit = ora1 - ora2
    return rit


def ChromeTimeToDatetime(timestamp):
    """
    Converts a chrome timestamp into a readable format.
    :param timestamp: in the chrome format, starting from 01-01-1601 at 00:00, in microseconds
    :return: data in datetime format, starting from 01-01-1970 at 00:00
    """
    detected = datetime.datetime.fromtimestamp(timestamp / 1e6)
    detected = detected - delta()
    return detected


def ChromeCurrentInstant(secondi_indietro):
    """
    Current instant in time format, minus a number of seconds behind: this serves for comparisons
    with stored timestamps when we want only the ones within a certain interval.
    For the current instant, call the function with secondi_indietro=0.
    :return: current instant - secondi_indietro (chrome format)
    """
    seconds = time.mktime(datetime.datetime.now().timetuple()) + (delta().days * 86400) - secondi_indietro
    micros = int(seconds * 1e6)
    return micros


def DatetimeCurrentInstant():
    """
    Wrapper utility function
    :return: current instant in readable format
    """
    return str(datetime.datetime.now())

