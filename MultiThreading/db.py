import time, sqlite3
import TimeManagement as tm
import os.path
import microphone as mic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "YSDIdb")


def ClearAll():
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


def MicInsert(instant):  # must added the value parameter
    #instant = int(tm.ChromeCurrentInstant(0)) - mic.RECORD_SECONDS*1000000
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """INSERT INTO microphone
            VALUES (?)
      """
    cur.execute(sql, (instant,))
    connection.commit()
    connection.close()


def HistoryInsert(visits):
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
def HistoryCount():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT COUNT(*)
            FROM history;
                """
    cur.execute(sql)
    tupla = cur.fetchone()
    connection.close()
    return int(tupla[0])
def MicCount():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    sql = """SELECT COUNT(*)
                FROM microphone;
                    """
    cur.execute(sql)
    tupla = cur.fetchone()
    connection.close()
    return int(tupla[0])
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
                 WHERE (?-ChromeTimestamp)<= ?;
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
                 WHERE (?-ChromeTimestamp)<= ?;
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
             WHERE (?-ChromeTimestamp)<= ?;
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
             WHERE (?-ChromeTimestamp)<= ?;
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
    cur.execute(sql, (now + 1000000,))

    # mic:
    sql = """INSERT INTO microphone
                VALUES (?)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO microphone
                    VALUES (?)"""
    cur.execute(sql, (now + 1000000,))

    # desk:
    sql = """INSERT INTO desk
                    VALUES (?,0)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO desk
                        VALUES (?,1)"""
    cur.execute(sql, (now + 3000000,))
    sql = """INSERT INTO desk
                 VALUES (?,1)"""
    cur.execute(sql, (now + 5000000,))

    # hist:
    sql = """INSERT INTO history
                    VALUES (?,1)"""
    cur.execute(sql, (now,))
    sql = """INSERT INTO history
                        VALUES (?,0)"""
    cur.execute(sql, (now + 3000000,))
    sql = """INSERT INTO history
                 VALUES (?,1)"""
    cur.execute(sql, (now + 5000000,))

    connection.commit()
    connection.close()
