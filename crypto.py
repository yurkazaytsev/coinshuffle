import re

# from ecdsa.util import number_to_string
# import ecdsa
# from lib.bitcoin import (
#     generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
#     bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
#     pw_decode, Hash, public_key_from_private_key, address_from_private_key,
#     is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
#     var_int, op_push)


# def int_to_bytes(val, num_bytes):
#     return [(val & (0xff << pos*8)) >> pos*8 for pos in range(num_bytes)]
#
# class MockAddress(object):
#
#     def __init__(self, addr):
#         self.addr =str(addr)
#
#     def __hash__(self):
#         return self.addr.__hash__()
#
#     def __str__(self):
#         return self.addr
#
#
# class MockVerificationKey(object):
#
#     def __init__(self, index):
#         pattern = re.compile('^vk\[[1-9]+\]$')
#         if type(index) == int:
#             self.index = index
#         elif type(index) == str:
#             if pattern.match(index):
#                 self.index = int(index[3:-1])
#
#     def verify(self, payload, signature):
#         pass
#
#     def address(self):
#         return MockAddress(self.index)
#
#     def __str__(self):
#         return "vk[" + str(self.index) + "]"
#
#     def __hash__(self):
#         return self.index
#
# class MockSingingKey(object):
#
#     def __init__(self, index):
#         __G = generator_secp256k1
#         _r  = G.order()
#         pvk = ecdsa.util.randrange( pow(2,256) ) %_r
#         self.pub = pvk*G
#         self.eck = EC_KEY(number_to_string(pvk,_r))
#         # pattern = re.compile('^sk\[[1-9]+\]$')
#         # if type(index) == int:
#         #     self.index = index
#         # elif type(index) == str:
#         #     if pattern.match(index):
#         #         self.index = int(index[3:-1])
#
#     def verification_key(self):
#         return self.pub
#
#     def __str__(self):
#         return
#
#     def __hash__(self):
#         return self.index
#
#     def sign(self, message):# 4-bytes array for this mock only
#         return int_to_bytes(hash(message) + self.index,4)

class MockEncryptionKey(object):

    def __init__(self, index):
        pattern = re.compile('^ek\[[1-9]+\]$')
        if type(index) == int:
            self.index = index
        elif type(index) == str:
            if pattern.match(index):
                self.index = int(index[3:-1])

    def encrypt(self, m):
        decrypted = "~decrypt["+ str(self.index) +"]"
        if m.endswith(decrypted):
            return m[0: -len(decrypted)]
        return m + "~encrypt["+ str(self.index) +"]"

    def __str__(self):
        return "ek["+ str(self.index) +"]"

    def __hash__(self):
        return self.index

class MockDecryptionKey(object):

    def __init__(self, index):
        pattern = re.compile('dk\[[1-9]+\]$')
        if type(index) == int:
            self.index = index
            self.key = MockEncryptionKey(index)
        elif type(index) == str:
            if pattern.match(index):
                self.index = int(index[3:-1])

        self.key = MockEncryptionKey(self.index)

    def encryption_key(self):
        return self.key

    def decrypt(self, m):
        encrypted = "~encrypt["+ str(self.index) +"]"
        if m.endswith(encrypted):
            return m[0: -len(encrypted)]
        return m + "~decrypt["+ str(self.index) +"]"

    def __str__(self):
        return "dk["+ str(self.index) +"]"

class Crypto(object):
    """
    Mock class for the real crypto system
    """
    def __init__(self):
        self.signing_key_counter = 1;
        self.decryption_key_counter = 1;


    def mock_decryption_key(self, index):
        return MockDecryptionKey(index)

    # def mock_singin_key(self, index):
    #     pass

    # def make_signing_key(self):
    #     self.signing_key_counter += 1
    #     return self.mock_singin_key(self.signing_key_counter))
    #     pass

    def make_decryption_key(self):
        self.decryption_key_counter += 1
        return self.mock_decryption_key(self.decryption_key_counter)
