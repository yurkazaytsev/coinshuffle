from lib.bitcoin import (
    generator_secp256k1, point_to_ser, public_key_to_p2pkh, EC_KEY,
    bip32_root, bip32_public_derivation, bip32_private_derivation, pw_encode,
    pw_decode, Hash, public_key_from_private_key, address_from_private_key,
    is_valid, is_private_key, xpub_from_xprv, is_new_seed, is_old_seed,
    var_int, op_push, pubkey_from_signature, msg_magic)


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

    def make_transaction(self, amount, fee, inputs, outputs, changes):
        return "transaction go here"

    def check_double_spend(t):
        "Double Spend Check should go here"
        return true

    def verify_signature(self, sig, message, vk):
        pk, compressed = pubkey_from_signature(sig,Hash(msg_magic(message)))
        address_from_signature = public_key_to_p2pkh(point_to_ser(pk.pubkey.point,compressed))
        address_from_vk = self.address(vk)
        return address_from_signature == address_from_signature
