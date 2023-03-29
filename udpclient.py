import socket
import sys
import threading
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
while True:
    msg=input()
    client.sendto(msg.encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
    locker.acquire()
    msg=client.recv(1024).decode('utf-8')
    locker.release()
    print(msg)