import time
import serial
import csv


# The purpose of this code is to test whether or not the rover can be given instructions from a .csv file



ser = serial.Serial('/dev/serial0', 2400)

# Define a function to execute motor commands based on direction and time
def execute_command(direction, duration):

    if direction == "fwd":
        val = int((25/100)*127)
        command = bytes([val+64])
        command2 = bytes([val+127+64])
        print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration*=0.5
        while(duration >= 0):
            time.sleep(0.1)
            #FM = measure_distance(17,23)
            duration -= 0.1
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
        print(command, command2)
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
        command = bytes([val])
        command2 = bytes([val+127+64])
        print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration = duration*0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.1)
            #RF = measure_distance(6,16)
            duration -= 0.1
            #time.sleep(0.1)
            #RB = measure_distance(13,20)
            #duration -= 0.1
            #if(RF or RB < 30):
            #    ser.write(b'\x00')  # Calculate the time it takes to turn right by x degrees
    elif direction == "left":
        val = int((25/100)*127)
        command = bytes([val+64])
        command2 = bytes([val+127])
        print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration = duration*0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.1)
            #LF = measure_distance(22,25)
            duration -= 0.1
            time.sleep(0.1)
            #LB = measure_distance(5,12)
            duration -= 0.1
            #if(LF or LB < 30):
            #    ser.write(b'\x00,x00')   # Calculate the time it takes to turn left by x degrees
    else:
        print("Invalid direction command: {}".format(direction))
    ser.write(b'\x00')
#Open the CSV file and read each line
with open('instruction.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        direc = row[0]
        durat = int(row[1])
        execute_command(direc, durat)
        ser.write(b'\x00\x00')
        time.sleep(1)

# Stop the motors and close the serial connection
##ser.write(b'\x02\x0A\x02\xB4')
##ser.write(b'\x00\x64')#motors run in opposite directions
##ser.write(b'\x7F\xE3')#both forward
##ser.write(b'\x01\x00\x32\x00')##backwards
##ser.write(b'\x01\x00\x10\x00')
##time.sleep(3)
ser.write(b'\x00\x00')#stop
ser.close()


