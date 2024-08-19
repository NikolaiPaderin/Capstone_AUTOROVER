import socket
import time
import serial
import csv
from datetime import datetime

# Create a socket object
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ser=serial.Serial('/dev/ttyUSB2', 9600)
# Bind the socket to a specific address and port
#host = "100.96.1.38"  # Replace with the actual IP address or hostname
#port = 12345
#server_socket.bind((host, port))

# Listen for incoming connections
#server_socket.listen(5)

#print(f"Server listening on {host}:{port}")
count = 0 
while True:
    # Accept a connection from the client
    #client_socket, addr = server_socket.accept()
    #print(f"Connection from {addr}")

    #Receive data from the client
    #data = client_socket.recv(1024).decode('utf-8')
    #print(f"Received from client: {data}")

    # Process the received data (you can add your custom logic here)
    ser.flushInput()
    ser.flushOutput()
    command = 'AT\r\n'
    ser.write(command.encode())
    time.sleep(0.1)
    command = 'AT+CGPS=1,1\r\n'
    ser.write(command.encode())
    check = 0
    while check != 'N':
        command = 'AT+CGPSINFO\r\n'
        ser.write(command.encode())
        time.sleep(1)
        GPSDATA = ser.read_all().decode('utf-8')
        print(GPSDATA)
        with open("raw_data.csv", 'a') as file:
            file.write(f"{GPSDATA}\n")
        output = GPSDATA.split('\n')
        output = output[1].split(': ')
    #output2 = output2[1].split(',')
        for item in output:
            output2 = item        
        output2 = output2.split(',')
        output3 = []
        x = 0
        lat = []
        lat_l = []
        lon = []
        lon_l = []

        for val in output2:
           output3.append(val)
           if x == 0:
              lat = val
           if x == 1:
              lat_l = val
           if x == 2:
              lon = val
           if x == 3:
              lon_l = val
           x +=1
        result = 0
        print(lat,lat_l,lon,lon_l)
        for char in lat:
            digit = ord(char)-ord('0')
            result = result*10+digit
        lat = result/10000000

        result = 0
        for chare in lon:
            digit = ord(chare)-ord('0')
            result = result*10+digit
        lon = result/10000000
        lat_d = lat//100
        lat_m = lat-lat_d * 100
        lat_dec = lat_d +lat_m /  60
        lon_d = lon//100
        lon_m = lon - lon_d*100
        lon_dec = lon_d + lon_m / 60
        if lon_l == 'W':
            lon_dec *=-1

        check = lat_l
        print(lat_dec-0.006651481,lon_dec+0.00919302)
        lat_con = lat_dec-0.006651481
        lon_con = lon_dec+0.00919302

    information = '{lat_dec},{lon_dec}'
    now = datetime.now()
    current_time= now.strftime("%H:%M:%S")
    print(current_time)
    with open("gps_configuration.csv", 'a') as file:
        file.write(f"{current_time}\n")
        file.write(f"raw data: {lat_dec}, {lon_dec}\n")
        file.write(f"calibrated data: {lon_con}, {lat_con}\n")
    with open("raw_configuration.csv", 'a') as file:
        file.write(f"{current_time}\n")
        file.write(f"{lat_dec}, {lon_dec}\n")
    with open("adjusted_configuration.csv", 'a') as file:
        file.write(f"{current_time}\n")
        file.write(f"calibrated data: {lon_con}, {lat_con}\n")

        
    # In this example, we'll simply reverse the received data
    # Send the reversed data back to the client
    #if check == 'N':
    #    client_socket.send(information.encode('utf-8'))
    #print("data sent")
    time.sleep(1)

    # Close the client socket
#client_socket.close()
ser.close()
