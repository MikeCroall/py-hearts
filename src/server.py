import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ""  # means can run anywhere basically
port = 3000

players = []

try:
    s.bind((host, port))
except socket.error as ex:
    print(str(ex))

s.listen(4)

print("Waiting for a connection on port {}".format(3000))


def threaded_client_handler(conn, username):
    conn.send("Hello, and welcome to Hearts!\n".encode())
    while True:
        data = conn.recv(2048)
        if not data:
            break
        # broadcast to everyone else who said what
        broadcast_except_player(username + ": " + data.decode("utf-8"), conn)

        # below simply echos back to that player
        #reply = "Server: " + data.decode("utf-8")
        #conn.sendall(reply.encode())

    conn.close()


def broadcast(message):
    for name, conn in players:
        conn.sendall(message.encode())


def broadcast_except_player(message, player_conn):
    for name, conn in players:
        if conn != player_conn:
            conn.sendall(message.encode())


while True:
    conn, addr = s.accept()
    username = "user_{}".format(len(players) + 1)

    print("Connected to {}:{}, as {}".format(addr[0], addr[1], username))
    players.append((username, conn))
    start_new_thread(threaded_client_handler, (conn,username,))
