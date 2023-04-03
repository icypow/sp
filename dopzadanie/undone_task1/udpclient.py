import socket
import sys
import threading
import hashlib
import time
import struct
msglen=100
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
client.settimeout(5)
i=5
def make_packet(data):
    packet_len = len(data)
    #print(packet_len)
    checksum = hashlib.md5(data[:msglen-24]).digest()
    packet = struct.pack('!I16s', packet_len, checksum[:16]) + data[:msglen-24]
    return packet
def unpack_packet(socket, adr):
    packet=socket.recv(msglen)
    packet_len, checksum = struct.unpack('!I16s', packet[:20])
    data = packet[20:20+packet_len]
    #print(packet_len)
    if hashlib.md5(data).digest()[:16] != checksum:
        while True:
            socket.sendto("1".encode('utf-8'), adr)
            packet=socket.recv(msglen)
            packet_len, checksum = struct.unpack('!I16s', packet[:20])
            #print(packet_len)
            data = packet[20:20+packet_len]
            if hashlib.md5(data).digest()[:16] == checksum:
                break
    socket.sendto("0".encode('utf-8'), adr)
    return data.decode('utf-8'), packet_len 
name=sys.argv[3]
client.sendto((name).encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
try:
    response=client.recv(msglen).decode('utf-8')
except socket.timeout:
    print('Превышено время ожидания ответа сервера1')
    exit()
if response=="0":
    print("Клиент с таким именем уже подключался")
    exit()
while True:
    msg=input()
    msg=msg.encode('utf-8')
    while msg:
        packet=make_packet(msg)
        #print(msg)
        while True:
            client.sendto(packet, (sys.argv[1], int(sys.argv[2])))
            try:
                response=client.recv(msglen).decode('utf-8')
            except socket.timeout:
                print('Превышено время ожидания ответа сервера1')
                exit()
            if response=="0":
                break
        msg=msg[msglen-24:]
    
    response=""
    while True:
        try:
            resp, leng = unpack_packet(client, (sys.argv[1], int(sys.argv[2])))
        except socket.timeout:
                print('Превышено время ожидания ответа сервера2')
                exit()
        #print(leng, msglen)
        response+=resp
        if leng<=msglen:
            #print('breaking')
            break
    print(response)