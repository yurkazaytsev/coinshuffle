import unittest
import sys
import time
from coin import Coin
from crypto import Crypto
from messages import Messages
from commutator_thread import Commutator
from commutator_thread import Channel
from commutator_thread import ChannelWithPrint
from phase import Phase
import socket
import threading
from coin_shuffle import Round

# class fakeLogChannel(object):
#
#     def __init__(self, prefix =''):
#         self.prefix = prefix
#         pass
#
#     def send(self, message):
#         print(self.prefix + message + ".\n")

class protocolThread(threading.Thread):
    """
    This class emulate thread with protocol run
    """
    def __init__(self, host, port, vk, amount, fee, sk, addr_new, change):
        threading.Thread.__init__(self)
        self.messages = Messages()
        self.income = Channel()
        self.outcome = Channel()
        self.logger = ChannelWithPrint()
        self.commutator = Commutator(self.income, self.outcome, logger = self.logger)
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
        self.deamon = True
        self.commutator.connect(host, port)
        # self.commutator.start()

    def run(self):
        self.commutator.start()
        self.messages.make_greeting(self.vk)
        msg = self.messages.packets.SerializeToString()

        # self.commutator.send(msg)
        self.income.send(msg)
        # req = self.commutator.recv()
        req = self.outcome.recv()
        # print(req)
        self.messages.packets.ParseFromString(req)
        self.session = self.messages.packets.packet[-1].packet.session
        self.number = self.messages.packets.packet[-1].packet.number
        if self.session != '':
             # print("Player #"  + str(self.number)+" get session number.\n")
             self.logger.send("Player #"  + str(self.number)+" get session number.\n")
        # # Here is when announcment should begin
        # req = self.commutator.recv()
        req = self.outcome.recv()
        self.messages.packets.ParseFromString(req)
        phase = self.messages.get_phase()
        number = self.messages.get_number()
        if phase == 1 and number > 0:
            self.logger.send("player #" + str(self.number) + " is about to share verification key with " + str(number) +" players.\n")
            self.number_of_players = number
            #Share the keys
            self.messages.clear_packets()
            self.messages.packets.packet.add()
            self.messages.packets.packet[-1].packet.from_key.key = self.vk
            self.messages.packets.packet[-1].packet.session = self.session
            self.messages.packets.packet[-1].packet.number = self.number
            shared_key_message = self.messages.packets.SerializeToString()
            # self.commutator.send(shared_key_message)
            self.income.send(shared_key_message)
            messages = ''
            for i in range(number):
                # messages += self.commutator.recv()
                messages += self.outcome.recv()
            self.messages.packets.ParseFromString(messages)
            self.players = {packet.packet.number:str(packet.packet.from_key.key) for packet in self.messages.packets.packet}
        if self.players:
            print('player #' +str(self.number)+ " get " + str(len(self.players))+".\n")
        #
        coin = Coin()
        crypto = Crypto()
        self.messages.clear_packets()
        # log_chan = fakeLogChannel(prefix = str(self.number) + ": ")
        # self.commutator.debuger = log_chan
        begin_phase = Phase('Announcement')
        # Make Round
        protocol = Round(
            coin,
            crypto,
            self.messages,
            self.outcome,
            self.income,
            self.logger,
            self.session,
            begin_phase,
            self.amount ,
            self.fee,
            self.sk,
            self.players,
            self.addr_new,
            self.change)
        protocol.protocol_definition()
        # time.sleep(120)
        self.commutator.join()
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
# pp = pprint.PrettyPrinter(indent=4)

class TestProtocol(unittest.TestCase):

    def test_000_positive_test(self):
        begin_phase = Phase('Announcement')
        amount = 1000
        fee = 1
        # generate fake signing keys
        G = generator_secp256k1
        _r  = G.order()
        number_of_players = 4
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
        #( host, port, vk, amount, fee, sk, addr_new, change)
        playerThreads = [protocolThread(HOST,PORT,players[player],amount,fee,players_ecks[player], players_new_addresses[player], players_changes[player]) for player in players]
        # serverThread.start()
        for thread in playerThreads: thread.start()
        # serverThread.join()
        self.assertTrue(True)


suite = unittest.TestLoader().loadTestsFromTestCase(TestProtocol)
unittest.TextTestRunner(verbosity=2).run(suite)
