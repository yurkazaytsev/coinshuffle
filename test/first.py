#
from imp import reload

import sys
from random import (randint, shuffle)
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
reload(sys.modules['coin_shuffle'])
# This file is just for Tests
session = 'usid'
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
temp =''
hash_values = ''
# new_addreses_fake = [str(i) for i in range(number_of_players)]

# Channels definition
# This is an array for incoming channels of players
in_channels = [goless.chan() for i in range(number_of_players)]
# This is an array for outcoming channels of players
out_channels = [goless.chan() for i in range(number_of_players)]
# single log channel
log_chan = goless.chan()
# broadcasting channel

# Here is a players client running protocol
def go_player(i):
    z =  Round(Coin(),
          Crypto(),
          Messages(),
          in_channels[i],
          out_channels[i],
          log_chan,
          session,
          begin_phase,
          amount,
          fee,
          players_ecks[i],
          players,
          players_new_addresses[i],
          players_changes[i])
    z.protocol_definition()
    in_channels[i].close()
    out_channels[i].close()
# Here is collector. It listen to all channels
def collector():
    global temp, hash_values
    # Phase 1
    for chan in out_channels:
        temp += chan.recv()
    for chan in in_channels:
        chan.send(temp)
    # Phase 2
    for i in range(number_of_players - 1):
        in_channels[i + 1].send(out_channels[i].recv())
    addrs = out_channels[-1].recv()
    # Phase 3
    for chan in in_channels:
        chan.send(addrs)
    # Phase 4
    for chan in out_channels:
        hash_values += chan.recv()
    for chan in in_channels:
        chan.send(hash_values)
    log_chan.close()


for i in range(number_of_players): goless.go(go_player,i)
goless.go(collector)
for msg in log_chan:
    print(msg)


# msgs = Messages()
# msgs.packets.ParseFromString(hash_values)
# msgs.packets
#
# encryption_keys = msgs.get_encryption_keys()
# encryption_keys
#
# hash(str([encryption_keys[players[i]] for i in range(number_of_players)]) + str(players_new_addresses))
#
# players_new_addresses
# hash(str(players_new_addresses))
# # tempo
# set([1,2,3,4,5])
