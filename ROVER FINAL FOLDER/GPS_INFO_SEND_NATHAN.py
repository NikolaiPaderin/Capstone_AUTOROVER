import socket
import time
import random
import threading
import serial
# Replace these with your desired latitude and longitude values
latitude = 37.7749
longitude = -122.4194
#ser=serial.Serial('/dev/ttyUSB2', 9600)
# Create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "100.96.1.38" # Change this to the appropriate host
port = 12345 # Change this to the appropriate port

server_socket.bind((host, port))
server_socket.listen(1)
print(f"Server listening on {host}:{port}")

client_socket, client_address = server_socket.accept()
print(f"Accepted connection from {client_address}")
def get_GPS():
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
        print(lat_dec,lon_dec)
        check = 'N'
    information = f"{lat_dec} {lon_dec}"
    return information
def receive_data():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                print(f"Received from client: {data}")
                # Process the received data here, if needed

                # Send a response back to the client (echo) with a newline delimiter
                response = (f"sent")
                client_socket.send((response + "\n").encode())
        except ConnectionResetError:
            print("Client disconnected.")
            break

receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

while True:
    # Generate random latitude and longitude (for testing)
    latitude, longitude = 30.616568, -96.311092
    data = get_GPS()
    location_string= data
    #get_GPS()
    #with open(lat_lon, 'r') as file:
    #    location_string = lat_lon.read_all()
    #lat_lon.close()
    # Create a single string with latitude and longitude
    #location_string = f"{location_string}"

    # Send the string to the connected client with a newline delimiter
    client_socket.send((location_string + "\n").encode())

    print(f"Sent: {location_string}")

    time.sleep(5) # Wait for 5 seconds before sending the next coordinates