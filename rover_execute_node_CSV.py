import time
import serial
import csv
import math

# The purpose of this code is to test whether or not the rover can be given instructions from a .csv file



ser = serial.Serial('/dev/serial0', 9600)

    
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT)#front left
#GPIO.setup(17, GPIO.OUT)#front middle
#GPIO.setup(27, GPIO.OUT)#front right
#GPIO.setup(22, GPIO.OUT)#left front
#GPIO.setup(5, GPIO.OUT)#left back
#GPIO.setup(6, GPIO.OUT)#right front
#GPIO.setup(13, GPIO.OUT)#right back
#GPIO.setup(19, GPIO.OUT)#back middle

#GPIO.setup(18, GPIO.IN)#Front left
#GPIO.setup(23, GPIO.IN)#front Middle
#GPIO.setup(24, GPIO.IN)#Front Right
#GPIO.setup(25, GPIO.IN)#Left Front
#GPIO.setup(12, GPIO.IN)#Left Back
#GPIO.setup(16, GPIO.IN)#Right Front
#GPIO.setup(20, GPIO.IN)#Right Back
#GPIO.setup(21, GPIO.IN)#Back middle

def get_location():
    url = 'https://ipapi.co/json/'
    response = requests.get(url)
    data = response.json()

    x[0] = data.get('latitude', 'N/A')
    x[1] = data.get('longitude', 'N/A')

    return x

def measure_distance(TRIG_PIN, ECHO_PIN):
    # send a pulse to the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # measure the time it takes for the pulse to bounce back
    start_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        if time.time() - start_time > 0.1:
            return -1
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        if time.time() - start_time > 0.1:
            return -1
        pulse_end = time.time()

    # calculate distance in inches
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 13503.9
    distance = round(distance, 2)

    return distance

ser = serial.Serial('/dev/serial0', 9600)


###Object avoidance code, work more on this
def avoidF(FL, ML, MR, FR):
    FL = measure_distance(F, L)
    ML = measure_distance(M, L)
    MR = measure_distance(M, R)
    FR = measure_distance(F, R)
    LF = measure_distance(L, F)
    LB = measure_distance(L, B)
    RF = measure_distance(R, F)
    RB = measure_distance(R, B)
    if(FL < 50 and ML < 50 and MR < 50 and FR < 50):
      #cant go at an angle
    if(FL < 50 and ML < 50 and MR < 50 and not (FR < 50)):
        #large right
    if(FL < 50 and ML < 50 and not (MR < 50) and not (FR < 50)):
        #medium turn right
    if(FL < 50 and not (ML < 50) and not (MR < 50) and not (FR < 50)):
        #small right
    if((FL > 50) and (ML < 50) and (MR < 50) and (FR < 50)):
        #large left
    if((FL > 50) and not (ML < 50) and (MR < 50) and (FR < 50)):
        #medium left
    if((FL > 50) and not (ML < 50) and not (MR < 50) and (FR < 50)):
        #small left
        
    
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




def calibrated_angle_from_north(point1, point2):
    # Calculate the difference in longitude (east-west direction)
    delta_longitude = point2[1] - point1[1]

    # Calculate the difference in latitude (north-south direction)
    delta_latitude = point2[0] - point1[0]

    # Calculate the angle in radians using arctan2
    angle_radians = math.atan2(delta_longitude, delta_latitude)

    # Convert the angle from radians to degrees
    angle_degrees = math.degrees(angle_radians)

    # Ensure the angle is between 0 and 360 degrees
    calibrated_angle = (angle_degrees + 360) % 360

    return calibrated_angle
#Open the CSV file and read each line
def calibrate():
    x = get_location()
    execute_command(fwd, 5)
    y = get_location()
    angle = calibrated_angle_from_north(x,y)
    return angle
def adjust_angle(point1, point2, prev_angle):
    delta_longitude = point2[1] - point1[1]

    # Calculate the difference in latitude (north-south direction)
    delta_latitude = point2[0] - point1[0]

    # Calculate the angle in radians using arctan2
    angle_radians = math.atan2(delta_longitude, delta_latitude)

    # Convert the angle from radians to degrees
    angle_degrees = math.degrees(angle_radians)

    # Ensure the angle is between 0 and 360 degrees
    calibrated_angle = (angle_degrees + 360) % 360

    calibrated_angle -= prev_angle

    return calibrated_angle

def calculate_distance(point1, point2):
    if len(point1) != 2 or len(point2) != 2:
        raise ValueError("Both input arrays should have exactly 2 elements (x and y coordinates).")

    x1, y1 = point1
    x2, y2 = point2

    # Calculate the squared differences of x and y coordinates
    x_diff_squared = (x2 - x1) ** 2
    y_diff_squared = (y2 - y1) ** 2

    # Calculate the sum of squared differences
    sum_of_squared_diff = x_diff_squared + y_diff_squared

    # Calculate the square root to get the distance
    distance = math.sqrt(sum_of_squared_diff)

    return distance

with open('nodes.csv') as csvfile:
       reader = csv.reader(csvfile)
       angle = calibrate()
       for row in reader:
           current_location = get_location()
           next_node[0] = row[0]
           next_node[1] = int(row[1])
           distance = calculate_distance(current_location, next_node)
           new_angle = adjust_angle(current_location, next_node, angle)
           if(angle < 0):
               turn = "left"
           else(angle > 0):
               turn = "right"
           execute_command(turn, new_angle)
           execute_command(fwd, distance)
           ser.write(b'\x00')
           current_location = get_location()
           while (next_node != current_location):
               distance = calculate_distance(current_location, next_node)
               new_angle = adjust_angle(current_location, next_node, angle)
               if(angle < 0):
                   turn = "left"
               else(angle > 0):
                   turn = "right"
               execute_command(turn, new_angle)
               execute_command(fwd, distance)
               
           #write verification to ensure that rover is within 1 to 2 meters of the designated node#

# Stop the motors and close the serial connection
##ser.write(b'\x02\x0A\x02\xB4')
##ser.write(b'\x00\x64')#motors run in opposite directions
##ser.write(b'\x7F\xE3')#both forward
##ser.write(b'\x01\x00\x32\x00')##backwards
##ser.write(b'\x01\x00\x10\x00')
##time.sleep(3)
ser.write(b'\x00\x00')#stop
ser.close()


