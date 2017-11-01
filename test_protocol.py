import unittest
import sys
import pprint
from random import (randint, shuffle)
from coin import Coin
from crypto import Crypto
from messages import Messages
from mailbox import Mailbox
from phase import Phase
import threading


class protocolThread(threading.Thread):
    def __init__(self, host, port, vk):
        threading.Thread.__init__(self)
        self.messages = Messages()
        self.mailbox = Mailbox(host,port)
        self.vk = vk
        self.session = None
        self.number = None

    def run(self):
        self.mailbox.connect()
        self.messages.make_greeting(self.vk)
        msg = self.messages.packets.SerializeToString()
        self.mailbox.send(msg)
        req = self.mailbox.recv()
        self.messages.packets.ParseFromString(req)
        self.session = self.messages.packets.packet[-1].packet.session
        self.number = self.messages.packets.packet[-1].packet.number
        pp.pprint("session: " + self.session + " number: " + str(self.number))
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
        number_of_players = 5
        players_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_ecks = [EC_KEY(number_to_string(pvk ,_r))  for pvk in players_pvks]
        players_new_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_change_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
        players_changes = [ public_key_to_p2pkh(point_to_ser(pvk*G, True)) for pvk in players_change_pvks ]
        players_new_addresses = [ public_key_to_p2pkh(point_to_ser(pvk*G, True)) for pvk in players_new_pvks]
        players_pks =[eck.get_public_key(True) for eck in players_ecks]
        players = dict(zip(range(number_of_players),players_pks))
        print("")
        # for i in players: print(players[i])
        playerThreads = [protocolThread(HOST,PORT,players[player]) for player in players]
        for thread in playerThreads: thread.start()
        self.assertTrue(True)


suite = unittest.TestLoader().loadTestsFromTestCase(TestProtocol)
unittest.TextTestRunner(verbosity=2).run(suite)
