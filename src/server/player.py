import time


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
            return True
        except:
            print("{}'s connection is failing".format(self.name))
            return False

    def said(self):
        return self.recv_timeout().decode("utf-8")

    def recv_timeout(self, timeout=2):
        self.conn.setblocking(0)

        total_data = []
        data = ""

        begin = time.time()
        while True:
            if total_data and time.time() - begin > timeout:
                break

            elif time.time() - begin > timeout * 2:
                break

            try:
                data = self.conn.recv(8192)
                if data:
                    total_data.append(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass

        return b''.join(total_data)