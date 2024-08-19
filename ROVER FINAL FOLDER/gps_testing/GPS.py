import socket
import time
import serial
import csv
from datetime import datetime
import re

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
def get_GPS():
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

    # Print the latitude and longitude
            return latitude, longitude

 
    # In this example, we'll simply reverse the received data
    # Send the reversed data back to the client
    #if check == 'N':
    #    client_socket.send(information.encode('utf-8'))
    #print("data sent")
    time.sleep(1)
    
    # Close the client socket
#client_socket.close()
lat, lon = get_GPS()
print(f"{lat} {lon}")
ser.close()

