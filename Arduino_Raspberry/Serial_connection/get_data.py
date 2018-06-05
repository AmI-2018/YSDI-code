# CODE FOR SERIAL COMMUNICATION BETWEEN RASPBERRY AND ARDUINO UNO
import serial,time

ser = serial.Serial(port='COM1', baudrate=9600, timeout=10) # specify serial port and bauderate
print(ser.name)  # check which port is really used

while 1:
        line = str(ser.read(3))
        #print(line)
        i = line.find("0")
        if i<0:
            i = line.find("1")
        if i>=0:
            num = int(line[i:i+1])
            print(num)
        #time.sleep(1)  # sleep 1 seconds

ser.close()  ##Only executes once the loop exits