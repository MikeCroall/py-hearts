import socket
from _thread import *
from tkinter import *

global chat
global message
root = Tk()
chat = StringVar()
message = StringVar()

# gui
frame_chat_history = Frame(root)
frame_chat_history.pack()
frame_send_message = Frame(root)
frame_send_message.pack(side=BOTTOM, fill=X, expand=1)

chat.set("Welcome to py-hearts!\n")
lbl_chat = Label(frame_chat_history, textvariable=chat, anchor=NW, justify=LEFT, font=("Arial", 12))
lbl_chat.pack(fill=BOTH, expand=1)
txt_message = Entry(frame_send_message, font=("Arial", 12), textvariable=message)
txt_message.pack(side=LEFT, fill=X, expand=1)


def btn_send_clicked():
    try:
        if keep_alive:
            print("Sending message...")
            if message.get() == "":
                return
            s.sendall(message.get().encode())
            add_to_chat_log("Me: {}".format(message.get()))
            message.set("")
            print("Message sent")
    except Exception as ex:
        print("Something went wrong!")
        print(ex)
        raise


btn_send = Button(frame_send_message, text="Send", font=("Arial", 12), command=btn_send_clicked)
btn_send.pack(side=RIGHT)


def add_to_chat_log(m):
    chat.set("{}\n{}".format(chat.get(), m))
    print(m)


# connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keep_alive = True

server = input('Server IP: ')  # for testing on localhost use 127.0.0.1
if not server:
    server = "127.0.0.1"
    add_to_chat_log("No server entered, defaulting to 127.0.0.1")
port = 3033

try:
    s.connect((server, port))
    add_to_chat_log("Connection established\n")
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

root.mainloop()
s.close()
