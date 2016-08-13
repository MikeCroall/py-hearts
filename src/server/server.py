import socket

try:
    from _thread import *
except ImportError:
    print("Please ensure you are using Python 3+\nWe must import _thread")
from player import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents address being unavailable when restarting server

host = ""  # means can run anywhere basically
port = 3033

players = []
accepted_colours = ["white", "black", "red", "green", "blue", "cyan", "yellow", "magenta"]  # or hex codes

try:
    s.bind((host, port))

    s.listen(5)

    print("Waiting for a connection on port {}".format(port))


    def handle_command_from_player(message, player):
        if message.lower().startswith("/name "):
            original_name = player.name
            player.name = " ".join(message.split(" ")[1:])
            print("{} changed their username to {}".format(original_name, player.name))
            connected = connected_players()
            player.tell("You have set your username to {}\nCurrently connected: {}".format(
                player.name, connected))
            broadcast_except_player("{} changed their username to {}\nCurrently connected: {}".format(
                original_name, player.name, connected), player)

        elif message.lower().startswith("/colour "):
            colour = message.split(" ")[1].lower()
            if not colour: return
            if colour in accepted_colours:
                player.colour = colour
                player.tell("You have set your colour to {}".format(colour), c=colour)
                print("{} set their colour to {}".format(player.name, player.colour))
                # todo check for hex codes in elif
            else:
                player.tell("{} is not a recognised colour name".format(colour))  # todo ", try using hex codes instead"

        else:
            print("{} attempted unrecognised command {}".format(player.name, message))
            player.tell("You have attempted an unrecognised command")


    def threaded_client_handler(player):
        conn.sendall("You have successfully connected to py-hearts!".encode())
        while True:
            if not player.conn:
                break  # player disconnect? probably not the way to check it
            message = player.said()
            if not message or message == "/exit":
                break  # player definitely disconnected
            if message.startswith("/"):
                # command other than exit
                handle_command_from_player(message, player)
            else:
                print(player.name + ": " + message)
                broadcast_except_player(player.name + ": " + message, player)
        conn.close()
        players.remove(player)
        print("{} disconnected".format(player.name))
        broadcast("{} disconnected".format(player.name))


    def broadcast(message):
        failed = []
        for player in players:
            if not player.tell(message):
                failed.append(player)
        for p in failed: players.remove(p)
        for p in failed: broadcast("{} disconnected".format(p.name))


    def broadcast_except_player(message, not_this_player):
        failed = []
        for player in players:
            if player != not_this_player:
                if not player.tell(message, not_this_player.colour):
                    failed.append(player)
        for p in failed: players.remove(p)
        for p in failed: broadcast("{} disconnected".format(p.name))


    def connected_players():
        return "({}) - ".format(len(players)) + ', '.join([p.name for p in players])


    while True:
        try:
            conn, addr = s.accept()
            name = "anonymous_new_user"

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

except socket.error as ex:
    print(str(ex))

s.close()
