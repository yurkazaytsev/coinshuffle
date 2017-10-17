import re

class MockVerificationKey(object):

    def __init__(self, index):
        pattern = re.compile('^vk\[[1-9]+\]$')
        if type(index) == int:
            self.index = index
        elif type(index) == str:
            if pattern.match(index):
                self.index = int(index[3:-1])

    # def verify(self, payload, signature):



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

    def hash_code(self):
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

    def mock_singin_key(self, index):
        pass

    def make_signing_key(self):
        self.signing_key_counter += 1
        return self.mock_singin_key(self.signing_key_counter))
        pass

    def make_decryption_key(self):
        self.decryption_key_counter += 1
        return self.mock_decryption_key(self.decryption_key_counter))
