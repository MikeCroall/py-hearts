import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket: {}".format(s))

server = "www.google.co.uk"
port = 80
request = "GET / HTTP/1.1\nHost: {}\n\n".format(server)

s.connect((server, port))
s.send(request.encode())

result = s.recv(4096)
print("Response: {}".format(result.decode()))