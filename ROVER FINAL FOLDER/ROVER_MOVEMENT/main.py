from haversine import haversine_with_angle
import time
import serial
import csv
import requests
import re

ser = serial.Serial('/dev/ttyS0', 9600)
gps = serial.Serial('/dev/ttyUSB2', 9600)

def get_GPS():
    command = 'AT\r\n'
    gps.write(command.encode())
    time.sleep(0.1)
    command = 'AT+CGPS=1,1\r\n'
    gps.write(command.encode())
    check = 0
    while check != 'N':
        command = 'AT+CGPSINFO\r\n'
        gps.write(command.encode())
        time.sleep(1)
        GPSDATA = gps.read_all().decode('utf-8')
        output = GPSDATA.split('\n')
        output = output[1]
        match = re.search(r'(\d+)(\d{2}\.\d+),\s*([NS]),\s*(\d+)(\d{2}\.\d+),\s*([EW])', output)
        if match:
            latitude_degrees = int(match.group(1))
            latitude_minutes = float(match.group(2))
            if match.group(3) == 'S':
                latitude_degrees *= -1
            longitude_degrees = int(match.group(4))
            longitude_minutes = float(match.group(5))
            if match.group(6) == 'W':
                longitude_degrees *= -1

    # Convert to proper latitude and longitude format
            latitude = latitude_degrees + latitude_minutes / 60
            longitude = abs(longitude_degrees) + longitude_minutes / 60
            if match.group(6) == 'W':
                longitude = -longitude
            return latitude, longitude

    time.sleep(1)

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
            duration -= 0.01

        ser.write(b'\x00')
    elif direction == "back":
        val = int((25/100)*127)
        command = bytes([val])
        command2 = bytes([val+127])
        ser.write(command)
        ser.write(command2)
        while(duration >= 0):
            time.sleep(0.1)
            duration -= 0.1

        ser.write(b'\x00')
    elif direction == "right":
        val = int((25/100)*127)
        command = bytes([val+1])
        command2 = bytes([val+127+64])
        ser.write(command)
        ser.write(command2)
        duration = duration*3                                                               *0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            duration -= 0.01
    elif direction == "left":
        val = int((25/100)*127)
        command = bytes([val+64])
        command2 = bytes([val+127+1])
        ser.write(command)
        ser.write(command2)
        duration = duration*3*0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            duration -= 0.01
            time.sleep(0.01)
            duration -= 0.01
    else:
        print("Invalid direction command: {}".format(direction))
    ser.write(b'\x00')










prev0, prev1 =  get_GPS()
print("initial calibration")
print("current GPS: ", prev0, prev1)
time.sleep(3)
execute_command("fwd", 3)
print("moving forward for calibration")
time.sleep(3)
curr0, curr1 = get_GPS()
print("current GPS: ", prev0, prev1)
current_angle = 0
#calibrate for initial current angle from true north
distance_meters, angle_from_north, angle_difference = haversine_with_angle(prev0, prev1, curr0, curr1, current_angle)
print(f"distance: {distance_meters}, Angle from north: {angle_from_north}, angle difference: {angle_difference}")
current_angle = angle_from_north
with open('nodes.csv', mode = 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter = ' ')
    for row in reader:
        destination_lat = float(row[0])
        destination_lon = float(row[1])
        print("getting first node: ", destination_lat, destination_lon)
        print("destination: ", destination_lat," ", destination_lon)
        distance_meters, angle_from_north, angle_difference = haversine_with_angle(curr0, curr1, destination_lat, destination_lon, current_angle)
        print("distance: ",distance_meters, " angle from north: ", angle_from_north, " current diff: ", angle_difference)
        while(distance_meters > 0.25):
            #curr = get_GPS()
            distance_meters, angle_from_north, angle_difference = haversine_with_angle(curr0, curr1, destination_lat, destination_lon, current_angle)
            if(angle_difference > 3):
                execute_command("right", angle_difference)
                print(f"turning right {angle_difference} degrees")
                curr_angle = angle_from_north
                current_angle = angle_from_north

            if(angle_difference < -3):
                execute_command("left", angle_difference)
                print(f"turning left {angle_difference*-1} degrees")
                current_angle = angle_from_north
                curr_angle = angle_from_north
            execute_command("fwd", 0.25)

        curr0, curr1 = get_GPS() 

        
            

gps.close()
ser.close()
