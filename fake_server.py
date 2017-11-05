from messages import Messages
import socket
import threading
from thread import start_new_thread

class fakeServerThread(threading.Thread):
    """
    This class emulate server behaviour
    """
    def __init__(self, host, port, number_of_players=5, buffsize=2**15,timeout = 10):
        threading.Thread.__init__(self)
        self.frame = unichr(9166).encode('utf-8')
        self.buf_size = buffsize
        self.number_of_players = number_of_players
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(timeout)
        self.socket.bind((self.host, self.port))
        self.socket.listen(number_of_players)
        self.pool = {}
        self.connections_count = 0
        self.pool_formed = False

    def remove(self, addr):
        if addr in self.pool:
            del self.pool[addr]

    def broadcast_message(self, message):
        for addr in self.pool:
            self.pool[addr]['connection'].send(message)

    def unicast_message(self, message, key):
        recepient = [self.pool[addr]['connection'] for addr in self.pool if self.pool[addr]['key'] == key][0]
        if recepient:
            recepient.send(messages)

    def clientThread(self, conn, addr, buffsize):
        msgs = Messages()
        while True:
            try:
                message = conn.recv(buffsize)
                if message:
                    msgs.packets.ParseFromString(message[:-3])
                    session = msgs.get_session()
                    number = msgs.get_number()
                    from_key = msgs.get_from_key()
                    to_key = msgs.get_to_key()
                    if session=='' and number==0 and from_key!='':
                        if not self.pool[addr]['key']:
                            self.pool[addr]['key'] = from_key
                            msgs.clear_packets()
                            msgs.packets.packet.add()
                            msgs.packets.packet[-1].packet.session = self.pool[addr]['session']
                            msgs.packets.packet[-1].packet.number = self.pool[addr]['number']
                            msg = msgs.packets.SerializeToString() + self.frame
                            conn.send(msg)
                            # time.sleep(1)
                            if len([1 for address in self.pool if self.pool[address]['key']]) == self.number_of_players:
                                msgs.clear_packets()
                                msgs.packets.packet.add()
                                msgs.packets.packet[-1].packet.phase = 1
                                msgs.packets.packet[-1].packet.number = self.number_of_players
                                self.broadcast_message(msgs.packets.SerializeToString()+self.frame)
                    if session!='' and number!=0 and from_key!='' and to_key =='':
                        self.broadcast_message(message)
                    if session!='' and number!=0 and from_key!='' and to_key !='':
                        self.unicast_message(message,to_key)

                else:
                    pass
            except Exception as e:
                continue

    def run(self):
        while True:
            # conn, addr = self.socket.accept()
            if not self.connections_count == self.number_of_players:
                conn, addr = self.socket.accept()
                print(addr[0] + ':' + str(addr[1]) + " connected\n")
                self.connections_count += 1
                self.pool[addr]={}
                self.pool[addr]['connection'] = conn
                self.pool[addr]['number'] = self.connections_count
                self.pool[addr]['session'] = str(self.pool[addr]['number']) * 3
                self.pool[addr]['key'] = None
                start_new_thread(self.clientThread,(conn,addr, self.buf_size))
            elif not self.pool_formed:
                self.pool_formed =True
                print('pool of players in formed')
                self.pool_formed =True
        conn.close()
        self.socket.close()

    def stop(self):
        self.socket.close()
