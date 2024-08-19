import time
import serial
import csv
import requests


# The purpose of this code is to test whether or not the rover can be given instructions from a .csv file



ser = serial.Serial('/dev/ttyS0', 9600)


def execute_command(direction, duration):
    #speed is 120 meters a minute or 2 meters per second
    if direction == "fwd":
        val = int(31)
        command = bytes([val+64])
        command2 = bytes([(val+127+64)])
        #print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration*=(0.5*(100/93)*(3/2.7))
        while(duration >= 0):
            time.sleep(0.01)
            #FM = measure_distance(17,23)
            duration -= 0.01

            #time.sleep(0.1)
            #FR = measure_distance(27,24)
            #duration -= 0.1
            #time.sleep(0.1)
            #FL = measure_distance(4,18)
            #duration -= 0.1
            #if(FM or FR or FL < 30):
            #    ser.write(b'\x00,x00'
        ser.write(b'\x00')
    elif direction == "back":
        val = int((25/100)*127)
        command = bytes([val])
        command2 = bytes([val+127])
        #print(command, command2)
        ser.write(command)
        ser.write(command2)
        while(duration >= 0):
            time.sleep(0.1)
            #BL = measure_distance(B,L)
            duration -= 0.1
            #time.sleep(0.1)
            #BR = measure_distance(B,R)
            #duration -= 0.1
            #if(BL or BR < 30):
            #    ser.write(b'\x00,x00')
        ser.write(b'\x00')
    elif direction == "right":
        val = int((25/100)*127)
        command = bytes([val+1])
        command2 = bytes([val+127+64])
        #print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration = duration*3                                                               *0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            #RF = measure_distance(6,16)
            duration -= 0.01
            #time.sleep(0.1)
            #RB = measure_distance(13,20)
            #duration -= 0.1
            #if(RF or RB < 30):
            #    ser.write(b'\x00')  # Calculate the time it takes to turn right by x degrees
    elif direction == "left":
        val = int((25/100)*127)
        command = bytes([val+64])
        command2 = bytes([val+127+1])
        #print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration = duration*3*0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            #LF = measure_distance(22,25)
            duration -= 0.01
            time.sleep(0.01)
            #LB = measure_distance(5,12)
            duration -= 0.01
            #if(LF or LB < 30):
            #    ser.write(b'\x00,x00')   # Calculate the time it takes to turn left by x degrees
    else:
        print("Invalid direction command: {}".format(direction))
    ser.write(b'\x00')