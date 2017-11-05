import socket
import asyncore

class Mailbox(object):
    """
    This class is implement mailbox for coinshuffle protocol.
    This version is built upon the socket for communication with server and
    """

    def __init__(self, host, port, timeout = 0):
        self.__host = host
        self.__port = port
        self.frame = unichr(9166).encode('utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.MAX_BLOCK_SIZE = 16384
        self.timeout = timeout
        self.socket.settimeout(self.timeout)

    def connect(self):
        self.socket.connect((self.__host,self.__port))

    def send(self, message):
        request = message + self.frame
        self.socket.sendall(request)

    def recv(self):
        response = self.socket.recv(self.MAX_BLOCK_SIZE)
        # while True:
        #     try:
        #         response = self.socket.recv(self.MAX_BLOCK_SIZE)
        #         return response[:-3]
        #     except:
        #         # self.socket.send(self.frame)
        #         # print('unblocked')
        #         continue
        return response[:-3]

    def close(self):
        self.socket.close()

    def recvfromall(self, number_of_players):
        messages = ''
        for i in range(number_of_players):
            response = self.socket.recv(self.MAX_BLOCK_SIZE)
            messages += response[:-3]
        return messages

    def share(self, message, number, number_of_players):
        messages =''
        for i in range(number_of_players):
            if i + 1 is number:
                self.send(message)
            response = self.socket.recv(self.MAX_BLOCK_SIZE)
            messages += response[:-3]
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
