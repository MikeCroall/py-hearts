import socket
try:
    from _thread import *
except ImportError:
    print("Please ensure you are using Python 3+\nWe must import _thread")
from player import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = ""  # means can run anywhere basically
port = 3033

players = []

try:
    s.bind((host, port))
except socket.error as ex:
    print(str(ex))

s.listen(5)

print("Waiting for a connection on port {}".format(port))


def threaded_client_handler(player):
    conn.sendall(
        "You have successfully connected to py-hearts!\nCurrently connected: {}".format(
            socket.gethostname(), player.name, ', '.join([p.name for p in players])).encode())
    while True:
        message = player.said()
        if not message or message == "/exit":
            break
        if message[0] == "/":
            # command other than exit
            if message.lower().startswith("/name "):
                chosen_name = " ".join(message.split(" ")[1:])
                broadcast_except_player("{} changed their name to {}".format(player.name, chosen_name), player)
                player.name = chosen_name
                player.tell("You have set your username to {}".format(chosen_name))
        else:
            print(player.name + ": " + message)
            broadcast_except_player(player.name + ": " + message, player)
    conn.close()
    players.remove(player)
    print("{} disconnected".format(player.name))
    broadcast("{} disconnected".format(player.name))


def broadcast(message):
    broadcast_except_player(message, None)


def broadcast_except_player(message, not_this_player):
    for player in players:
        if player != not_this_player:
            player.tell(message)


while True:
    try:
        conn, addr = s.accept()
        name = "user_{}".format(len(players) + 1)

        print("{} connected from {}:{}".format(name, addr[0], addr[1]))
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
