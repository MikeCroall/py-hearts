import socket, time

try:
    from _thread import *
except ImportError:
    print("Please ensure you are using Python 3+\nWe must import _thread")
from tkinter import *

ready = False
username = "unset_username"
root = Tk()
root.withdraw()
message = StringVar()


# gui
def enter_from_box(event):
    btn_send_clicked()


def btn_send_clicked():
    global username
    try:
        if keep_alive and ready:
            text = message.get()
            if text.strip() == "":
                return
            if text.startswith("/"):
                if text.lower().startswith("/name "):
                    s.sendall(text.encode())
                    username = " ".join(text.split(" ")[1:])
                else:
                    s.sendall(text.encode())
            else:
                s.sendall(text.encode())
                add_to_chat_log("{}: {}".format(username, text))
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
    print(m)
    lst_chat.see(END)
    lst_chat.itemconfigure(END, fg=c)


# connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

username = input("Username: ")
if not username:
    add_to_chat_log("No username entered, generating username...", c="orange")
    username = "user_{}".format(str(int(time.time() * 1000))[-4:])

server = input("Server IP: ")  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    add_to_chat_log("No server entered, defaulting to 127.0.0.1", c="orange")

port = 3033

try:
    s.connect((server, port))
    add_to_chat_log("Connection established", c="green")
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
    else:
        add_to_chat_log("Received unrecognised command from server /{}".format(command))


def receive_loop():
    global keep_alive
    while keep_alive:
        try:
            data = s.recv(1024)
            if not data:
                add_to_chat_log("Disconnected from server", c="red")
                keep_alive = False
                break  # if server closed
            text = data.decode("utf-8")
            if text.startswith("/"):
                print("Received command from server {}".format(text))
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
        root.destroy()
        pass
    except:
        raise

s.close()
