from ecdsa.util import number_to_string
import ecdsa
from lib.bitcoin import (generator_secp256k1, point_to_ser, EC_KEY)

# For now it is ECIES encryption/decryption methods from bitcoin lib. It should be updated for something else i suppose.

class Crypto(object):

    def __init__(self):
        self.G = generator_secp256k1
        self._r  = self.G.order()

    def generate_key_pair(self):
        self.private_key = ecdsa.util.randrange( pow(2,256) ) %self._r
        self.eck = EC_KEY(number_to_string(self.private_key, self._r))
        self.public_key = point_to_ser(self.private_key*self.G,True)

    def export_public_key(self):
        """
        serialization of public key
        """
        return self.public_key.encode('hex')

    def encrypt(self, message, pubkey):
        return self.eck.encrypt_message(message, pubkey.decode('hex'))

    def decrypt(self, message):
        return self.eck.decrypt_message(message)



# crypta1 = Crypto()
# crypta2 = Crypto()
#
# crypta1.generate_key_pair()
# crypta2.generate_key_pair()
#
# msg = "Hello World!"
# pub1 = crypta1.export_public_key()
# ciph = crypta2.encrypt(msg ,pub1)
#
# crypta1.decrypt(ciph) == msg
