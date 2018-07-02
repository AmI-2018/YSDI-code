"""
@author: Edoardo Calvi                  --> insertions in the database + tweaks on the readings
@author: Matteo Garbarino               --> readings from the database + tweaks on the insertions
This module interfaces with the sqlite3 database.
"""

import time, sqlite3
import TimeManagement as tm
# import os.path                                            # !!!

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # !!!
# db_path = os.path.join(BASE_DIR, "YSDIdb")                # this works on PCs, but not on the raspberry
# test per rasp
db_path = "/home/pi/Desktop/MultiThreading/YSDIdb"  # TO BE UPDATED WITH NEW FOLDER NAME
                                                    # ONCE THE FILES WILL BE PUT ON THE RASPBERRY !!!


def ClearAll():
    """
    Reset previous data and empty the database.
    :return: /
    """
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT name
            FROM sqlite_master
            WHERE type="table"
          """
    cur.execute(sql)
    tables = cur.fetchall()
    sql = """DELETE FROM {}"""
    for tupla in tables:
        cur.execute(sql.format(tupla[0]))
    connection.commit()
    connection.close()


def MicInsert(instant):
    """
    Insertion of the timestamp of the start of recording.
    :param instant: timestamp
    :return: /
    """
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """INSERT INTO microphone
            VALUES (?)
      """
    cur.execute(sql, (instant,))
    connection.commit()
    connection.close()


def HistoryInsert(visits):
    """
    Insertion of the visited websites coupled with the info about if they are allowed.
    :param visits: list of couples [instant, allowed]
    :return: /
    """
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """INSERT INTO history
              VALUES (?,?)
            """
    for coppia in visits:
        instant = coppia[0]
        if coppia[1]:
            cur.execute(sql, (instant, 1))
        else:
            cur.execute(sql, (instant, 0))
    connection.commit()
    connection.close()


def ChairInsert(sitting):
    """
    Insertion of the current chair value. The timestamp is taken here, on receiver side, because it's sent from Arduino.
    :param sitting: whether the user is currently sitting
    :return: /
    """
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """INSERT INTO chair (ChromeTimestamp, sitting)
          VALUES (?,?);
    """
    instant = tm.ChromeCurrentInstant(0)
    cur.execute(sql, (instant, sitting))
    connection.commit()
    connection.close()
    return


def DeskInsert(moving):
    """
    Insertion of data about the writing desk. The timestamp is taken here because it's sent from Arduino.
    :param moving: whether variations on the load cell were detected
    :return: /
    """
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """INSERT INTO desk (ChromeTimestamp, moving)
          VALUES (?,?);
    """
    instant = tm.ChromeCurrentInstant(0)
    cur.execute(sql, (instant, moving))
    connection.commit()
    connection.close()
    return


# The following functions before the # are for the debugging window
def DeskLast5():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """
    SELECT moving
    FROM desk
    WHERE ChromeTimestamp > ?
    ORDER BY ChromeTimestamp DESC;
    """
    cur.execute(sql, (tm.ChromeCurrentInstant(10),))
    strng = ""
    for i in range(0,5):
        tupla = cur.fetchone()
        if tupla is None:
            strng = strng + "0"
        else:
            strng = strng + str(tupla[0])
    connection.close()
    return strng
def HistoryLast():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT ChromeTimestamp
            FROM history
            ORDER BY 1 DESC;
                """
    cur.execute(sql)
    tupla = cur.fetchone()
    connection.close()
    if tupla is None:
        return "None"
    return str(tupla[0])
def MicLast():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT *
                FROM microphone
                ORDER BY ChromeTimestamp DESC;
                    """
    cur.execute(sql)
    tupla = cur.fetchone()
    if tupla is None:
        return "None"
    inizio = tupla[0]
    fine = inizio + 5e6
    string = str(inizio) + " :: " + str(fine)
    connection.close()
    return string
def getLastSit():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT sitting
             FROM chair
             ORDER BY ChromeTimestamp DESC;
                        """
    cur.execute(sql)
    tupla = cur.fetchone()
    connection.close()
    if tupla is None:
        return 0
    return tupla[0]
#


# Useful functions:
def getHist(Trange, now):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()

    sql = """SELECT *
                 FROM history
                 WHERE (?-ChromeTimestamp)< ?;
                            """
    cur.execute(sql, (now, Trange))
    tupla = list(cur.fetchall())
    connection.close()
    return tupla


def getDesk(Trange, now):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()

    sql = """SELECT *
                 FROM desk
                 WHERE (?-ChromeTimestamp)< ?;
                            """
    cur.execute(sql, (now, Trange))
    tupla = list(cur.fetchall())
    connection.close()
    return tupla


def getMic(Trange, now):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()

    sql = """SELECT *
             FROM microphone
             WHERE (?-ChromeTimestamp)< ?;
                        """
    cur.execute(sql, (now, Trange))
    tupla = list(cur.fetchall())
    connection.close()
    return tupla


def getSit(Trange, now):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()

    sql = """SELECT *
             FROM chair
             WHERE (?-ChromeTimestamp)< ?;
                        """
    cur.execute(sql, (now, Trange))
    tupla = list(cur.fetchall())
    connection.close()
    return tupla


def init(now):  # just for testing
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()

    # chair:
    sql = """INSERT INTO chair
                VALUES (?,0)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO chair
                    VALUES (?,1)"""
    cur.execute(sql, (now + 1100000,))
    sql = """INSERT INTO chair
                    VALUES (?,0)"""
    cur.execute(sql, (now+5000000,))
    sql = """INSERT INTO chair
                        VALUES (?,1)"""
    cur.execute(sql, (now + 10000000,))

    # desk:
    sql = """INSERT INTO desk
                    VALUES (?,0)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO desk
                        VALUES (?,1)"""
    cur.execute(sql, (now + 3000000,))
    sql = """INSERT INTO desk
                 VALUES (?,0)"""
    cur.execute(sql, (now + 5000000,))

    # hist:
    sql = """INSERT INTO history
                    VALUES (?,1)"""
    cur.execute(sql, (now+1100000,))
    sql = """INSERT INTO history
                        VALUES (?,0)"""
    cur.execute(sql, (now + 3000000,))
    sql = """INSERT INTO history
                 VALUES (?,1)"""
    cur.execute(sql, (now + 5000000,))

    # mic:
    sql = """INSERT INTO microphone
                    VALUES (?)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO microphone
                            VALUES (?)"""
    cur.execute(sql, (now + 1100000,))
    sql = """INSERT INTO microphone
                                VALUES (?)"""
    cur.execute(sql, (now + 2000000,))
    sql = """INSERT INTO microphone
                        VALUES (?)"""
    cur.execute(sql, (now + 27000000,))
    sql = """INSERT INTO microphone
                            VALUES (?)"""
    cur.execute(sql, (now + 29999999,))

    connection.commit()
    connection.close()
