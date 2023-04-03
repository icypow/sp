import socket
import sys
import threading
import queue
import hashlib
import time
import struct
msglen=100
max_timeout=5
locker=threading.Lock()
queues=dict()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
connections=list()
names=dict()
recv_list=list()
recv_dict=dict()
def msgsnd(msg, adr):
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
                print('got response')
                break
            print(msg, 'MSG')
        msg=msg[msglen-24:]
def make_packet(data):
    packet_len = len(data)
    print(data.decode('utf-8'))
    checksum = hashlib.md5(data[:msglen-24]).digest()
    #print(checksum)
    packet = struct.pack('!I16s', packet_len, checksum[:16]) + data[:msglen-24]
    return packet
def unpack_packet(socket, adr, packet):
    packet_len, checksum = struct.unpack('!I16s', packet[:20])
    data = packet[20:20+packet_len]
    if hashlib.md5(data).digest()[:16] != checksum:
        while True:
            socket.sendto("1".encode('utf-8'), adr)
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
            #print(packet_len)
            data = packet[20:20+packet_len]
            if hashlib.md5(data).digest()[:16] == checksum:
                break
    socket.sendto("0".encode('utf-8'), adr)
    return data.decode('utf-8'), packet_len 
def q(adr, msg):
    global recv_dict
    global recv_list
    response=""
    while True:
        try:
            resp, leng = unpack_packet(server, adr, msg)
            #print(leng)
        except socket.timeout:
                print('Превышено время ожидания ответа клиента', names[adr])
                exit()
        response+=resp
        if leng<=msglen-24:
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
        queue_name, queue_msg = msg[:iterator], msg[iterator+1:]
        locker.acquire()
        if queue_name not in queues: 
            print("Создана новая очередь", queue_name)
            queues[queue_name]=queue.Queue()
        locker.release()
        print("Сообщение '", queue_msg, "' от ", names[adr], " в очередь ", queue_name, sep='')
        locker.acquire()
        queues[queue_name].join
        try:
            queues[queue_name].put(queue_msg)
        except:
            msgsnd("Невозможно невозможно положить в очередь", adr)
            return
        finally:
            msgsnd("Успешное добавление в очередь", adr)
            return
        locker.release()
    else:
        queue_name=msg
        if queue_name not in queues:
            msgsnd("Нет такой очереди", adr)
            return
        print(names[adr], "берет из очереди", queue_name, )
        locker.acquire()
        queues[queue_name].join
        try:
            msg=queues[queue_name].get(block=True)
        except:
            msgsnd("Невозможно получить из очереди", adr)
            return
        locker.release()
        print("Попытка послать сообщение клиенту", names[adr])
        msgsnd(msg, adr)
        print("Успешная отправка клиенту", names[adr])
        locker.acquire()
        if queues[queue_name].empty()==True:
            print("Удаление очереди", queue_name)
            del queues[queue_name]
        locker.release()
while True:
    #print('inp')
    msg, adr=server.recvfrom(msglen)
    #print(adr)
    if adr not in connections:
        name=msg.decode('utf-8')
        if name in names:
            server.sendto("0".encode('utf-8'), adr)
            continue
        server.sendto("1".encode('utf-8'), adr)
        print(name, "подключился")
        connections.append(adr)
        names[adr]=name
        continue
    if adr in recv_list:
        recv_dict[adr]=msg
        recv_list.remove(adr)
        continue
    else:
        # packet=msg
        # packet_len, checksum = struct.unpack('!I16s', packet[:20])
        # data = packet[20:20+packet_len]
        # print(data.decode('utf-8'))
        #print('here')
        t = threading.Thread(target=q, args=(adr, msg)).start()