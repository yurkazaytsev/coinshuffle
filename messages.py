import protobuf.message_pb2 as message

class Message(object):

    # Just adding new packet to packets list
    def __init__(self, messages):
        self.__packet = messages.Packets.packet.add()

    # making the message based on type of message
    def make(msg):
        if type(msg) == 'message_pb2.Blame':
            self.__packet.packet.message.blame.reason = msg.reason
