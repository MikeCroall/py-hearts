import socket
from _thread import *
from player import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ""  # means can run anywhere basically
port = 3000

players = []

try:
    s.bind((host, port))
except socket.error as ex:
    print(str(ex))

s.listen(5)

print("Waiting for a connection on port {}".format(port))


def threaded_client_handler(player):
    conn.sendall("You have successfully connected to the hearts server @ {}!\n".format(socket.gethostname()).encode())
    while True:
        message = player.said()
        if not message:
            break
        print(player.name + ": " + message)
        broadcast_except_player(player.name + ": " + message, player)
    conn.close()
    print("{} disconnected".format(player.name))


def broadcast(message):
    for player in players:
        player.tell(message)


def broadcast_except_player(message, not_this_player):
    for player in players:
        if player != not_this_player:
            player.tell(message)


while True:
    try:
        conn, addr = s.accept()
        name = "user_{}".format(len(players) + 1)

        print("Connected to {}:{}, as {}".format(addr[0], addr[1], name))
        broadcast("{} has joined".format(name))

        p = Player(name, conn)
        players.append(p)

        start_new_thread(threaded_client_handler, (p,))

    except KeyboardInterrupt as user_cancelled:
        print("\rExiting...")
        break

    except:
        raise

s.close()
