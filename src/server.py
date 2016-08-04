import socket
from _thread import *
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ""  # means can run anywhere basically
port = 3000

try:
    s.bind((host, port))
except socket.error as ex:
    print(str(ex))

s.listen(4)

print("Waiting for a connection on port {}".format(3000))

def threaded_client(conn):
    conn.send(str.encode("Hello, and welcome to Hearts!\n"))
    while True:
        data = conn.recv(2048)
        reply = "Server: " + data.decode("utf-8")
        if not data:
            break
        conn.sendall(str.encode(reply))
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to {}:{}".format(addr[0], addr[1]))

    start_new_thread(threaded_client, (conn,))