import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

server = input('Server IP: ')  # for testing on localhost use 127.0.0.1
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
        print(chr(27) + "[2A" + data.decode("utf-8") + "\033[K" + "\n")
        # above: special strings go to line above (avoid messing with input looks) and clear to end of line
        # todo GUI to avoid needing this awful (and not working properly) special character system

start_new_thread(receive_loop, ())

try:
    while keep_alive:
        data = input('Me: ')
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
