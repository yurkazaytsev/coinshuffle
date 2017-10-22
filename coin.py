from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push)


class Coin(object):
    """
    it is a class for interaction with blockchain interaction
    will be fake functions for now
    """

    def sufficient_funds(self, address, amount):
        """
        System should check for sufficient funds here.
        returns true for now
        """
        return True

    def address(self, vk):
        return public_key_to_p2pkh(vk)
