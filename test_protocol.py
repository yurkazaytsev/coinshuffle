import unittest
import sys
import time
import pprint
from random import (randint, shuffle)
from coin import Coin
from crypto import Crypto
from messages import Messages
from mailbox import Mailbox
from phase import Phase
from fake_server import fakeServerThread
import socket
import threading
from coin_shuffle import Round

class fakeLogChannel(object):

    def __init__(self):
        pass

    def send(self, message):
        print(message)

class protocolThread(threading.Thread):
    """
    This class emulate thread with protocol run
    """
    def __init__(self, host, port, vk, amount, fee, sk, addr_new, change):
        threading.Thread.__init__(self)
        self.messages = Messages()
        self.mailbox = Mailbox(host,port,timeout = None)
        self.vk = vk
        self.session = None
        self.number = None
        self.number_of_players = None
        self.players = {}
        self.amount = amount
        self.fee = fee
        self.sk = sk
        self.addr_new = addr_new
        self.change = change

    def run(self):
        self.mailbox.connect()
        self.messages.make_greeting(self.vk)
        msg = self.messages.packets.SerializeToString()
        self.mailbox.send(msg)
        req = self.mailbox.recv()
        self.messages.packets.ParseFromString(req)
        self.session = self.messages.packets.packet[-1].packet.session
        self.number = self.messages.packets.packet[-1].packet.number
        if self.session != '':
             print("Player #"  + str(self.number)+" get session number.\n")
        # Here is when announcment should begin
        verification_keys_stage_complete = False
        while not verification_keys_stage_complete:
            req = self.mailbox.recv()
            self.messages.packets.ParseFromString(req)
            session = self.messages.get_session()
            phase = self.messages.get_phase()
            number = self.messages.get_number()
            from_key = self.messages.get_from_key()
            if phase is not 1:
                if number > 0 and from_key != '':
                    self.players[number] = from_key
            else:
                if number > 0:
                    self.number_of_players = number
                    self.messages.clear_packets()
                    self.messages.packets.packet.add()
                    self.messages.packets.packet[-1].packet.session = self.session
                    self.messages.packets.packet[-1].packet.number = self.number
                    self.messages.packets.packet[-1].packet.from_key.key = self.vk
                    outcoming_message = self.messages.packets.SerializeToString()
                    self.mailbox.send(outcoming_message)
            if self.number_of_players:
                verification_keys_stage_complete = self.number_of_players == len(self.players)
        # req = self.mailbox.recv()
        # self.messages.packets.ParseFromString(req)
        # phase = self.messages.get_phase()
        # number = self.messages.get_number()
        # time.sleep(1)
        # # phase = 1
        # # number = self.number_of_players
        # # # self.messages.clear_packets()
        # # self.messages.packets.packet.add()
        # # self.messages.packets.packet[-1].packet.from_key.key = self.vk
        # # self.messages.packets.packet[-1].packet.session = self.session
        # # self.messages.packets.packet[-1].packet.number = self.number
        # # msgs = self.mailbox.share(self.messages.packets.SerializeToString(), self.number, number)
        #
        # if phase == 1 and number > 0:
        #     print("player #" + str(self.number) + " is about to share verification key with " + str(number) +" players.\n")
        #     self.number_of_players = number
        #     #Share the keys
        #     self.messages.clear_packets()
        #     self.messages.packets.packet.add()
        #     self.messages.packets.packet[-1].packet.from_key.key = self.vk
        #     self.messages.packets.packet[-1].packet.session = self.session
        #     self.messages.packets.packet[-1].packet.number = self.number
        #     shared_key_message = self.messages.packets.SerializeToString()
        #     messages = self.mailbox.share(shared_key_message, self.number, self.number_of_players)
        #     self.messages.packets.ParseFromString(messages)
        #     self.players = {packet.packet.number:str(packet.packet.from_key.key) for packet in self.messages.packets.packet}
        # print(str(self.players)+ '\n')
        # # if self.players:
        # #     print('player #' +str(self.number)+ " get " + str(len(self.players)))

        coin = Coin()
        crypto = Crypto()
        log_chan = fakeLogChannel()
        begin_phase = Phase('Announcement')
        # Make Round
        protocol = Round(
            coin,
            crypto,
            self.messages,
            self.mailbox,
            log_chan,
            self.session,
            begin_phase,
            self.amount ,
            self.fee,
            self.sk,
            self.players,
            self.addr_new,
            self.change)
        protocol.protocol_definition()
        time.sleep(10)
        self.mailbox.close()
#
from ecdsa.util import number_to_string
import ecdsa
from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push, msg_magic)

from coin_shuffle import Round
# Here is a host and port for cashsuffle server
HOST = "localhost"
PORT = 8080
pp = pprint.PrettyPrinter(indent=4)

class TestProtocol(unittest.TestCase):

    def test_000_positive_test(self):
        begin_phase = Phase('Announcement')
        amount = 1000
        fee = 1
        # generate fake signing keys
        G = generator_secp256k1
        _r  = G.order()
        number_of_players = 3
        players_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_ecks = [EC_KEY(number_to_string(pvk ,_r))  for pvk in players_pvks]
        players_new_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_change_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_changes = [ public_key_to_p2pkh(point_to_ser(pvk*G, True)) for pvk in players_change_pvks ]
        players_new_addresses = [ public_key_to_p2pkh(point_to_ser(pvk*G, True)) for pvk in players_new_pvks]
        players_pks =[eck.get_public_key(True) for eck in players_ecks]
        players = dict(zip(range(number_of_players),players_pks))
        print("\n")
        # serverThread = fakeServerThread(HOST, PORT, number_of_players = number_of_players)
        # serverThread.start()
        #( host, port, vk, amount, fee, sk, addr_new, change)
        playerThreads = [protocolThread(HOST,PORT,players[player],amount,fee,players_ecks[player], players_new_addresses[player], players_changes[player]) for player in players]
        for thread in playerThreads: thread.start()
        # serverThread.join()
        self.assertTrue(True)


suite = unittest.TestLoader().loadTestsFromTestCase(TestProtocol)
unittest.TextTestRunner(verbosity=2).run(suite)
