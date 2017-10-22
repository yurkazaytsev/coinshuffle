from random import randint
from phase import Phase
from coin import Coin
from crypto import Crypto
from messages import Messages
import goless


from ecdsa.util import number_to_string
import ecdsa
from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push, msg_magic)

from coin_shuffle import Round


# This file is just for Tests

begin_phase = Phase('Announcement')
amount = 1000
fee = 1
# generate fake signing keys
G = generator_secp256k1
_r  = G.order()
coin = Coin()
number_of_players = 10
players_ecks = [EC_KEY(number_to_string(ecdsa.util.randrange( pow(2,256) ) %_r ,_r))  for i in range(number_of_players) ]
me = randint(0,number_of_players-1)
my_eck = players_ecks[me]
players_pks =[eck.get_public_key(True) for eck in players_ecks]
players = dict(zip(range(number_of_players),players_pks))
sk  = my_eck
addr_new = "123123"
change = "12312312"
inchan = goless.chan()
outchan = goless.chan()
logchan = goless.chan()

def logger():
    while True:
        print(logchan.recv())

output_temp = None

def echo():
    global output_temp
    while True:
        output_temp = outchan.recv()
        # inchan.send(val)

goless.go(logger)
goless.go(echo)
z  = Round(Coin(),Crypto(),Messages(), inchan, outchan, logchan ,begin_phase, amount, fee, sk, players, addr_new, change)
z.protocol_definition()
zzz = Messages()
zzz.packets.ParseFromString(output_temp)
zzz.packets
