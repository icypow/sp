import socket
import sys
import threading
import queue
import hashlib
import time
max_timeout=5
locker=threading.Lock()
queues=dict()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
connections=list()
names=list()
recv_list=list()
recv_dict=dict()

def q(adr, msg):
    global recv_dict
    global recv_list
    income_checksum=msg[:32]
    msg=msg[32:]
    checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
    while income_checksum!=checksum:
        print("Чексумма не совпала. Оповещаю отправителя и жду переотправки пакета")
        server.sendto("1".encode('utf-8'), adr)
        recv_list.append(adr)
        set_timer=time.time()
        while adr in recv_list:
            if time.time()-set_timer>max_timeout:
                print("Превышено время ожидания от", adr)
                recv_list.remove(adr)
                connections.remove(adr)
                return
        response=recv_dict[adr]
        msg=response[32:]
        income_checksum=response[:32]
        checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
    print("UDP-INFO: Чексумма совпала! Беру сообщения в оборот")
    server.sendto("0".encode('utf-8'), adr)
    iterator=msg.find('+')
    if iterator != -1:
        queue_name, queue_msg = msg[:iterator], msg[iterator+1:]
        locker.acquire()
        if queue_name not in queues: 
            print("Создана новая очередь", queue_name)
            queues[queue_name]=queue.Queue()
        locker.release()
        print("Сообщение '", queue_msg, "' от ", adr, " в очередь ", queue_name, sep='')
        locker.acquire()
        queues[queue_name].join
        try:
            queues[queue_name].put(queue_msg)
        except:
            server.sendto(("SERVER: Невозможно невозможно положить в очередь").encode('utf-8'), adr)
            return
        finally:
            server.sendto("SERVER: Успешное добавление в очередь".encode('utf-8'), adr)
        locker.release()
    else:
        queue_name=msg
        if queue_name not in queues:
            server.sendto(("SERVER: Нет такой очереди").encode('utf-8'), adr)
            return
        print(adr, "берет из очереди", queue_name, )
        locker.acquire()
        queues[queue_name].join
        try:
            msg=queues[queue_name].get(block=True)
        except:
            server.sendto(("SERVER: Невозможно получить из очереди").encode('utf-8'), adr)
            return
        locker.release()
        checksum = hashlib.md5(msg.encode('utf-8')).hexdigest()
        msg=str(checksum)+msg
        print("Попытка послать сообщение клиенту")
        while True:
            server.sendto(msg.encode('utf-8'), adr)
            recv_list.append(adr)
            set_timer=time.time()
            while adr in recv_list:
                if time.time()-set_timer>max_timeout:
                    print("Превышено время ожидания от", adr)
                    recv_list.remove(adr)
                    connections.remove(adr)
                    return
            if recv_dict[adr]=="0":
                print("Успешно!")
                break
        locker.acquire()
        if queues[queue_name].empty()==True:
            print("Удаление очереди", queue_name)
            del queues[queue_name]
        locker.release()
while True:
    msg, adr=server.recvfrom(1024)
    print(adr)
    if adr not in connections:
        name=msg.decode('utf-8')
        if name in names:
            server.sendto("0".encode('utf-8'), adr)
            continue
        server.sendto("1".encode('utf-8'), adr)
        print(name, "connected")
        connections.append(adr)
        names.append(name)
        continue
    msg = msg.decode('utf-8')
    #print("FIRST IN", msg)
    if adr in recv_list:
        recv_dict[adr]=msg
        recv_list.remove(adr)
    if (msg=="0" or msg=="1")and adr not in recv_list:
        continue
    else:
        t = threading.Thread(target=q, args=(adr, msg)).start()