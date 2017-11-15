from collections import deque
import socket
import select
import time

class Commutator(object):
    """
    This class implement full duplex channel over a socket.
    It use incoming separate LIFO stacks for incoming and outcoming messages.
    it use select for unblocking the channel
    the enter symbol is used for terminating the message
    """
    def __init__(self, host, port, timeout = None, buffsize = 4096, split_value = 128, switch_time = 1, debuger = None):
        self.__host = host
        self.__port = port
        self.frame = unichr(9166).encode('utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.MAX_BLOCK_SIZE = buffsize
        self.timeout = timeout
        self.socket.settimeout(self.timeout)
        self.in_lifo = deque([])
        self.out_lifo = deque([])
        self.split_value = split_value
        self.switch_time = switch_time
        self.debuger = debuger

    def debug(self, message):
        if self.debuger:
            self.debuger.send(str(message))

    def connect(self):
        self.socket.settimeout(60)
        self.socket.connect((self.__host,self.__port))
        self.socket.settimeout(self.timeout)

    def _recv(self):
        "bare recv"
        response = ''
        while response[-3:] != self.frame:
            try:
                response += self.socket.recv(self.MAX_BLOCK_SIZE)
            except Exception as e:
                self.debug(e)
                continue
        return response[:-3]

    def _send(self, message):
        "bare send"
        request = message + self.frame
        while request:
            try:
                send = self.socket.send(request)
            except Exception as e:
                self.debug(e)
                continue
            request = request[send:]

    def send(self, message):
        sended = False
        while not sended:
            r2r, r2w, r2e = select.select([self.socket],[self.socket],[],self.switch_time)
            if r2r:
                self.debug('recv from send: socets state ' + str(r2r) + ";" + str(r2w) + "." + " inlifo" + str(self.in_lifo))
                self.in_lifo.append(self._recv())
            elif r2w:
                self.debug('send from send: socets state ' + str(r2r) + ";" + str(r2w) + "." + " inlifo" + str(self.in_lifo))
                self._send(message)
                sended = True

    def recv(self):
        r2r, r2w, r2e = select.select([self.socket],[self.socket],[],self.switch_time)
        if self.in_lifo:
            self.debug('recv from buffer: socets state ' + str(r2r) + ";" + str(r2w) + "." + " inlifo" + str(self.in_lifo))
            return self.in_lifo.popleft()
        else:
            self.debug('recv from socket: socets state ' + str(r2r) + ";" + str(r2w) + "." + " inlifo" + str(self.in_lifo))
            return self._recv()

    def close(self):
        self.socket.close()
