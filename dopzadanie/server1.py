import socket
import sys
import threading
import queue
import hashlib
import time
import struct
max_timeout=100
client_queue=queue.PriorityQueue()
locker=threading.Lock()
queues=dict()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
connections=list()
names=dict()
recv_list=list()
recv_dict=dict()
names_list=list()
adr_dict=dict()
def make_packet(data):
    packet_len = len(data)
    checksum = hashlib.md5(data).digest()
    packet = struct.pack('!I16s', packet_len, checksum[:16]) + data[:1000]
    return packet
def unpack_packet(socket, adr, packet):
    packet_len, checksum = struct.unpack('!I16s', packet[:20])
    data = packet[20:20+packet_len]
    if hashlib.md5(data).digest()[:16] != checksum:
        while True:
            socket.sendto("1".encode('utf-8'), names[adr])
            recv_list.append(adr)
            set_timer=time.time()
            while adr in recv_list:
                if time.time()-set_timer>max_timeout:
                    print("Превышено время ожидания от", names[adr])
                    recv_list.remove(adr)
                    connections.remove(adr)
                    return
            packet=recv_dict[adr]
            packet_len, checksum = struct.unpack('!I16s', packet[:20])
            data = packet[20:20+packet_len]
            if hashlib.md5(data).digest()[:16] == checksum:
                break
    socket.sendto("0".encode('utf-8'), adr)
    return data.decode('utf-8'), packet_len 
def q(adr, msg, tm):
    global recv_dict
    global recv_list
    response=""
    while True:
        try:
            resp, leng = unpack_packet(server, adr, msg)
        except socket.timeout:
                print('Превышено время ожидания ответа клиента', names[adr])
                exit()
        response+=resp
        if leng<=1000:
            break
        else:
            recv_list.append(adr)
            set_timer=time.time()
            while adr in recv_list:
                if time.time()-set_timer>max_timeout:
                    print("Превышено время ожидания от", names[adr])
                    recv_list.remove(adr)
                    connections.remove(adr)
                    return
            msg=recv_dict[adr]
    msg=response
    iterator=msg.find('+')
    if iterator != -1:
        client_name, queue_msg = msg[:iterator], msg[iterator+1:]
        locker.acquire()
        if client_name not in names_list: 
            server.sendto(make_packet(("SERVER: Нет такого клиента").encode('utf-8')), adr)
            return
        locker.release()
        print("Сообщение '", queue_msg, "' от ", names[adr], " в очередь ", client_name, sep='')
        locker.acquire()
        client_queue.join
        info=list()
        info.append(names[adr])
        info.append(client_name)
        info.append(queue_msg)
        ninfo=list()
        ninfo.append(int(tm))
        ninfo.append(info)
        try:
            client_queue.put(ninfo)
        except:
            server.sendto(make_packet(("SERVER: Невозможно невозможно положить в очередь").encode('utf-8')), adr)
            return
        finally:
            server.sendto(make_packet(("SERVER: Успешное добавление в очередь").encode('utf-8')), adr)
        locker.release()

def sendmsg():
    print('here')
    while True:
        if not client_queue.empty():
            locker.acquire()
            client_queue.join
            newmsg=client_queue.get(block=True)
            print(newmsg)
            adr=adr_dict[newmsg[1][1]]
            msg=newmsg[1][2]
            while msg:
                packet=make_packet(msg.encode('utf-8'))
                while True:
                    server.sendto(packet, adr)
                    try:
                        recv_list.append(adr)
                        set_timer=time.time()
                        while adr in recv_list:
                            if time.time()-set_timer>max_timeout:
                                print("Превышено время ожидания от", names[adr])
                                recv_list.remove(adr)
                                connections.remove(adr)
                                return
                        response=recv_dict[adr]
                        #print(response)
                    except socket.timeout:
                        print('Превышено время ожидания ответа сервера1')
                        exit()
                    if response.decode('utf-8')=="0":
                        break
                msg=msg[1000:]
            locker.release()
thread_sender=threading.Thread(target=sendmsg).start()
while True:
    msg, adr=server.recvfrom(1024)
    tm=time.time_ns()
    if adr not in connections:
        name=msg.decode('utf-8')
        if name in names_list:
            server.sendto("0".encode('utf-8'), adr)
            continue
        server.sendto("1".encode('utf-8'), adr)
        print(name, "подключился")
        connections.append(adr)
        names_list.append(name)
        names[adr]=name
        adr_dict[name]=adr
        continue
    if adr in recv_list:
        #print(msg.decode('utf-8'))
        recv_dict[adr]=msg
        recv_list.remove(adr)
        continue
    else:
        t = threading.Thread(target=q, args=(adr, msg, tm)).start()
    
