class Player:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn

    def tell(self, message):
        if self.conn:
            self.conn.sendall(message.encode())
        else:
            print("{}'s connection is failing".format(self.name))

    def said(self):
        return self.conn.recv(2048).decode("utf-8")
