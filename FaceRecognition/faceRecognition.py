import numpy as np
import cv2 as cv
import time

front_face = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
lateral_face = cv.CascadeClassifier("haarcascade_profileface.xml")
cap = cv.VideoCapture(0)

if __name__ == "__main__":
    print("Starting")
    for i in range(1,10):
        ret, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        fr = front_face.detectMultiScale(gray)
        lat = lateral_face.detectMultiScale(gray)
        if len(fr) != 0 or len(lat) != 0:
            print("Gotcha! %s %s" % (len(fr), len(lat)))
        else:
            print("None.")
        time.sleep(3)
    cap.release()

    foto = cv.imread("foto_laterale.jpg")
    grigia = cv.cvtColor(foto, cv.COLOR_BGR2GRAY)
    fr = front_face.detectMultiScale(grigia)
    lat = lateral_face.detectMultiScale(grigia)
    print("Foto artificiale: ", end="")
    if len(fr) != 0:
        print("centrale! ", end="")
    if len(lat) != 0:
        print("laterale!")
