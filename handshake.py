import socket
from messages import Messages

HOST = "localhost"
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

framing_end = unichr(9166).encode('utf-8')
msgs = Messages()
pack = msgs.packets.packet.add()
pack.packet.from_key.key = '12ababa12'
request = msgs.packets.SerializeToString() + framing_end
s.sendall(request)
response = s.recv(1024)
msgs.packets.ParseFromString(response)
print(msgs.packets)
# msgs.packets.ParseFromString(response[:-3])
# print(msgs.packets)
