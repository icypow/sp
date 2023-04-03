import socket
import sys
import threading
import hashlib
import time
import struct
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
client.settimeout(5)
i=5
def make_packet(data):
    packet_len = len(data)
    checksum = hashlib.md5(data).digest()
    packet = struct.pack('!I16s', packet_len, checksum[:16]) + data[:1000]
    return packet
def unpack_packet(socket, adr):
    packet=socket.recv(1024)
    packet_len, checksum = struct.unpack('!I16s', packet[:20])
    data = packet[20:20+packet_len]
    if data.decode('utf-8')[:6]=="SERVER":
        return data.decode('utf-8'), packet_len
    if hashlib.md5(data).digest()[:16] != checksum:
        while True:
            socket.sendto("1".encode('utf-8'), adr)
            packet=socket.recv(1024)
            packet_len, checksum = struct.unpack('!I16s', packet[:20])
            data = packet[20:20+packet_len]
            if hashlib.md5(data).digest()[:16] == checksum:
                break
    socket.sendto("0".encode('utf-8'), adr)
    return data.decode('utf-8'), packet_len 
name=sys.argv[3]
client.sendto((name).encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
try:
    response=client.recv(1024).decode('utf-8')
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
        while True:
            client.sendto(packet, (sys.argv[1], int(sys.argv[2])))
            try:
                response=client.recv(1024).decode('utf-8')
            except socket.timeout:
                print('Превышено время ожидания ответа сервера1')
                exit()
            if response=="0":
                break
        msg=msg[1000:]
    response=""
    while True:
        try:
            resp, leng = unpack_packet(client, (sys.argv[1], int(sys.argv[2])))
        except socket.timeout:
                print('Превышено время ожидания ответа сервера2')
                exit()
        response+=resp
        if leng<=1000:
            break
    print(response)