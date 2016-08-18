import socket, time

try:
    from _thread import *
except ImportError:
    print("Please ensure you are using Python 3+\nWe must import _thread")
from tkinter import *

ready = False
accepted_colours = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]

# variables that should be matched on the server side
username = "unset_username"
colour = "black"

root = Tk()
root.withdraw()
message = StringVar()


# gui
def enter_from_box(event):
    btn_send_clicked()


def handle_command_to_send(text):
    global username
    global colour
    args = text.split(" ")
    if len(args) == 0: return

    if args[0].lower() == "/name":
        if len(args) > 1:
            desired_username = " ".join(args[1:])
            if 0 < len(desired_username) <= 16:
                username = desired_username
                s.sendall(text.encode())
            else:
                add_to_chat_log("Please ensure your username is between 1 and 16 characters long!")
        else:
            add_to_chat_log("You must enter a desired username!")

    elif args[0].lower() == "/colour":
        if len(args) > 1:
            chosen_colour = args[1].lower()
            if chosen_colour in accepted_colours:
                colour = chosen_colour
                s.sendall(text.encode())
        else:
            add_to_chat_log("You must enter a desired colour!")
    else:
        s.sendall(text.encode())


def btn_send_clicked():
    global username
    try:
        if keep_alive and ready:
            text = message.get().strip()
            if text == "":
                return
            if text.startswith("/"):  # local command handling
                handle_command_to_send(text)
            else:
                s.sendall(text.encode())
                add_me_to_chat_log("{}: {}".format(username, text))
            message.set("")
    except Exception as ex:
        print("Something went wrong sending that message!")
        print(ex)
        raise


root.wm_title("py-hearts client - by Mike Croall")
root.bind('<Return>', enter_from_box)

frame_chat_history = Frame(root)
frame_chat_history.pack(fill=BOTH, expand=1)
frame_send_message = Frame(root)
frame_send_message.pack(side=BOTTOM, fill=X, expand=0)

scrollbar = Scrollbar(frame_chat_history)
lst_chat = Listbox(frame_chat_history, font=("Arial", 12), yscrollcommand=scrollbar.set, width=60)
scrollbar.config(command=lst_chat.yview)
txt_message = Entry(frame_send_message, font=("Arial", 12), textvariable=message)
btn_send = Button(frame_send_message, text="Send", font=("Arial", 12), command=btn_send_clicked)

scrollbar.pack(side=RIGHT, fill=Y)
lst_chat.pack(side=LEFT, fill=BOTH, expand=1)
txt_message.pack(side=LEFT, fill=X, expand=1)
btn_send.pack(side=RIGHT)


def add_to_chat_log(m, c="black"):
    # \n does not print as new line in list views, it prints as a bell, handle it separately
    for line in m.split("\n"):
        lst_chat.insert(END, line)
        lst_chat.itemconfigure(END, fg=c)
    print(m)
    lst_chat.see(END)


def add_me_to_chat_log(m):
    global colour
    for line in m.split("\n"):
        lst_chat.insert(END, line)
        lst_chat.itemconfigure(END, fg=colour)
    print(m)
    lst_chat.see(END)


# connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

username = input("Username: ").strip()
if not username or len(username) > 16:
    add_to_chat_log("Invalid username entered, generating username...", c="orange")
    username = "user_{}".format(str(int(time.time() * 1000))[-4:])

server = input("Server IP: ")  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    add_to_chat_log("No server entered, defaulting to 127.0.0.1", c="orange")

port = 3033

try:
    s.connect((server, port))
    add_to_chat_log("Connection established", c="green")
    print(
        "\n\n====================================================================\n\tPlease use the pop-up window from this point on\n====================================================================\n")
    s.sendall("/name {}".format(username).encode())
except:
    add_to_chat_log("Connection could not be made", c="red")
    keep_alive = False


def handle_command_from_server(command):
    # slash has already been removed
    parts = command.split(" ")
    type = parts[0].lower()
    if type == "colour":
        actual_message = " ".join(parts[2:])
        add_to_chat_log(actual_message, c=parts[1])
    elif type == "hand":
        suits_to_print_in_colour = (" ".join(parts[1:])).split("\n")
        for x, line in enumerate(suits_to_print_in_colour):
            # order ALWAYS clubs, diamonds, spades, hearts (in this game at least)
            add_to_chat_log(line, "black" if x % 2 == 0 else "red")
        print("Hand is as shown:\n{}".format("\n".join(suits_to_print_in_colour)))
    else:
        add_to_chat_log("Received unrecognised command from server /{}".format(command))


def recv_timeout(sock, timeout=2):
    sock.setblocking(0)

    total_data = []
    data = ""

    begin = time.time()
    while True:
        if total_data and time.time() - begin > timeout:
            break

        elif time.time() - begin > timeout * 2:
            break

        try:
            data = sock.recv(8192)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass

    return ''.join(total_data)


def receive_loop():
    global keep_alive
    while keep_alive:
        try:
            data = recv_timeout(s)
            if not data:
                add_to_chat_log("Disconnected from server", c="red")
                keep_alive = False
                break  # if server closed
            text = data.decode("utf-8")
            if text.startswith("/"):
                handle_command_from_server(text[1:])  # removes /
            else:
                add_to_chat_log(data.decode("utf-8"))
        except socket.error as ex:
            keep_alive = False
            add_to_chat_log("Socket error {}".format(str(ex)), c="red")
    time.sleep(1)
    root.destroy()


start_new_thread(receive_loop, ())

ready = True

if __name__ == "__main__":
    root.deiconify()
    try:
        root.mainloop()
    except KeyboardInterrupt as ex:  # allow (albeit slow) keyboard interrupt in terminal to exit window
        pass
    except:
        raise

s.close()
