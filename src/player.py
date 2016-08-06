class Player:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn

    def tell(self, message):
        self.conn.sendall(message.encode())

    def said(self):
        return self.conn.recv(2048).decode("utf-8")