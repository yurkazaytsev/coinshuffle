import socket

class Mailbox(object):
    """
    This class is implement mailbox for coinshuffle protocol.
    This version is built upon the socket for communication with server and
    """

    def __init__(self, host, port, timeout = None):
        self.__host = host
        self.__port = port
        self.frame = unichr(9166).encode('utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.MAX_BLOCK_SIZE = 2**12
        self.timeout = timeout
        self.socket.settimeout(self.timeout)

    def connect(self):
        self.socket.connect((self.__host,self.__port))

    def send(self, message):
        request = message + self.frame
        # print request
        return self.socket.sendall(request)


    def recv(self):
        response = ''
        while response[-3:] != self.frame:
            response += self.socket.recv(self.MAX_BLOCK_SIZE)
        return response[:-3]

    def close(self):
        self.socket.close()

    def share(self, message, number, number_of_players):
        messages =''
        for i in range(1, number_of_players + 1):
            if i is number:
                self.send(message)
            response = self.recv()
            messages += response
        return messages
# Testing part
# from messages import Messages
#
# msgs = Messages()
# msgs.make_greeting('testkey')
# mb = Mailbox('localhost',8080)
# mb.connect()
# mb.send(msgs.packets.SerializeToString())
# msgs.packets.ParseFromString(mb.recv())
# msgs.packets
