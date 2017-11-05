import socket
import unittest
from messages import Messages
import protobuf.message_pb2 as message_factory

HOST = "localhost"
PORT = 8080
framing_end = unichr(9166).encode('utf-8')
buf_size = 2**14

class TestServer(unittest.TestCase):

    def test_1000_server_conncetion(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
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
        s.close()

    def test_001_broadcast(self):
        # make a sockets for 3 player
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((HOST,PORT))
        s1.settimeout(5)

        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((HOST,PORT))
        s2.settimeout(5)

        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3.connect((HOST,PORT))
        s3.settimeout(5)
        # define some keys
        vk1 = "verification key 1"
        vk2 = "verification key 2"
        vk3 = "verification key 3"
        # make a messages factories for players
        mf1 = Messages()
        mf2 = Messages()
        mf3 = Messages()
        # make an handshake messages
        pack1 = mf1.packets.packet.add()
        pack1.packet.from_key.key = vk1
        req1 = mf1.packets.SerializeToString() + framing_end

        pack2 = mf2.packets.packet.add()
        pack2.packet.from_key.key = vk2
        req2 = mf2.packets.SerializeToString() + framing_end

        pack3 = mf3.packets.packet.add()
        pack3.packet.from_key.key = vk3
        req3 = mf3.packets.SerializeToString() + framing_end
        # send outcoming messages
        s1.send(req1)
        s2.send(req2)
        s3.send(req3)
        # receive the outputs
        res1 = s1.recv(buf_size)
        res2 = s2.recv(buf_size)
        res3 = s3.recv(buf_size)
        # unparse messages
        mf1.packets.ParseFromString(res1[:-3])
        mf2.packets.ParseFromString(res2[:-3])
        mf3.packets.ParseFromString(res3[:-3])
        # Get sessions and numbers
        session1 = mf1.packets.packet[-1].packet.session
        number1 = mf1.packets.packet[-1].packet.number
        session2 = mf2.packets.packet[-1].packet.session
        number2 = mf2.packets.packet[-1].packet.number
        session3 = mf3.packets.packet[-1].packet.session
        number3 = mf3.packets.packet[-1].packet.number
        print(number1, session1)
        print(number2, session2)
        print(number3, session3)
        # Assert numbers
        self.assertTrue(number1 in [1,2,3])
        self.assertTrue(number2 in [1,2,3])
        self.assertTrue(number3 in [1,2,3])
        self.assertTrue(len(set([number1, number2, number3])) == 3)
        # assert sessions
        self.assertTrue(len(set([session1, session2, session3]))==3)
        #receive Announcement
        an1 = s1.recv(buf_size)
        an2 = s2.recv(buf_size)
        an3 = s3.recv(buf_size)
        self.assertTrue(an1 == an2 == an3)
        # one brodcast
        mf1.clear_packets()
        mf1.packets.packet.add()
        mf1.packets.packet[-1].packet.session = session1
        mf1.packets.packet[-1].packet.number = number1
        mf1.packets.packet[-1].packet.from_key.key = vk1
        mf1.packets.packet[-1].signature.signature = '12345123123123123'
        req = mf1.packets.SerializeToString() + framing_end
        s1.send(req)
        # others should receive it
        res1 = s1.recv(buf_size)
        res2 = s2.recv(buf_size)
        res3 = s3.recv(buf_size)
        # Everyone should receive the same
        self.assertTrue(res1 == res2 == res3 == req)

    def test_002_unicast(self):
        # make a sockets for 3 player
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((HOST,PORT))
        s1.settimeout(5)

        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((HOST,PORT))
        s2.settimeout(5)

        s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s3.connect((HOST,PORT))
        s3.settimeout(5)
        # define some keys
        vk1 = "verification key 1"
        vk2 = "verification key 2"
        vk3 = "verification key 3"
        # make a messages factories for players
        mf1 = Messages()
        mf2 = Messages()
        mf3 = Messages()
        # make an handshake messages
        pack1 = mf1.packets.packet.add()
        pack1.packet.from_key.key = vk1
        req1 = mf1.packets.SerializeToString() + framing_end

        pack2 = mf2.packets.packet.add()
        pack2.packet.from_key.key = vk2
        req2 = mf2.packets.SerializeToString() + framing_end

        pack3 = mf3.packets.packet.add()
        pack3.packet.from_key.key = vk3
        req3 = mf3.packets.SerializeToString() + framing_end
        # send outcoming messages
        s1.send(req1)
        s2.send(req2)
        s3.send(req3)
        # receive the outputs
        res1 = s1.recv(buf_size)
        res2 = s2.recv(buf_size)
        res3 = s3.recv(buf_size)
        # unparse messages
        mf1.packets.ParseFromString(res1[:-3])
        mf2.packets.ParseFromString(res2[:-3])
        mf3.packets.ParseFromString(res3[:-3])
        # Get sessions and numbers
        session1 = mf1.packets.packet[-1].packet.session
        number1 = mf1.packets.packet[-1].packet.number
        session2 = mf2.packets.packet[-1].packet.session
        number2 = mf2.packets.packet[-1].packet.number
        session3 = mf3.packets.packet[-1].packet.session
        number3 = mf3.packets.packet[-1].packet.number
        print(number1, session1)
        print(number2, session2)
        print(number3, session3)
        # Assert numbers
        self.assertTrue(number1 in [1,2,3])
        self.assertTrue(number2 in [1,2,3])
        self.assertTrue(number3 in [1,2,3])
        self.assertTrue(len(set([number1, number2, number3])) == 3)
        # assert sessions
        self.assertTrue(len(set([session1, session2, session3]))==3)
        #receive Announcement
        an1 = s1.recv(buf_size)
        an2 = s2.recv(buf_size)
        an3 = s3.recv(buf_size)
        self.assertTrue(an1 == an2 == an3)
        # one uncast
        mf1.clear_packets()
        mf1.packets.packet.add()
        mf1.packets.packet[-1].packet.session = session1
        mf1.packets.packet[-1].packet.number = number1
        mf1.packets.packet[-1].packet.from_key.key = vk1
        mf1.packets.packet[-1].packet.to_key.key = vk3
        req = mf1.packets.SerializeToString() + framing_end
        s1.send(req)
        # others should receive it
        res3 = s3.recv(buf_size)
        # player 3 should recieve the message
        self.assertTrue(req == res3)

suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)
unittest.TextTestRunner(verbosity=2).run(suite)
