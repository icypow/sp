import socket
import sys
import threading
import hashlib
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
i=5
while True:
    msg=input()
    checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
    msg=str(checksum)+msg
    while True:
        # if i>0:
        #     client.sendto((hashlib.md5("random".encode('utf-8')).hexdigest()+"123+random").encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
        #     i-=1
        # else:
        client.sendto((msg).encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
        response=client.recv(1024).decode('utf-8')
        if response=="0":
            break
    response=client.recv(1024).decode('utf-8')
    if response[:6]=="SERVER":
        print(response)
    else:
        msg=response[32:]
        income_checksum=response[:32]
        checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
        while income_checksum!=checksum:
            print("UDP-INFO: Чексумма не совпала. Оповещаю отправителя и жду переотправки пакета")
            client.sendto("1".encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
            response=client.recv(1024).decode('utf-8') 
            msg=response[32:]
            income_checksum=response[:32]
            checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
        print("UDP-INFO: Чексумма совпала! Беру сообщения в оборот")
        client.sendto("0".encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
        print(msg)