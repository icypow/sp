import socket
import sys
import threading
import time
import random
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
i=0
while True:

    time.sleep(0.5+0.1*random.randint(0, 1))
    client.sendto(f"123+{i}msg".encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
    locker.acquire()
    msg=client.recv(1024).decode('utf-8')
    locker.release()
    print(msg)
    i+=1