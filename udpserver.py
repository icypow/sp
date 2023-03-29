import socket
import sys
import queue
import re
queues=dict()
connections=list()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
while True:
    msg, adr=server.recvfrom(1024)
    msg = msg.decode('utf-8')
    if adr not in connections:
        print(adr, "connected")
        connections.append(adr)
    iterator=msg.find('+')
    if iterator != -1:
        queue_name, queue_msg = msg[:iterator], msg[iterator+1:]
        print(queue_name, queue_msg, "В очередь")
    else:
        queue_name=msg
        print(queue_name, "Из очереди")
