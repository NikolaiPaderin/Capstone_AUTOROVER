import socket
import threading
import time
import multiprocessing
import serial
import csv
from datetime import datetime
import re


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
            check = 'N'

    # Print the latitude and longitude
            return latitude, longitude

 
    # In this example, we'll simply reverse the received data
    # Send the reversed data back to the client
    #if check == 'N':
    #    client_socket.send(information.encode('utf-8'))
    #print("data sent")
    time.sleep(1)

IP = "100.96.1.38"
PORT = 12345
ADDR = IP, PORT
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
clients = []
gps1, gps2 = get_GPS()
GPS = f"{gps1} {gps2}"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    ip = addr[0]
    connected = True
    other_conn = None
    other_addr = None
    t = True
    # Find the other connected client

    if (ip == '100.96.1.2'):
        while (t):
            for client_conn, client_addr in clients:
                if client_addr != addr:
                    other_conn = client_conn
                    other_addr = client_addr
                    t = False 
                if (other_conn == None):
                    time.sleep(5)
        receive_thread = threading.Thread(target=receive_data, args=(conn, addr, other_conn, other_addr))
        receive_thread.start()

    else:
        rec = threading.Thread(target=receive_datapath, args=(conn, addr))
        rec.start()
    while connected:
        if (ip == '100.96.1.2'):
            gps1, gps2 = get_GPS()
            GPS = f"{gps1} {gps2}"
            conn.send((GPS + "\n").encode())
        time.sleep(5)

def receive_data(sender_conn, sender_addr, receiver_conn, reciever_addr):
    while True:
        try:
            data = sender_conn.recv(1024).decode()
            if data:
                print(f"Received from client {sender_addr}: {data}")
                # Forward the received data to the other client
                if (reciever_addr[0] == '100.96.1.3'):
                    gps1, gps2 = get_GPS()
                    GPS = f"{gps1} {gps2}"
                    receiver_conn.send((GPS + " " + data).encode())
        except ConnectionResetError:
            print(f"Client {sender_addr} disconnected.")
            break
def receive_datapath(sender_conn, sender_addr):
    while True:
        try:
            datapath = sender_conn.recv(1024).decode()
            if datapath:
                print("From pathfinder: ", datapath)

        except ConnectionResetError:
            print(f"Client {sender_addr} disconnected.")
            break



def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))
        thread = multiprocessing.Process(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS]")

if __name__ == "__main__":
    main()