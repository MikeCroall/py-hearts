import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

server = "127.0.0.1"  # for testing - only 127.0.0.1 while server.py running on same machine
port = 3000

s.connect((server, port))
print("Connection established")


def receive_loop():
    while keep_alive:
        data = s.recv(1024)
        if not data:
            continue  # if no data actually received
        print(data.decode("utf-8"))


def send_loop():
    while keep_alive:
        data = input('')
        if not data:
            continue  # if hit enter without any actual input
        s.sendall(data.encode())


start_new_thread(receive_loop, ())
start_new_thread(send_loop, ())

while keep_alive:
    continue

''' buffered receiving larger than specified buffer
response = s.recv(1024)
result = response
while len(response) > 0:
    response = s.recv(1024)  # does not return at end of data receiving if data isn't 1024 bytes? Something isn't right
    result += response
'''


''' original main loop
while True:
    data = s.recv(2048)
    print(data.decode("utf-8"))
    reply = input('Me: ')
    if not data:
        break
    s.sendall(str.encode(reply))
'''
