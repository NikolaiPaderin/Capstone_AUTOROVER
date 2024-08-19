import socket
import threading
import time
import multiprocessing
from GPS import get_GPS()
ser=serial.Serial('/dev/ttyUSB2', 9600)
IP = "100.96.1.38"
PORT = 12345
ADDR = IP, PORT
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
clients = []
gps = get_GPS()

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
            conn.send((gps + "\n").encode())
        time.sleep(5)

def receive_data(sender_conn, sender_addr, receiver_conn, reciever_addr):
    while True:
        try:
            data = sender_conn.recv(1024).decode()
            if data:
                print(f"Received from client {sender_addr}: {data}")
                # Forward the received data to the other client
                if (reciever_addr[0] == '100.96.1.3'):
                    receiver_conn.send((gps + data).encode())
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