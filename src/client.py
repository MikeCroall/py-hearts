import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "127.0.0.1"  # only 127.0.0.1 while server.py running on same machine
port = 3000

s.connect((server, port))
print("Connection established")

'''
response = s.recv(1024)
result = response
while len(response) > 0:
    response = s.recv(1024)  # does not return at end of data receiving if data isn't 1024 bytes? Something isn't right
    result += response
'''

while True:
    data = s.recv(2048)
    print(data.decode("utf-8"))
    reply = input('Client: ')
    if not data:
        break
    s.sendall(str.encode(reply))

print("Connection lost")