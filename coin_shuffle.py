class BlameException(Exception):
    pass

class Round(object):
    """
    A single round of the protocol. It is possible that the players may go through
    several failed rounds until they have eliminated malicious players.
    """

    def __init__(self, coin, crypto, messages, inchan, outchan, logchan , session , phase, amount, fee, sk, players, addr_new, change):

        if coin:
            self.__coin = coin
        else:
            raise ValueError('No coin object')

        if crypto:
            self.__crypto = crypto
        else:
            raise ValueError('No crypto object')

        self.__inchan = inchan
        self.__outchan = outchan
        self.__logchan = logchan
        self.__session = session

        if messages:
            self.__messages = messages

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
            self.__players = players
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
        # addresses = [public_key_to_p2pkh(pk) for pk in self.__players.values()]
        offenders = list()
        for player in self.__players:
            # address = public_key_to_p2pkh(players[player])
            address = self.__coin.address(self.__players[player])
            if not self.__coin.sufficient_funds(address,self.__amount + self.__fee):
                offenders.append(player)
        if len(offenders) == 0:
            return
        else:
            self.__phase = "Blame"
            for i in offenders:
                self.__messages.blame_insufficient_funds(offender)
                # self.__messages.sign_last_packet(self.__sk)
                self.__messages.form_last_packet(self.__sk, self.__session, self.__me, self.__vk, None)
                self.__outchan.send(self.__messages.packets.SerializeToString())
            raise BlameException('Insufficient funds')

    def broadcast_new_key(self ,change_addresses):
        dk = self.__crypto.generate_key_pair()
        # Broadcast the public key and store it in the set with everyone else's.
        self.__encryption_keys[self.__vk] = self.__crypto.export_public_key()
        change_addresses[self.__vk] = self.__change
        self.__messages.add_encryption_key(self.__encryption_keys[self.__vk], change_addresses[self.__vk])
        self.__messages.form_last_packet(self.__sk, self.__session, self.__me, self.__vk, None)
        # self.__messages.sign_last_packet(self.__sk)
        self.__outchan.send(self.__messages.packets.SerializeToString())
        # return dk

    # In phase 1, everybody announces their new encryption keys to one another. They also
    # optionally send change addresses to one another. This function reads that information
    # from a message and puts it in some nice data structures.

    def read_announcements(self, messages, encryption_keys, change):
        val = self.__inchan.recv()
        try:
            self.__messages.packets.ParseFromString(val)
        except DecodeError:
            self.__logchan('Decoding Error!')

        if (self.__messages.encryption_keys_count() == self.__N):
            self.__encryption_keys = self.__messages.get_encryption_keys()
            self.__logchan.send('Player '+ str(self.__me + 1) + ' recieved all keys for test')
        else:
            raise(BlameException)


    def encrypt_new_address(self):
        # Add our own address to the mix. Note that if me == N, ie, the last player, then no
        # encryption is done. That is because we have reached the last layer of encryption.
        encrypted = self.__addr_new
        for i in range(self.__N - 1, self.__me, -1):
            # Successively encrypt with the keys of the players who haven't had their turn yet.
            encrypted = self.__crypto.encrypt(encrypted, self.__encryption_keys[self.__players[i]])
        return encrypted

    def protocol_definition(self):

        if self.__amount <= 0:
            raise ValueError('wrong amount for transaction')

        # Phase 1: Announcement
        # In the announcement phase, participants distribute temporary encryption keys.
        self.__phase = 'Announcement'
        self.__logchan.send("Player " + str(self.__me + 1) + " begins CoinShuffle protocol " + " with " + str(self.__N) + " players.")
        # Check for sufficient funds.
        # There was a problem with the wording of the original paper which would have meant
        # that player 1's funds never would have been checked, but it's necessary to check
        # everybody.
        self.blame_insufficient_funds()
        self.__logchan.send("Player " + str(self.__me + 1) + " finds sufficient funds")
        # This will contain the change addresses.
        change_addresses = dict()
        # self.__dk = self.broadcast_new_key(change_addresses)

        self.broadcast_new_key(change_addresses)
        self.__logchan.send("Player " + str(self.__me + 1) + " has broadcasted the new encryption key.")
        # Now we wait to receive similar key from everyone else.
        announcement =  dict()
        #TO Reciver form multiple
        self.__logchan.send("Player " + str( self.__me + 1) + " is about to read announcements.")

        self.read_announcements(announcement, self.__encryption_keys, change_addresses)

        # Phase 2: Shuffle
        # In the shuffle phase, players go in order and reorder the addresses they have been
        # given by the previous player. They insert their own address in a random location.
        # Everyone has the incentive to insert their own address at a random location, which
        # sufficient to ensure that the result appears random to everybody.
        self.__phase = 'Shuffling'
        # self.__logchan.send("Player " + str( self.__me + 1) + " reaches phase 2: " + str(self.__encryption_keys))
        # clear the packets for the messages
        try:
            # Player one begins the cycle and encrypts its new address with everyone's
            # public encryption key, in order.
            # Each subsequent player reorders the cycle and removes one layer of encryption.
            self.__messages.clear_packets()
            if self.__me == 0:
                self.__messages.add_str(self.encrypt_new_address())
                # form packet and...
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, self.__players[self.__me + 1])
                # ... send it to the next player
                self.__outchan.send(self.__messages.packets.SerializeToString())
            elif self.__me == self.__N - 1:
                # get packets from previous
                val = self.__inchan.recv()
                try:
                    self.__messages.packets.ParseFromString(val)
                except DecodeError:
                    self.__logchan('Decoding Error!')
                # decrypt players layer in every packet
                for packet in self.__messages.packets.packet:
                    packet.packet.message.str = self.__crypto.decrypt(packet.packet.message.str)
                # add the last address
                self.__messages.add_str(self.__addr_new)
                # shuffle the packets
                self.__messages.shuffle_packets()
                # form packet ...
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, None)
                # and send it to everyone
                self.__outchan.send(self.__messages.packets.SerializeToString())
            else:
                # get packets from previous
                val = self.__inchan.recv()
                try:
                    self.__messages.packets.ParseFromString(val)
                except DecodeError:
                    self.__logchan('Decoding Error!')
                # decrypt players layer in every packet
                for packet in self.__messages.packets.packet:
                    packet.packet.message.str = self.__crypto.decrypt(packet.packet.message.str)
                # add encrypted new addres of players
                self.__messages.add_str(self.encrypt_new_address())
                # shuffle the packets
                self.__messages.shuffle_packets()
                # form packet and...
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, self.__players[self.__me + 1])
                # and send it to next player
                self.__outchan.send(self.__messages.packets.SerializeToString())
        except BlameException:
            self.__logchan("Blame!")
