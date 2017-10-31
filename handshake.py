import socket
import unittest
from messages import Messages
import protobuf.message_pb2 as message_factory

# HOST = "localhost"
# PORT = 8080
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST,PORT))
#
# framing_end = unichr(9166).encode('utf-8')
# msgs = Messages()
# pack = msgs.packets.packet.add()
# pack.packet.from_key.key = 'some key for test'
# request = msgs.packets.SerializeToString() + framing_end
# s.sendall(request)
# response = s.recv(2048)
# msgs.packets.ParseFromString(response[:-3])
# print(msgs.packets)
HOST = "localhost"
PORT = 8080
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST,PORT))
# framing_end = unichr(9166).encode('utf-8')
# session = None
# number = None

class TestServer(unittest.TestCase):

    def test_server_conncetion(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        framing_end = unichr(9166).encode('utf-8')
        session = None
        number = None
        msgs = Messages()
        pack = msgs.packets.packet.add()
        pack.packet.from_key.key = 'some key for test'
        request = msgs.packets.SerializeToString() + framing_end
        s.sendall(request)
        response = s.recv(2048)
        msgs.packets.ParseFromString(response[:-3])
        self.assertIsInstance(msgs.packets, message_factory.Packets)
        session = msgs.packets.packet[-1].packet.session
        number = msgs.packets.packet[-1].packet.number
        self.assertIsNotNone(session)
        self.assertIsNotNone(number)
        self.assertIsInstance(session,str)
        self.assertIsInstance(number,int)
        self.assertTrue(len(session)>0)
        self.assertTrue(number > 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)
unittest.TextTestRunner(verbosity=2).run(suite)
