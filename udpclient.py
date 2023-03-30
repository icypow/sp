import socket
import sys
import threading
import zlib
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
while True:
    msg=input()
    client.sendto(msg.encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
    response=client.recv(1024).decode('utf-8')
    if response[:6]=="SERVER":
        print(response)
    else:
        msg=response
        checksum = zlib.crc32(msg.encode('utf-8'))
        client.sendto(str(checksum).encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
        response=client.recv(1024).decode('utf-8')
        if response=="0":
            print(msg)