import socket, time
try:
    from _thread import *
except ImportError:
    print("Please ensure you are using Python 3+\nWe must import _thread")
from tkinter import *

ready = False

root = Tk()

message = StringVar()

# gui
root.wm_title("py-hearts client")


def enter_from_box(event):
    btn_send_clicked()


root.bind('<Return>', enter_from_box)

frame_chat_history = Frame(root)
frame_chat_history.pack(fill=BOTH, expand=1)
frame_send_message = Frame(root)
frame_send_message.pack(side=BOTTOM, fill=X, expand=0)

scrollbar = Scrollbar(frame_chat_history)
scrollbar.pack(side=RIGHT, fill=Y)
lst_chat = Listbox(frame_chat_history, font=("Arial", 12), yscrollcommand=scrollbar.set, width=60)
lst_chat.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar.config(command=lst_chat.yview)
txt_message = Entry(frame_send_message, font=("Arial", 12), textvariable=message)
txt_message.pack(side=LEFT, fill=X, expand=1)


def btn_send_clicked():
    try:
        if keep_alive and ready:
            text = message.get()
            if text.strip() == "":
                return
            if text[0] == "/":
                print("Commands not yet implemented")
                # todo handle commands
            else:
                s.sendall(text.encode())
                add_to_chat_log("{}: {}".format(username, text))
            message.set("")
    except Exception as ex:
        print("Something went wrong sending that message!")
        print(ex)
        raise


btn_send = Button(frame_send_message, text="Send", font=("Arial", 12), command=btn_send_clicked)
btn_send.pack(side=RIGHT)


def add_to_chat_log(m):
    # \n does not print as new line in list views, handle it separately
    for line in m.split("\n"):
        lst_chat.insert(END, line)
    print(m)
    lst_chat.see(END)


# connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

username = input("Username: ")
if not username:
    add_to_chat_log("No username entered, generating username...")
    username = "user_{}".format(str(int(round(time.time() * 1000)))[-4])

server = input("Server IP: ")  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    add_to_chat_log("No server entered, defaulting to 127.0.0.1")

port = 3033

try:
    s.connect((server, port))
    add_to_chat_log("Connection established\n")
    s.sendall("/name {}".format(username))
except:
    add_to_chat_log("Connection could not be made")
    keep_alive = False


def receive_loop():
    global keep_alive
    while keep_alive:
        data = s.recv(1024)
        if not data:
            continue  # if no data actually received
        add_to_chat_log(data.decode("utf-8"))


start_new_thread(receive_loop, ())

ready = True
root.mainloop()
s.close()
