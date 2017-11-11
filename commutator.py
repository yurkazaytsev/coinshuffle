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
    def __init__(self, host, port, timeout = None, buffsize = 4096, split_value = 128, switch_time = None):
        self.__host = host
        self.__port = port
        self.frame = unichr(9166).encode('utf-8')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.MAX_BLOCK_SIZE = buffsize
        self.timeout = timeout
        self.socket.settimeout(self.timeout)
        self.in_lifo = deque([])
        self.out_lifo = deque([])
        self.split_value = split_value
        self.switch_time = switch_time

    def connect(self):
        self.socket.connect((self.__host,self.__port))

    def send(self, message):
        # self.socket.sendall(message + self.frame)
        request = message + self.frame
        while request:
            try:
                send = self.socket.send(request)
                request = request[send:]
            except Exception as e:
                print(e)
                # print('send timeout error ' + str(len(self.in_lifo)))
                continue
            request = request[self.split_value:]

    def recv(self):
        # return self.socket.recv(self.MAX_BLOCK_SIZE)[:-3]
        response = ''
        while response[-3:] != self.frame:
            try:
                response += self.socket.recv(self.MAX_BLOCK_SIZE)
            except Exception as e:
                print(e)
                continue
                # print(response)
                # print('recv timeout error '  + str(len(self.in_lifo)) + ' ' + str(len(self.out_lifo)))
                # break
        return response[:-3]

    # def recv(self):
    #     if len(self.in_lifo) is not 0:
    #         return self.in_lifo.popleft()
    #     else:
    #         received = False
    #         while not received:
    #             r2r, r2w, err = select.select([self.socket],[self.socket],[], self.switch_time)
    #             if len(r2r) > 0:
    #                 print ('recv r2w')
    #                 received = True
    #                 return self.bare_recv()
    #             if len(r2w) > 0 and len(self.out_lifo) > 0:
    #                 print('recv r2r')
    #                 self.bare_send(self.out_lifo.popleft())


    # def send(self, message):
    #     if len(self.out_lifo) > 0:
    #         self.out_lifo.append(message)
    #         request = self.out_lifo.popleft()
    #     else:
    #         request = message
    #     sended = False
    #     while not sended:
    #         print('send')
    #         r2r, r2w, err = select.select([self.socket],[self.socket],[], self.switch_time)
    #         if len(r2w) > 0:
    #             print ('send r2w')
    #             self.bare_send(request)
    #             sended = True
    #         if len(r2r) > 0:
    #             print ('send r2r')
    #             self.in_lifo.append(self.bare_recv())

    def close(self):
        self.socket.close()
