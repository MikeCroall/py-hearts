import time

class Player:
    def __init__(self, name, conn, colour="black"):
        self.name = name
        self.conn = conn
        self.colour = colour

    def tell(self, message, c="black"):
        try:
            message += chr(23)  # include EOT char
            if not c or c == "black":
                self.conn.sendall(message.encode())
            else:
                self.conn.sendall("/colour {} {}".format(c, message).encode())
            return True
        except:
            print("{}'s connection is failing".format(self.name))
            return False
