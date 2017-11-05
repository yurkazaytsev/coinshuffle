import protobuf.message_pb2 as message_factory
from random import shuffle

class Messages(object):

    def __init__(self):
        self.packets = message_factory.Packets()

    def make_greeting(self, vk):
        packet = self.packets.packet.add()
        packet.packet.from_key.key = vk

    def form_last_packet(self, eck, session, number, vk_from , vk_to):
        packet = self.packets.packet[-1]
        packet.packet.session = session
        packet.packet.number = int(number)
        packet.packet.from_key.key = vk_from
        if vk_to : packet.packet.to_key.key = vk_to
        msg = packet.packet.SerializeToString()
        packet.signature.signature = eck.sign_message(msg,True)

    def form_all_packets(self, eck, session, number, vk_from, vk_to):
        for packet in self.packets.packet:
            packet.packet.session = session
            packet.packet.number = int(number)
            packet.packet.session = session
            packet.packet.number = int(number)
            packet.packet.from_key.key = vk_from
            if vk_to : packet.packet.to_key.key = vk_to
            msg = packet.packet.SerializeToString()
            packet.signature.signature = eck.sign_message(msg,True)

    def blame_insufficient_funds(self, offender):
        """
        offender is a veryfikation key! of player who have insufficient funds
        """
        # add new packet
        packet = self.packets.packet.add()
        # set blame resaon
        packet.packet.message.blame.reason = message_factory.INSUFFICIENTFUNDS
        # set blame acused
        packet.packet.message.blame.accused.key = offender
        # set phase (it is 'Blame' here, for real ;) )
        packet.packet.phase = message_factory.BLAME
        # we return nothing here. Message_factory is a state machine, We just update state

    def add_encryption_key(self, ek, change):
        """
        Adds encryption keys at the Announcement stage
        ek - is serialized encryption key
        """
        # add new packet
        packet = self.packets.packet.add()
        # add encryption key
        packet.packet.message.key.key = ek
        if change : packet.packet.message.address.address = change

    def get_encryption_keys(self):
        return {str(packet.packet.from_key.key) : packet.packet.message.key.key.encode('utf-8')  for packet in  self.packets.packet}

    def get_new_addresses(self):
        return [packet.packet.message.str.encode('utf-8') for packet in self.packets.packet]

    def get_hashes(self):
        return {str(packet.packet.from_key.key) : packet.packet.message.hash.hash.encode('utf-8')  for packet in  self.packets.packet}

    def add_str(self, string):
        packet = self.packets.packet.add()
        packet.packet.message.str = string

    def add_hash(self, hash_value):
        packet = self.packets.packet.add()
        packet.packet.message.hash.hash = hash_value

    def shuffle_packets(self):
        packs = [p for p in self.packets.packet]
        shuffle(packs)
        self.clear_packets()
        for i in range(0,len(packs)):
            self.packets.packet.add()
            self.packets.packet[-1].CopyFrom(packs[i])

    def encryption_keys_count(self):
        return len([1 for packet in self.packets.packet if len(packet.packet.message.key.key) != 0])

    def get_session(self):
        return self.packets.packet[-1].packet.session

    def get_number(self):
        return self.packets.packet[-1].packet.number

    def get_from_key(self):
        return self.packets.packet[-1].packet.from_key.key

    def get_to_key(self):
        return self.packets.packet[-1].packet.to_key.key

    def get_phase(self):
        return self.packets.packet[-1].packet.phase

    def get_players(self):
        return {packet.packet.number : str(packet.packet.from_key.key) for packet in self.packets.packet}

    def clear_packets(self):
        self.__init__()
