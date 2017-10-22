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



# # Tests
#
# msgs = Messages()
# msgs.add_encryption_key('112334456789','asdasda')
# msgs.sign_packet(msgs.packets.packet[0],2)
#
# msgs.packets.ParseFromString(msg_itself)
#
#
# msgs.packets
#
# msgs.blame_insufficient_funds('asdasdasdadsvarwef')
#
# msg_itself = msgs.packets.SerializeToString()
#
#
# ## Some test goes here
# packets = message_factory.Packets()
# packet = packets.packet.add()
# # Here is how we set up the message
# packet.packet.message.blame.reason = message_factory.INSUFFICIENTFUNDS
# packet.packet.message.blame.accused.key = '1121323'
#
#
# ##
# messages = Messages()
# msg = message.Message()
# msg.blame.reason  = 1
#
# message
# float("10.0")
#
# None or ""
