import socket
import sys
connections=list()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
while True:
    msg, adr=server.recvfrom(1024)
    if adr not in connections:
        print(adr, "connected")
        connections.append(adr)
    print(msg.decode('utf-8'))
#server.sendto("Hello, client!".encode('utf-8'), adr)