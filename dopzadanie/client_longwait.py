import socket
import sys
import threading
import hashlib
import time
import struct
response_list=list()
msg_list=list()
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
locker=threading.Lock()
i=5
def inputer():
    while True:
        packet=client.recv(1024)
        try:
            if packet.decode('utf-8')=="0" or packet.decode('utf-8')=="1":
                response_list.append(packet)
        except:
            msg_list.append(packet)
def reciever():
    #print('here')
    while True:
        response=""
        while True:
            resp, leng = unpack_packet(client, (sys.argv[1], int(sys.argv[2])))
            response+=resp
            if leng<=1000:
                break
        #print(msg_list)
        print(response)
def sender():
    #print('hrer')
    while True:
        msg=input()
        msg=msg.encode('utf-8')
        while msg:
            packet=make_packet(msg)
            while True:
                client.sendto(packet, (sys.argv[1], int(sys.argv[2])))
                while len(response_list)==0:
                    pass
                response=response_list[0].decode('utf-8')
                response_list.pop(0)
                if response=="0":
                    break
            msg=msg[1000:]
def make_packet(data):
    packet_len = len(data)
    checksum = hashlib.md5(data).digest()
    packet = struct.pack('!I16s', packet_len, checksum[:16]) + data[:1000]
    return packet
def unpack_packet(socket, adr):
    while len(msg_list)==0:
        pass
    packet=msg_list[0]
    msg_list.pop(0)
    time.sleep(10)
    packet_len, checksum = struct.unpack('!I16s', packet[:20])
    data = packet[20:20+packet_len]
    if data.decode('utf-8')[:6]=="SERVER":
        return data.decode('utf-8'), packet_len
    if hashlib.md5(data).digest()[:16] != checksum:
        while True:
            socket.sendto("1".encode('utf-8'), adr)
            while len(msg_list)==0:
                pass
            packet=msg_list[0]
            msg_list.pop(0)
            packet_len, checksum = struct.unpack('!I16s', packet[:20])
            data = packet[20:20+packet_len]
            if hashlib.md5(data).digest()[:16] == checksum:
                break
    socket.sendto("0".encode('utf-8'), adr)
    return data.decode('utf-8'), packet_len 
name=sys.argv[3]
client.sendto((name).encode('utf-8'), (sys.argv[1], int(sys.argv[2])))
response=client.recv(1024).decode('utf-8')
if response=="0":
    print("Клиент с таким именем уже подключался")
    exit()
t=threading.Thread(target=reciever).start()
p=threading.Thread(target=sender).start()
p=threading.Thread(target=inputer).start()
