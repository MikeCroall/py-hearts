import socket, time
from tkinter import *
from tkinter import messagebox
import threading

ready = False
accepted_colours = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
receive_buffer = b""
buffer_lock = threading.Lock()

# variables that should be matched on the server side
username = "unset_username"
colour = "black"

root = Tk()
root.withdraw()
message = StringVar()


def send(m):
    global s
    m += chr(23)  # include EOT char
    s.sendall(m.encode())


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
                send(text)
            else:
                add_to_chat_log("Please ensure your username is between 1 and 16 characters long!")
        else:
            add_to_chat_log("You must enter a desired username!", c="orange")

    elif args[0].lower() == "/colour":
        if len(args) > 1:
            chosen_colour = args[1].lower()
            if chosen_colour in accepted_colours:
                colour = chosen_colour
                send(text)
            else:
                add_to_chat_log("That colour is not recognised!", c="orange")
        else:
            add_to_chat_log("You must enter a desired colour!", c="orange")

    elif args[0].lower() == "/exit":
        add_to_chat_log("Disconnected from server", c="red")
        global keep_alive
        keep_alive = False
        send("/exit")
        close_thread = threading.Thread(target=close_countdown, args=())
        close_thread.setDaemon(True)
        close_thread.start()
    else:
        send(text)


def close_countdown():
    global root
    add_to_chat_log("Auto-closing in 3...", c="red")
    time.sleep(1)
    add_to_chat_log("2...", c="red")
    time.sleep(1)
    add_to_chat_log("1...", c="red")
    time.sleep(1)
    root.destroy()
    sys.exit(0)  # ensure program closes, as lock blocking may prevent this


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
                send(text)
                add_me_to_chat_log("{}: {}".format(username, text))
            message.set("")
    except Exception as ex:
        print("Something went wrong sending that message!")
        print(ex)
        raise


def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        send("/exit")
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
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

server = input("Server IP: ").strip()  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    add_to_chat_log("No server entered, defaulting to 127.0.0.1", c="orange")

port = 3033

try:
    s.connect((server, port))
    add_to_chat_log("Connection established", c="green")
    print("\n" + "=" * 68 + "\n\tPlease use the pop-up window from this point on\n" + "=" * 68 + "\n")
    send("/name {}".format(username))
except:
    add_to_chat_log("Connection could not be made", c="red")
    keep_alive = False


def handle_command_from_server(command):
    # slash has already been removed
    args = command.split(" ")
    command_type = args[0].lower()
    if command_type == "colour":
        actual_message = " ".join(args[2:])
        add_to_chat_log(actual_message, c=args[1])
    elif command_type == "hand":
        suits_to_print_in_colour = (" ".join(args[1:])).split("\n")
        for x, line in enumerate(suits_to_print_in_colour):
            # order ALWAYS clubs, diamonds, spades, hearts (in this game at least)
            add_to_chat_log(line, "black" if x % 2 == 0 else "red")
        print("Hand is as shown:\n{}".format("\n".join(suits_to_print_in_colour)))
    else:
        add_to_chat_log("Received unrecognised command from server /{}".format(command))


def receive_loop():
    global keep_alive, receive_buffer, buffer_lock
    while keep_alive:
        try:
            data = s.recv(4096)
            if not data:  # server disconnected if blocking call returns empty byte string
                add_to_chat_log("Disconnected from server", c="red")
                keep_alive = False
                close_thread = threading.Thread(target=close_countdown, args=())
                close_thread.setDaemon(True)
                close_thread.start()
            with buffer_lock:
                receive_buffer += data
        except socket.error as ex:
            keep_alive = False
            add_to_chat_log("Socket error {}".format(str(ex)), c="red")


def get_next_message():
    global keep_alive, receive_buffer, buffer_lock
    end_of_transmission = chr(23)  # end of transmission char
    decoded = receive_buffer.decode("utf-8")
    while keep_alive:
        while end_of_transmission not in decoded:
            time.sleep(0.1)
            with buffer_lock:
                decoded = receive_buffer.decode("utf-8")
            # no full transmission yet, loop to check again
        # now something new to check
        if end_of_transmission in decoded:  # double check to avoid failures
            first_cut_off = decoded.index(end_of_transmission)
            to_parse = decoded[:first_cut_off]  # excluding EOT char
            with buffer_lock:
                receive_buffer = decoded[first_cut_off + 1:].encode()  # excluding EOT char
            return to_parse
        else:
            return "Error: EOT not found in get_next_message after loop break"


def parse_loop():
    global keep_alive
    while keep_alive:
        try:
            text = get_next_message()  # returns decoded string
            if not text: break
            if text.startswith("/"):
                handle_command_from_server(text[1:])  # removes /
            else:
                add_to_chat_log(text)
        except socket.error as ex:
            keep_alive = False
            add_to_chat_log("Socket error {}".format(str(ex)), c="red")


rec_thread = threading.Thread(target=receive_loop, args=())
par_thread = threading.Thread(target=parse_loop, args=())
rec_thread.setDaemon(True)
par_thread.setDaemon(True)
rec_thread.start()
par_thread.start()

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
