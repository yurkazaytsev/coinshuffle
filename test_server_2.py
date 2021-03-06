import unittest
import time
from random import (randint, shuffle)
from crypto import Crypto
from messages import Messages
from mailbox import Mailbox
import socket
import threading

from ecdsa.util import number_to_string
import ecdsa
from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push, msg_magic)

class protocolThread(threading.Thread):

    def __init__(self, host, port, vk, sk):
        threading.Thread.__init__(self)
        self.messages = Messages()
        self.mailbox = Mailbox(host,port,timeout  = None)
        self.vk = vk
        self.sk = sk
        self.session = None
        self.number = None
        self.number_of_players = None
        self.players = {}

    def run(self):
        crypto = Crypto()
        crypto.generate_key_pair()
        enc_key = crypto.export_public_key()
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
        req = self.mailbox.recv()
        self.messages.packets.ParseFromString(req)
        phase = self.messages.get_phase()
        number = self.messages.get_number()
        time.sleep(1)
        if phase == 1 and number > 0:
            print("player #" + str(self.number) + " is about to share verification key with " + str(number) +" players.\n")
            self.number_of_players = number
            #Share the keys
            self.messages.clear_packets()
            self.messages.packets.packet.add()
            self.messages.packets.packet[-1].packet.from_key.key = self.vk
            self.messages.packets.packet[-1].packet.session = self.session
            self.messages.packets.packet[-1].packet.number = self.number
            shared_key_message = self.messages.packets.SerializeToString()
            messages = self.mailbox.share(shared_key_message, self.number, self.number_of_players)
            self.messages.packets.ParseFromString(messages)
            self.players = {packet.packet.number:str(packet.packet.from_key.key) for packet in self.messages.packets.packet}
        print("Player #" + str(self.number) + " got players " + str(self.players)+ '\n')
        # crypto = Crypto()
        # crypto.generate_key_pair()
        # enc_key = crypto.export_public_key()
        # clear old messages
        self.messages.clear_packets()
        # add encrytion key
        self.messages.add_encryption_key(enc_key, None)
        # self.messages.add_str('x')
        self.messages.packets.packet[-1].packet.from_key.key = self.players[self.number]
        self.messages.packets.packet[-1].packet.session = self.session
        self.messages.packets.packet[-1].packet.number = self.number
        # self.messages.packets.packet[-1].signature.signature = '1234'
        # for the packet
        # self.messages.form_last_packet(self.sk, self.session, self.number, self.vk, None)
        # # share the keys
        outcome_message = self.messages.packets.SerializeToString()
        print("Player " + str(self.number) + " is about to share encrytion key.\n" )
        msgs = self.mailbox.share(outcome_message, self.number, self.number_of_players)
        # self.mailbox.send(outcome_message)
        # print(self.mailbox.send(outcome_message))
        # # parse the result
        # try:
        #     self.messages.packets.ParseFromString(msgs)
        # except DecodeError:
        #     print('Decoding Error!')
        # # get encryption keys
        # if (self.messages.encryption_keys_count() == self.number_of_players):
        #     self.encryption_keys = self.messages.get_encryption_keys()
        #     print('Player '+ str(self.number) + ' recieved all keys for test\n')
        # else:
        #     raise Exception('Not get encryption keys!')
        #
        time.sleep(10)
        self.mailbox.close()

HOST = "localhost"
PORT = 8080

G = generator_secp256k1
_r  = G.order()
number_of_players = 3
players_pvks = [ecdsa.util.randrange( pow(2,256) ) %_r   for i in range(number_of_players) ]
players_ecks = [EC_KEY(number_to_string(pvk ,_r))  for pvk in players_pvks]
players_pks =[eck.get_public_key(True) for eck in players_ecks]
players = dict(zip(range(number_of_players),players_pks))

playerThreads = [protocolThread(HOST,PORT,players[player], players_ecks[player]) for player in players]
for thread in playerThreads:
    thread.start()
