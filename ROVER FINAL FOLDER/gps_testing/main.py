from haversine import haversine_with_angle
from GPS import get_GPS
from movement import execute_command
import time
import serial
import csv
import requests


ser = serial.Serial('/dev/ttyS0', 9600)
gps = serial.Serial('/dev/ttyUSB2', 9600)
prev = get_GPS()
execute_command(fwd, 3)
curr = get_GPS()
current_angle = 0
#calibrate for initial current angle from true north
distance_meters, angle_from_north, angle_difference = haversine_with_angle(prev[0], prev[1], curr[0], curr[1], current_angle)

with open('nodes.csv') as csvfile:
    reader = csv.reader(csvfile):
    for row in reader:
        destination_lat = row[0]
        destination_lon = row[1]
        while(distance_meters > 0.25):
            curr = get_GPS()
            distance_meters, angle_from_north, angle_difference = haversine_with_angle(current_location[0], current_location[1], destination[0], destination[1], current_angle)
            if(angle_difference > 3):
                execute_command(right, angle_difference)
                angle_difference = 0
            if(angle_difference < -3):
                execute_command(left, angle_difference)
                angle_difference = 0
            execute_command(fwd, 0.25)
            

gps.close()
ser.close()
