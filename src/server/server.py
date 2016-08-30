import socket
import time
import threading

from player import Player

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents address being unavailable when restarting server

host = ""  # means can run anywhere basically
port = 3033

players = []
accepted_colours = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]  # or hex codes

try:
    s.bind((host, port))

    s.listen(5)

    print("Waiting for a connection on port {}".format(port))


    def handle_command_from_player(message, player):
        # slash has already been removed
        args = message.split(" ")
        if len(args) == 0: return
        type = args[0]

        if type == "name" and len(args) > 1:
            original_name = player.name
            desired_name = " ".join(message.split(" ")[1:])
            if 0 < len(desired_name) <= 16:
                player.name = desired_name
                print("{} changed their username to {}".format(original_name, player.name))
                connected = connected_players()
                player.tell("You have set your username to {}\nCurrently connected ({}): {}".format(
                    player.name, len(players), connected))
                broadcast_except_player("{} set their username to {}\nCurrently connected ({}): {}".format(
                    original_name, player.name, len(players), connected), player)
            else:
                print("{} wants (too long) username {}".format(original_name, desired_name))

        elif type == "colour":
            if len(args) > 1:
                colour = message.split(" ")[1].lower()
                if not colour: return
                if colour in accepted_colours:
                    player.colour = colour
                    print("{} set their colour to {}".format(player.name, player.colour))
                    player.tell("You have set your colour to {}".format(colour), c=colour)
                    broadcast_except_player("{} set their colour to {}".format(player.name, player.colour), player)
                    # todo check for hex codes in elif
                else:
                    player.tell(
                        "{} is not a recognised colour name".format(colour))  # todo ", try using hex codes instead"
            else:
                player.tell("You must enter a colour to use that command!")

        elif type == "hand":
            player.tell("/colour red This command is not ready yet")

        elif type == "help":
            player.tell(
                "\nAvailable commands:" +
                "\n    /name [new name]    - change your name" +
                "\n    /colour [new colour]    - change your text colour" +
                "\n    /hand    - show your current hand" +
                "\n    /help    - see this message" +
                "\n\n    /exit    - disconnect and close the application" +
                "\n")

        else:
            print("{} attempted unrecognised command {}".format(player.name, message))
            player.tell("You have attempted an unrecognised command: {}".format(message))


    def get_next_message(p):
        end_of_transmission = chr(23)  # end of transmission char
        with p.buffer_lock:
            decoded = p.receive_buffer.decode("utf-8")
        while p.keep_alive:
            while end_of_transmission not in decoded:
                time.sleep(0.1)
                with p.buffer_lock:
                    decoded = p.receive_buffer.decode("utf-8")
                # no full transmission yet, loop to check again
            # now something new to check
            if end_of_transmission in decoded:  # double check to avoid failures
                first_cut_off = decoded.index(end_of_transmission)
                to_parse = decoded[:first_cut_off]  # excluding EOT char
                with p.buffer_lock:
                    p.receive_buffer = decoded[first_cut_off + 1:].encode()  # excluding EOT char
                return to_parse
            else:
                return "Error: EOT not found in get_next_message after loop break"


    def receive_loop(p):
        while p.keep_alive:
            try:
                data = p.conn.recv(4096)
                if not data:  # player disconnected if blocking call returns empty byte string
                    # print("{} disconnected from server".format(p.name))
                    p.keep_alive = False
                with p.buffer_lock:
                    p.receive_buffer += data
            except socket.error as ex:
                p.keep_alive = False
                print("Socket error {}".format(str(ex)))


    def client_handler_main(player):
        player.receive_buffer = b""
        player.keep_alive = True
        player.buffer_lock = threading.Lock()

        rec_thread = threading.Thread(target=receive_loop, args=(player,))
        rec_thread.setDaemon(True)
        rec_thread.start()

        # below is parse loop
        player.tell("You have successfully connected to py-hearts!\n/help    - for information on the commands")
        while player.keep_alive:
            try:
                if not player.conn: break  # player disconnect? probably not the way to check it
                message = get_next_message(player)
                if not message: continue
                if message == "/exit": player.keep_alive = False; break  # player definitely disconnected
                if message.startswith("/"):
                    # command other than exit
                    handle_command_from_player(message[1:], player)
                else:
                    print(player.name + ": " + message)
                    broadcast_except_player(player.name + ": " + message, player)
            except Exception as ex:
                print("Error in {}'s thread".format(player.name))
                # maybe break here?
                raise
        player.conn.close()
        try:
            players.remove(player)
        except:
            pass
        print("{} disconnected from server".format(player.name))
        broadcast("{} disconnected from server".format(player.name))


    def broadcast(message):
        failed = []
        for player in players:
            if not player.tell(message):
                failed.append(player)
        for p in failed:
            p.keep_alive = False
            try:
                players.remove(p)
            except:
                pass
        for p in failed: broadcast("{} disconnected".format(p.name))


    def broadcast_except_player(message, not_this_player):
        failed = []
        for player in players:
            if player != not_this_player:
                if not player.tell(message, not_this_player.colour):
                    failed.append(player)
        for p in failed:
            p.keep_alive = False
            try:
                players.remove(p)
            except:
                pass
        for p in failed: broadcast("{} disconnected".format(p.name))


    def connected_players(): return ', '.join([p.name for p in players])


    while True:
        try:
            conn, addr = s.accept()
            name = "anonymous_new_user"

            print("{} connected from {}:{}".format(name, addr[0], addr[1]))
            broadcast("{} has joined".format(name))

            p = Player(name, conn)
            players.append(p)

            cli_thread = threading.Thread(target=client_handler_main, args=(p,))
            cli_thread.setDaemon(True)
            cli_thread.start()

        except KeyboardInterrupt as user_cancelled:
            print("\rExiting...")
            break

        except:
            raise

except socket.error as ex:
    print(str(ex))

s.close()
