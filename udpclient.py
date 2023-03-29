import socket
import sys
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    msg=input()
    client.sendto(msg.encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
