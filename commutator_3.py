import socket
import threading
import Queue

class Commutator(threading.Thread):
    """
    Class for decoupling of send and recv ops.
    """
    def __init__(self, income, outcome, logger = None, buffsize = 4096, timeout = 0):
        super(Commutator, self).__init__()
        self.income = income
        self.outcome = outcome
        self.logger = logger
        self.alive = threading.Event()
        self.alive.set()
        self.socket = None
        self.frame = unichr(9166).encode('utf-8')
        self.MAX_BLOCK_SIZE = buffsize
        self.timeout = timeout

    def debug(self, obj):
        if logger:
            logger.put(str(obj))

    def run(self):
        while self.alive.isSet():
            try:
                msg = self.income.get(True, 0.1)
                self._send(msg)
                self.debug('send!')
            except (Queue.Empty, socket.error) as e:
                try:
                    self.outcome.put_nowait(self._recv())
                    self.debug('recv')
                except (Queue.Empty, socket.error) as e:
                    continue

    def join(self, timeout=None):
        self.socket.close()
        self.alive.clear()
        threading.Thread.join(self, timeout)


    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.socket.settimeout(self.timeout)
            self.debug('connected')
        except IOError as e:
            self.logger.put(str(e))

    def _send(self, msg):
        msg += self.frame
        self.socket.send(msg)

    def close(self):
        self.socket.close()
        self.debug('closed')

    def _recv(self):
        response = ''
        while response[-3:] != self.frame:
            response += self.socket.recv(self.MAX_BLOCK_SIZE)
        return response[:-3]

class Channel(Queue.Queue):
    """
    simple Queue wrapper for using recv and send
    """
    def send(self, message):
        self.put(message)

    def recv(self):
        return self.get()

# test
# import Queue
from messages import Messages

inchan = Channel() #Queue.Queue()
outchan = Channel() #Queue.Queue()
logger = Channel() #Queue.Queue()

x = Commutator(inchan, outchan, logger = logger)
x.connect('localhost',8080)
x.start()
# x.close()
# x.join()
z = Messages()
z.make_greeting('1111111111111111111111111')
x.send(z.packets.SerializeToString())
outchan.get(True, 0.01)

x.socket.send(z.packets.SerializeToString())
x.socket.send(unichr(9166).encode('utf-8'))
inchan.send(z.packets.SerializeToString())
# inchan.get()
print(outchan.get(True, 0.1))
x.socket.getsockopt()
x.close()
x.join()

x.join()
logger.recv()
