import time
import serial
import requests
import numpy as np
import RPi.GPIO as GPIO


####setup of all needed ports + connection configuration
ser = serial.Serial('/dev/ttyS0', 9600)
GPIO.setmode(GPIO.BOARD)

# Trigger (Out)
GPIO.setup(3,  GPIO.OUT)# L2
GPIO.setup(11, GPIO.OUT)# L1
GPIO.setup(19, GPIO.OUT)# M
GPIO.setup(29, GPIO.OUT)# R1
GPIO.setup(33, GPIO.OUT)# R2

# Echo (In)
GPIO.setup(5,  GPIO.IN)# L2
GPIO.setup(13, GPIO.IN)# L1
GPIO.setup(21, GPIO.IN)# M
GPIO.setup(31, GPIO.IN)# R1
GPIO.setup(35, GPIO.IN)# R2

def execute_command(direction, duration, ser):
    #speed is 120 meters a minute or 2 meters per second
    if direction == "fwd":
        val = int(7)
        command = bytes([val+64])
        command2 = bytes([(val+127+64)])
        #print(command, command2)
        ser.write(command)
        ser.write(command2)
        duration*=(0.5*(100/93)*(3/2.7))
        print("moving forward")
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
        print("turning right")
        val = int((25/100)*127)
        command = bytes([val+1])
        command2 = bytes([val+127+64])
        ser.write(command)
        ser.write(command2)
        duration = duration*3 *0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            duration -= 0.01
    elif direction == "left":
        print("turning left")
        val = int((25/100)*127)
        command = bytes([val+64])
        command2 = bytes([val+127+1])
        ser.write(command)
        ser.write(command2)
        duration = duration*3*0.0088*(90/106.7)*(90/96.6)
        while(duration >= 0):
            time.sleep(0.01)
            duration -= 0.01
    else:
        print("Invalid direction command: {}".format(direction))
    ser.write(b'\x00')

def measure_distance(TRIG_PIN, ECHO_PIN):
    # send a pulse to the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # measure the time it takes for the pulse to bounce back
    start_time = time.time()
    pulse_start = time.time()
    pulse_end = time.time()
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
    distance = pulse_duration * 16880.486
    distance = round(distance, 2)

    return distance


def get_sensor_readings():
    """Acquire the sensor distance data and return as a list"""
    # this wont take parameters since the sensor readings will be done by actual hardware and corresponding func calls
    L2 = measure_distance(33, 35)  # was L2 (3, 5)
    time.sleep(0.1)

    L1 = measure_distance(11, 13)
    time.sleep(0.1)

    M = measure_distance(19, 21)
    time.sleep(0.1)

    R1 = measure_distance(29, 31)
    time.sleep(0.1)

    R2 = measure_distance(3, 5)  # was R2 (33, 35)
    time.sleep(0.1)
    print(f"L2: {L2}, L1: {L1}, M: {M}, R1: {R1}, R2: {R2}")
    return np.array([L2, L1, M, R1, R2])


def case_processing():
    """Perform weight multiplication and summation for each case (c1, c2, ...) and return as a list"""
    # actual function wont have parameters, this is for testing
    distance_arr = get_sensor_readings()  # actual func call wont have parameters

    # weight coefficients
    # w1, w2, w3, w4, w5 = 1, 2, 3, 4, 5  # weights are lightest to heaviest
    w1, w2, w3, w4, w5 = 100, 50, 20, 10, 1  # weights are heaviest to lightest

    # the comment by each weight is the order of sensors from most to least impactful for each case
    # the most impactful will have the most effect and will most likely have the smallest distance measurement
    # the idea is that the minimum of the cases is chosen as the current case

    # New weights format (SEEMS TO WORK)
    #            L2  L1  M   R1  R2
    c1weights = [w5, w5, w3, w1, w2]  # R1, M, R2, L1, L2 ; GOOD
    c2weights = [w5, w4, w3, w3, w1]  # R2, R1, M, L1, L2
    c3weights = [w2, w4, w5, w4, w2]  # M, (L1/R1), (L2/R2)
    c4weights = [w1, w3, w3, w4, w5]  # L2, L1, M, R1, R2
    c5weights = [w2, w1, w3, w5, w5]  # L1, M, L2, R1, R2 ; GOOD

    # weight vector multiplication
    c1 = np.sum(np.multiply(distance_arr, c1weights))  # hard left
    c2 = np.sum(np.multiply(distance_arr, c2weights))  # left
    c3 = np.sum(np.multiply(distance_arr, c3weights))  # straight
    c4 = np.sum(np.multiply(distance_arr, c4weights))  # right
    c5 = np.sum(np.multiply(distance_arr, c5weights))  # hard right

    print('The cases values are:', [c1, c2, c3, c4, c5])
    return [c1, c2, c3, c4, c5]


def case_classification():
    """Case classifier to determine which direction is best based on "path of least resistance" or minimum case value"""
    case_list = case_processing()  # actual func call wont have parameters. returns c list

    casename_dictionary = {0: 'c1', 1: 'c2', 2: 'c3', 3: 'c4', 4: 'c5'}
    min_val = min(case_list)  # find the min in case list, was min switched to max
    idx_of_min_val = case_list.index(min_val)
    casename = casename_dictionary[idx_of_min_val]
    print('the case determined is:', casename)

    casetype_dictionary = {'c1': 'hard left', 'c2': 'left', 'c3': 'straight', 'c4': 'right', 'c5': 'hard right'}
    casetype = casetype_dictionary[casename]
    print('the case type is:', casetype)

    return casetype


def obstacle_avoidance():
    """Sub routine triggered by nearby obstacle(s), determines navigation for obstacle avoidance and returns movement"""
    case_class = case_classification()  # actual func call wont have parameters
    return case_class
