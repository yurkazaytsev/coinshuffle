import protobuf.message_pb2 as message_factory

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

    def encryption_keys_count(self):
        return len([1 for packet in self.packets.packet if len(packet.packet.message.key.key) != 0])


# z = Messages()
# z.add_encryption_key('1',"2")
# # z.blame_insufficient_funds("2")
# z.add_encryption_key('3',"2")
#
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
