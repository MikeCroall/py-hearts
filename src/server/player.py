class Player:
    def __init__(self, name, conn, colour="black"):
        self.name = name
        self.conn = conn
        self.colour = colour

    def tell(self, message, c="black"):
        try:
            if not c or c == "black":
                self.conn.sendall(message.encode())
            else:
                self.conn.sendall("/colour {} {}".format(c, message).encode())
        except:
            print("{}'s connection is failing".format(self.name))

    def said(self):
        return self.conn.recv(2048).decode("utf-8")
