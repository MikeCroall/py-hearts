import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

server = "127.0.0.1"  # for testing - only 127.0.0.1 while server.py running on same machine
port = 3000

s.connect((server, port))
print("Connection established\n")


def receive_loop():
    while keep_alive:
        data = s.recv(1024)
        if not data:
            continue  # if no data actually received
        print(chr(27) + "[2A" + data.decode("utf-8") + "\033[K" + "\n")  # special strings go to line above (avoid messing with input looks) and clear to end of line


def send_loop():
    while keep_alive:
        data = input('Me: ')
        if not data:
            continue  # if hit enter without any actual input
        s.sendall(data.encode())


start_new_thread(receive_loop, ())
start_new_thread(send_loop, ())
try:
    while keep_alive:  # todo can just use main loop for either send or receive loop? No need for the extra thread
        continue
except KeyboardInterrupt as user_cancelled:
    print("\rDisconnecting...")
except:
    raise
