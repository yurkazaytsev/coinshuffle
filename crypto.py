from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Crypto(object):

    def __init__(self):
        self.__backend = default_backend()
        self.__padding = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH)
        self.__hashes = hashes.SHA256()

    def generate_key_pair(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.__backend)

        self.__public_key = self.__private_key.public_key()

    def public_key(self):
        """
        serialization of publik key
        """
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)

    def sign(self, message):
        return self.__private_key.sign(
            message,
            self.__padding,
            self.__hashes)

    def verify(self, signature, message):
        ## it raise exception for wrong signature
        return self.__public_key.verify(
            signature,
            message,
            self.__padding,
            self.__hashes )

#
#
#
# crypta =Crypto()
# crypta.generate_key_pair()
# crypta.public_key()
# message = 'Hello World'
# signature = crypta.sign(message)
#
#
# crypta.sign('Hello World')
