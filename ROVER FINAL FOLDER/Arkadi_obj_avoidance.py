import numpy as np


def get_sensor_readings(L2, L1, M, R1, R2):
    """Acquire the sensor distance data and return as a list"""
    # this wont take parameters since the sensor readings will be done by actual hardware and corresponding func calls
    # L2 = readL2
    # L1 = readL1
    # M = readM
    # R1 = readR1
    # R2 = readR2
    return np.array([L2, L1, M, R1, R2])


def case_processing(L2, L1, M, R1, R2):
    """Perform weight multiplication and summation for each case (c1, c2, ...) and return as a list"""
    # actual function wont have parameters, this is for testing
    distance_arr = get_sensor_readings(L2, L1, M, R1, R2)  # actual func call wont have parameters

    # weight coefficients
    # w1, w2, w3, w4, w5 = 1, 2, 3, 4, 5  # weights are lightest to heaviest
    w1, w2, w3, w4, w5 = 100, 50, 20, 10, 1  # weights are heaviest to lightest

    # the comment by each weight is the order of sensors from most to least impactful for each case
    # the most impactful will have the most effect and will most likely have the smallest distance measurement
    # the idea is that the minimum of the cases is chosen as the current case

    # Original weight format
    #            L2  L1  M   R1  R2
    # c1weights = [w4, w5, w2, w1, w3]  # R1, M, R2, L1, L2
    # c2weights = [w5, w4, w3, w2, w1]  # R2, R1, M, L1, L2
    # c3weights = [w4, w3, w1, w3, w4]  # M, (L1/R1), (L2/R2)  ; was 3, 2, 1, 2, 3
    # c4weights = [w1, w2, w3, w4, w5]  # L2, L1, M, R1, R2
    # c5weights = [w3, w1, w2, w4, w5]  # L1, M, L2, R1, R2
    # New weights format
    # c1weights = [w4, w2, w5, w1, w3]  # R1, R2, M, L1, L2
    # c2weights = [w5, w4, w3, w2, w1]  # R2, R1, M, L1, L2
    # c3weights = [w4, w3, w1, w3, w4]  # M, (L1/R1), (L2/R2)  ; was 3, 2, 1, 2, 3
    # c4weights = [w1, w2, w3, w4, w5]  # L2, L1, M, R1, R2
    # c5weights = [w3, w2, w1, w4, w5]  # L1, L2, M, R1, R2
    # New weights format
    #            L2  L1  M   R1  R2
    # c1weights = [w5, w4, w2, w1, w3]  # R1, M, R2, L1, L2
    # c2weights = [w5, w4, w3, w2, w1]  # R2, R1, M, L1, L2
    # c3weights = [w2, w4, w5, w4, w2]  # M, (L1/R1), (L2/R2)  ; was 3, 2, 1, 2, 3
    # c4weights = [w1, w2, w3, w4, w5]  # L2, L1, M, R1, R2
    # c5weights = [w2, w1, w3, w4, w5]  # L1, M, L2, R1, R2
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


def case_classification(L2, L1, M, R1, R2):
    """Case classifier to determine which direction is best based on "path of least resistance" or minimum case value"""
    case_list = case_processing(L2, L1, M, R1, R2)  # actual func call wont have parameters. returns c list

    casename_dictionary = {0: 'c1', 1: 'c2', 2: 'c3', 3: 'c4', 4: 'c5'}
    min_val = min(case_list)  # find the min in case list, was min switched to max
    idx_of_min_val = case_list.index(min_val)
    casename = casename_dictionary[idx_of_min_val]
    print('the case determined is:', casename)

    casetype_dictionary = {'c1': 'hard left', 'c2': 'left', 'c3': 'straight', 'c4': 'right', 'c5': 'hard right'}
    casetype = casetype_dictionary[casename]
    print('the case type is:', casetype)

    return casetype

def obstacle_avoidance(L2, L1, M, R1, R2):
    """Sub routine triggered by nearby obstacle(s), determines navigation for obstacle avoidance and returns movement"""
    return case_classification(L2, L1, M, R1, R2)  # actual func call wont have parameters

# Testbenching

# Single Sensor Detection #########################################
# Case 1 : Hard Left Case
print('Hard Left Case')
case1 = [10, 10, 10, 1, 10]
obstacle_avoidance(case1[0], case1[1], case1[2], case1[3], case1[4])
print('')