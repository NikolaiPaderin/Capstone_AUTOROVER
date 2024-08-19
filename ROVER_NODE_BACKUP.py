import time
import serial
import csv
import math

# The purpose of this code is to test whether or not the rover can be given instructions from a .csv file



ser = serial.Serial('/dev/serial0', 9600)

    
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)#front left
GPIO.setup(17, GPIO.OUT)#front middle
GPIO.setup(27, GPIO.OUT)#front right
GPIO.setup(22, GPIO.OUT)#left front
GPIO.setup(5, GPIO.OUT)#left back
GPIO.setup(6, GPIO.OUT)#right front
GPIO.setup(13, GPIO.OUT)#right back
GPIO.setup(19, GPIO.OUT)#back middle

GPIO.setup(18, GPIO.IN)#Front left
GPIO.setup(23, GPIO.IN)#front Middle
GPIO.setup(24, GPIO.IN)#Front Right
GPIO.setup(25, GPIO.IN)#Left Front
GPIO.setup(12, GPIO.IN)#Left Back
GPIO.setup(16, GPIO.IN)#Right Front
GPIO.setup(20, GPIO.IN)#Right Back
GPIO.setup(21, GPIO.IN)#Back middle

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

#ser = serial.Serial('/dev/serial0', 9600)


###Object avoidance code, work more on this
def avoidF(FL, ML, MM, MR, FR, angle):
  """Sub routine triggered by nearby obstacle(s), determines navigation for obstacle avoidance"""
  FL = measure_distance(F, L)
  ML = measure_distance(M, L)
  MR = measure_distance(M, R)
  M = measure_distance(M, M)
  FR = measure_distance(F, R)
  L = measure_distance(L, F)
  R = measure_distance(R, F)

  # weights for direction 
  left_weight = 0
  right_weight = 0

  # keep track of amount of times direction changed, use for repositioning
  # positive for right, negative for left, 0 for no change
  # last value after OA routine is what is leveraged
  dir_change = 0

  # read sensor distances to get positional weights of object relative to rover
  if FL <= 50:
    left_weight += 1
  if ML <= 50:
    left_weight += 1
  if M <= 50:
    left_weight += 1
    right_weight+= 1
  if MR <= 50:
    right_weight += 1
  if FR <= 50: 
    right_weight += 1

  # control logic for movement based on weights
  if(right_weight < left_weight): # right movement
    while(FL <= 50):
      execute_command('right', 5)
      dir_change += 1
      FL = measure_distance(F, L)
      
  if(left_weight < right_weight): # left movement
    while(FR <= 50):
      execute_command('left', 5)
      dir_change -= 1
      FR = measure_distance(F, R)
      
  if(right_weight == left_weight): # equal weights
    if(L > R): # turn right
      while(FL <= 50):
        execute_command('right', 5)
        dir_change += 1
        FL = measure_distance(F, L)
    else: # turn left
      while(FR <= 50):
        execute_command('left', 5)
        dir_change -= 1
        FR = measure_distance(F, R)
        
  if(R > L): # turn left
    while(FR <= 50):
     execute_command('left', 5)
     dir_change -= 1
     FR = measure_distance(F, R)

  #move forward until obj cannot be seen by left or right sensor(might need to change so its in 2 if statements instead of 1 while loop
  while(L < 50 or R < 50):
    execute_command('fwd', 0.5)
    L = measure_distance(L,L)
    R = measure_distance(R,R)

  #adjust angle for parallel path
  if(dir_change < 0):
    adjust = dir_change*(-1)
    execute_command('right', 5*adjust)
  if(dir_change > 0):
    execute_command('left', 5*dir_change)

  #move forward until either left or right depending on dir can no longer detect obj
  if(dir_change < 0):
    while(R < 50):
      execute_command('fwd', 0.1)
      R = measure_distance(R, R)
  if(dir_change > 0):
    while(L < 50):
      execute_command('fwd',0.1)
      L = measure_distance(L, L)

  #pivot for moving back to main path
  if(dir_change < 0):
    adjust = dir_change*(-1)
    execute_command('right', 5*adjust)
  if(dir_change > 0):
    execute_command('left', 5*dir_change)

  #move forward until left and right side no longer detect object
  while(L < 50 and R < 50):
    execute_command('fwd', 0.5)
    L = measure_distance(L,L)
    R = measure_distance(R,R)

  #final turn for course correction
  if(dir_change < 0):
    adjust = dir_change*(-1)
    execute_command('left', 5*adjust)
  if(dir_change > 0):
    execute_command('right', 5*dir_change)
  angle = calibrate()
      

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
        ser.write(b'\x00')  # Calculate the time it takes to turn right by x degrees
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
        ser.write(b'\x00,x00')   # Calculate the time it takes to turn left by x degrees
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
    execute_command('fwd', 5)
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
##time.sleep(3)
ser.write(b'\x00\x00')#stop
ser.close()
