from random import randint
from phase import Phase
from coin import Coin
from crypto import Crypto

from ecdsa.util import number_to_string
import ecdsa
from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push)

class BlameException(Exception):
    pass

# class Coin_Shuffle(object):
#     """
#     Abstract implementation of CoinShuffle in python.
#     http://crypsys.mmci.uni-saarland.de/projects/CoinShuffle/coinshuffle.pdf
#     """
#
#     def __init__(self, messages, crypto, coin):
#         """
#         messages - Object that knows how to create and copy messages.
#         crypto - Connects to the cryptography.
#         coin - Connects us to the Bitcoin or other cryptocurrency netork.
#         """
#         if messages and crypto and coin:
#             self.__messages = messages
#             self.__crypto = crypto
#             self.__coin = coin
#         else:
#             raise ValueError('crypto or coin or messages system missing')

class Round(object):
    """
    A single round of the protocol. It is possible that the players may go through
    several failed rounds until they have eliminated malicious players.
    """

    def __init__(self,coin, crypto, phase, amount, fee, sk, players, addr_new, change):

        if coin:
            self.__coin = coin
        else:
            raise ValueError('No coin object')

        if crypto:
            self.__crypto = crypto
        else:
            raise ValueError('No crypto object')


        self.__phase = phase
        #The amount to be shuffled.
        if amount >= 0:
            self.__amount = amount
        else:
            raise ValueError('wrong amount value')
        # The miner fee to be paid per player.
        if fee >= 0:
            self.__fee = fee
        else:
            raise ValueError('wrong fee value')
        # My signing private key
        self.__sk = sk
        # Which player am I?
        self.__me = None
        # The number of players.
        self.__N = None
        # The players' public keys
        if type(players) is dict:
            self.__playeres = players
            # The number of players.
            self.__N = len(players) # Do we realy need it?
        else:
            raise TypeError('Players should be stored in dict object')
        # My verification public key, which is also my identity.
        self.__vk = sk.get_public_key(True) # True here means that compression is on
        # decryption key
        if self.__N == len(set(players.values())):
            if self.__vk in players.values():
                self.__me = { v : k for k, v in players.iteritems()}[self.__vk]
            else:
                raise ValueError('My public key is not in players list')
        else:
            raise ValueError('Same public keys appears!')
        # decryption key
        self.__dk = None
        # This will contain the new encryption public keys.
        self.__encryption_keys = dict()
        # The set of new addresses into which the coins will be deposited.
        self.__new_addresses = None
        self.__addr_new = addr_new
        # My change address. (may be null).
        self.__change = change
        self.__signatures = dict()
        self.__mail_box = None

    def blame_insufficient_funds(self):
        addresses = [public_key_to_p2pkh(pk) for pk in players.values()]
        offenders = list()
        for player in players:
            address = public_key_to_p2pkh(players[player])
            if not self.__coin.sufficient_funds(address,self.__amount + self.__fee):
                offenders.append(player)
        if len(offenders) == 0:
            return
        else:
            self.__phase = "Blame"
            # TODO
            #
            # - broadcast blame phase
            # - sand a message for each player who have insufficietn funds
            raise BlameException('Insufficient funds')

    def broadcast_new_key(self ,change_addresses):
        dk = self.__crypto.make_decryption_key()
        # Broadcast the public key and store it in the set with everyone else's.
        self.__encryption_keys[self.__vk] = dk.encryption_key()
        change_addresses[self.__vk] = self.__change
        # make messages
        # broadcast messages
        return dk

    # In phase 1, everybody announces their new encryption keys to one another. They also
    # optionally send change addresses to one another. This function reads that information
    # from a message and puts it in some nice data structures.

    def read_announcements(self, messages, encryption_keys, change):
        pass

    def protocol_definition(self):

        if self.__amount <= 0:
            raise ValueError('wrong amount for transaction')

        # Phase 1: Announcement
        # In the announcement phase, participants distribute temporary encryption keys.
        self.__phase = 'Announcement'
        print ("Player " + str(self.__me + 1) + " begins CoinShuffle protocol " + " with " + str(self.__N) + " players.")
        # Check for sufficient funds.
        # There was a problem with the wording of the original paper which would have meant
        # that player 1's funds never would have been checked, but it's necessary to check
        # everybody.
        self.blame_insufficient_funds()
        print("Player " + str(me + 1) + " finds sufficient funds")
        # This will contain the change addresses.
        change_addresses = dict()
        self.__dk = self.broadcast_new_key(change_addresses)
        print("Player " + str(me + 1) + " has broadcasted the new encryption key.")
        # Now we wait to receive similar key from everyone else.
        announcement =  dict()
        #TO Reciver form multiple
        print("Player " + str( me + 1) + " is about to read announcements.")
        self.read_announcements(announcement, self.__encryption_keys, change_addresses)


# Here we generate the private keys of players
from random import randint

begin_phase = Phase('Announcement')
amount = 1000
fee = 1

G = generator_secp256k1
_r  = G.order()
coin = Coin
number_of_players = 10
players_ecks = [EC_KEY(number_to_string(ecdsa.util.randrange( pow(2,256) ) %_r ,_r))  for i in range(number_of_players) ]
me = randint(0,number_of_players-1)
my_eck = players_ecks[me]
players_pks =[eck.get_public_key(True) for eck in players_ecks]
players = dict(zip(range(number_of_players),players_pks))
sk  = my_eck
addr_new = 123123
change = 12312312

z  = Round(Coin(),Crypto(),begin_phase, amount, fee, sk, players, addr_new, change)

z.protocol_definition()
z.broadcast_decryption_key(dict())
z.__dict__
