import protobuf.message_pb2 as message_factory
from random import shuffle

class Messages(object):

    def __init__(self):
        self.packets = message_factory.Packets()

    # def sign_last_packet(self, eck):
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

    def add_str(self, string):
        packet = self.packets.packet.add()
        packet.packet.message.str = string

    def shuffle_packets(self):
        packs = [p for p in self.packets.packet]
        shuffle(packs)
        self.clear_packets()
        for i in range(0,len(packs)):
            self.packets.packet.add()
            self.packets.packet[-1].CopyFrom(packs[i])

    def encryption_keys_count(self):
        return len([1 for packet in self.packets.packet if len(packet.packet.message.key.key) != 0])

    def clear_packets(self):
        self.__init__()


# z.add_encryption_key('first','1')
# z.add_encryption_key('second','1')
# z.add_encryption_key('third','1')
# z.add_encryption_key('fourth','1')
#
# {str(packet.packet.from_key.key) :str(packet.packet.message.address.address) for packet in  z.packets.packet}
#
#
# z.packets

# z.get_encryption_keys()




#
# {packet.packet.message.address.address : packet.packet.message.key.key  for packet in  z.packets.packet}
#
# z.packets.packet[0].packet.message.key.key
#
# z.shuffle_packets()
#
# zz= Messages()
#
# pacs = [packet for packet in z.packets.packet]
# shuffle(pacs)
#
#
#
# zz.clear_packets()
# zzz = zz.packets.packet.add()
# zz.packets.ParseFromString(pacs[0])
# zz.packets.packet[-1].CopyFrom(pacs[0])
#
# type(pacs[0])
#
# zz.packets
#
# shuffle(pacs)
# z.packets.ParseFromString("".join(packs))
#
#
#
# z.add_encryption_key("1","2")
#
# x = Messages()
# x.add_encryption_key("3","4")
#
# z.packets.MergeFrom(x.packets)
#
#
# for i in range(10):
#     z.add_encryption_key(str(i),str(i))
#
#
# # z.clear_packets()
# [packet.packet.SerializeToString() for packet in z.packets.packet]
# packs
# packs
# z.packets.ParseFromString(packs[0] )
# z.packets
# z.encryption_keys_count()
# #
# # len([1 for packet in z.packets.packet if len(packet.packet.message.key.key) != 0])
# #
# #
# #
# # x = Messages()
# # x.packets.ParseFromString(3*zstr)
# #
# # len(x.packets.packet)
