from collections import deque
import socket
import select

class Commutator(object):
    """
    This class implement full duplex channel over a socket.
    It use incoming separate LIFO stacks for incoming and outcoming messages.
    it use select for unblocking the channel
    the enter symbol is used for terminating the message
    """
    def __init__(self, host, port, timeout = None, buffsize = 16384, split_value = 128, switch_time = None):
        self.__host = host
        self.__port = port
        self.frame = unichr(9166).encode('utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.MAX_BLOCK_SIZE = buffsize
        self.timeout = timeout
        self.socket.settimeout(self.timeout)
        self.in_lifo = deque([])
        self.out_lifo = deque([])
        self.split_value = split_value
        self.switch_time = switch_time

    def connect(self):
        self.socket.connect((self.__host,self.__port))

    def bare_send(self, message):
        request = message + self.frame
        while len(request)>0:
            self.socket.send(request[:self.split_value])
            request = request[self.split_value:]

    def bare_recv(self):
        response = ''
        while response[-3:] != self.frame:
            response += self.socket.recv(self.MAX_BLOCK_SIZE)
        return response[:-3]

    def recv(self):
        if len(self.in_lifo) is not 0:
            return self.in_lifo.popleft()
        else:
            received = False
            while not received:
                r2r, r2w, err = select.select([self.socket],[self.socket],[], self.switch_time)
                if len(r2r) > 0:
                    received = True
                    return self.bare_recv()
                if len(r2w) > 0 and len(self.out_lifo) > 0:
                    self.bare_send(self.out_lifo.popleft())

    def send(self, message):
        if len(self.out_lifo) > 0:
            self.out_lifo.append(message)
            request = self.out_lifo.popleft()
        else:
            request = message
        sended = False
        while not sended:
            r2r, r2w, err = select.select([self.socket],[self.socket],[], self.switch_time)
            if len(r2w) > 0:
                self.bare_send(request)
                sended = True
            if len(r2r) > 0:
                self.in_lifo.append(self.bare_recv())

    def close(self):
        self.socket.close()
