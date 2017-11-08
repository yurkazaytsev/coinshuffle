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
        self.__new_addresses = set()
        self.__addr_new = addr_new
        # My change address. (may be null).
        self.__change = change
        self.__signatures = dict()
        # self.__mail_box = None

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
                self.__messages.form_last_packet(self.__sk, self.__session, self.__me, self.__vk, None,self.__phase)
                self.__outchan.send(self.__messages.packets.SerializeToString())
            raise BlameException('Insufficient funds')

    def broadcast_new_key(self ,change_addresses):
        dk = self.__crypto.generate_key_pair()
        # Broadcast the public key and store it in the set with everyone else's.
        # self.__encryption_keys[self.__vk] = self.__crypto.export_public_key()
        # change_addresses[self.__vk] = self.__change
        self.__messages.add_encryption_key(self.__crypto.export_public_key(), self.__change)
        self.__messages.form_last_packet(self.__sk, self.__session, self.__me, self.__vk, None,self.__phase)
        # self.__messages.sign_last_packet(self.__sk)
        self.__outchan.send(self.__messages.packets.SerializeToString())
        # return dk

    # In phase 1, everybody announces their new encryption keys to one another. They also
    # optionally send change addresses to one another. This function reads that information
    # from a message and puts it in some nice data structures.

    def read_announcements(self, messages, encryption_keys, change_addresses):
        for i in range(self.__N):
            val = self.__inchan.recv()
            try:
                self.__messages.packets.ParseFromString(val)
            except Exception:
                self.__logchan.send('Decoding Error!')
            self.__encryption_keys[self.__messages.get_from_key()] = self.__messages.get_encryption_key()
            change_addresses[self.__messages.get_from_key()] = self.__messages.get_address()
        if (len(self.__encryption_keys) == self.__N):
            # self.__encryption_keys = self.__messages.get_encryption_keys()
            self.__logchan.send('Player '+ str(self.__me) + ' recieved all keys for test.\n')
        else:
            print(self.__encryption_keys)
            raise BlameException("Player # " + str(self.__me) + " not get all encryption keys")


    def encrypt_new_address(self):
        # Add our own address to the mix. Note that if me == N, ie, the last player, then no
        # encryption is done. That is because we have reached the last layer of encryption.
        encrypted = self.__addr_new
        for i in range(self.__N , self.__me, -1):
            # Successively encrypt with the keys of the players who haven't had their turn yet.
            encrypted = self.__crypto.encrypt(encrypted, self.__encryption_keys[self.__players[i]])
        return encrypted

    def equivocation_check(self):
        # compute hash
        computed_hash =str( hash( str(self.__new_addresses) + str([self.__encryption_keys[self.__players[i]] for i in range(self.__N) ])))
        # create a new message
        self.__messages.clear_packets()
        # add new hash
        self.__messages.add_hash(computed_hash)
        # sign a packets for broadcasting
        self.__messages.form_last_packet(self.__sk, self.__session, self.__me, self.__vk, None, self.__phase)
        # broadcast the message
        self.__outchan.send(self.__messages.packets.SerializeToString())
        # receive the others message
        val = self.__inchan.recv()
        try:
            self.__messages.packets.ParseFromString(val)
        except DecodeError:
            self.__logchan('Decoding Error!')
        hashes = self.__messages.get_hashes()
        for hash_value in hashes:
            if hashes[hash_value] != computed_hash:
                self.__logchan.send(" someone cheating!")
                raise BlameException
        self.__logchan.send('Player ' + str(self.__me) + ' is checked the hashed.\n')

    def protocol_definition(self):

        if self.__amount <= 0:
            raise ValueError('wrong amount for transaction')

        # Phase 1: Announcement
        # In the announcement phase, participants distribute temporary encryption keys.
        self.__phase = 'Announcement'
        self.__logchan.send("Player " + str(self.__me) + " begins CoinShuffle protocol " + " with " + str(self.__N) + " players.\n")
        # Check for sufficient funds.
        # There was a problem with the wording of the original paper which would have meant
        # that player 1's funds never would have been checked, but it's necessary to check
        # everybody.
        self.blame_insufficient_funds()
        self.__logchan.send("Player " + str(self.__me) + " finds sufficient funds.\n")
        # This will contain the change addresses.
        change_addresses = dict()
        # self.__dk = self.broadcast_new_key(change_addresses)

        self.broadcast_new_key(change_addresses)
        self.__logchan.send("Player " + str(self.__me) + " has broadcasted the new encryption key.\n")
        # Now we wait to receive similar key from everyone else.
        announcement =  dict()
        #TO Reciver form multiple
        self.__logchan.send("Player " + str( self.__me) + " is about to read announcements.\n")

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
            if self.__me == 1:
                self.__messages.add_str(self.encrypt_new_address())
                # form packet and...
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, self.__players[self.__me + 1],self.__phase)
                # ... send it to the next player
                self.__outchan.send(self.__messages.packets.SerializeToString())
            elif self.__me == self.__N:
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
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, None, self.__phase)
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
                self.__messages.form_all_packets(self.__sk, self.__session, self.__me, self.__vk, self.__players[self.__me + 1], self.__phase)
                # and send it to next player
                self.__outchan.send(self.__messages.packets.SerializeToString())
            #   Phase 3: broadcast outputs.
            #   In this phase, the last player just broadcasts the transaction to everyone else.
            self.__phase = 'BroadcastOutput'
            #Receive all new addresses
            val = self.__inchan.recv()
            try:
                self.__messages.packets.ParseFromString(val)
            except DecodeError:
                self.__logchan('Decoding Error!')
            # extract addresses from packets
            self.__new_addresses = self.__messages.get_new_addresses()
            #check if player address is in
            if self.__addr_new in self.__new_addresses:
                self.__logchan.send("Player "+ str(self.__me) + " receive addresses and found itsefs")
            else:
                self.__logchan.send("Player " + str(self.__me) + "  not found itsefs new address")
                raise BlameException
        except BlameException:
            self.__logchan("Blame!")
        # Phase 4: equivocation check.
        # In this phase, participants check whether any player has history different
        # encryption keys to different players.

        self.__phase = 'EquivocationCheck'
        self.__logchan.send("Player "+ str(self.__me) + " reaches phase 4: ")
        self.equivocation_check()

        # Phase 5: verification and submission.
        # Everyone creates a Bitcoin transaction and signs it, then broadcasts the signature.
        # If all signatures check out, then the transaction is history into the net.
        self.__phase = 'VerificationAndSubmission'
        self.__logchan.send("Player "+ str(self.__me) + " reaches phase 5: ")
