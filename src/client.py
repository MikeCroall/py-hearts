import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

server = input('Server IP: ')  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    print("No server entered, defaulting to 127.0.0.1")
port = 3033

try:
    s.connect((server, port))
    print("Connection established\n")
except:
    print("Connection could not be made")
    keep_alive = False


def receive_loop():
    while keep_alive:
        data = s.recv(1024)
        if not data:
            continue  # if no data actually received
        print(data.decode("utf-8"))
        # todo gui

start_new_thread(receive_loop, ())

try:
    while keep_alive:
        data = input('')
        if not data:
            continue  # if hit enter without any actual input
        s.sendall(data.encode())

except KeyboardInterrupt as user_cancelled:
    keep_alive = False
    print("\rDisconnecting...")

except:
    keep_alive = False
    raise

s.close()
