import socket
import sys
import threading
import queue
import time
import zlib
locker=threading.Lock()
queues=dict()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
connections=list()
recv_list=list()
recv_dict=dict()
def q(adr, msg):
    global recv_dict
    global recv_list
    iterator=msg.find('+')
    if iterator != -1:
        queue_name, queue_msg = msg[:iterator], msg[iterator+1:]
        print("Сообщение", queue_msg, "от", adr, "в очередь", queue_name)
        if queue_name not in queues:
            locker.acquire()
            if queue_name not in queues:
                print("Создана новая очередь", queue_name)
                queues[queue_name]=queue.Queue()
            locker.release()
        queues[queue_name].join
        try:
            queues[queue_name].put(queue_msg)
        except:
            server.sendto(("SERVER: Невозможно невозможно положить в очередь").encode('utf-8'), adr)
            return
        finally:
            server.sendto("SERVER: Успешное добавление в очередь".encode('utf-8'), adr)
            time.sleep(10)
            #queues[queue_name].task_done()
    else:
        queue_name=msg
        if queue_name not in queues:
            server.sendto(("SERVER: Нет такой очереди").encode('utf-8'), adr)
            return
        print(adr, "берет из очереди", queue_name, )
        queues[queue_name].join
        try:
            msg=queues[queue_name].get(block=True)
        except:
            server.sendto(("SERVER: Невозможно получить из очереди").encode('utf-8'), adr)
            return
        checksum = zlib.crc32(msg.encode('utf-8'))
        while True:
            server.sendto(msg.encode('utf-8'), adr)
            recv_list.append(adr)
            while adr in recv_list:
                pass
            if int(recv_dict[adr])==int(checksum):
                server.sendto("0".encode('utf-8'), adr)
                break
            else:
                server.sendto("1".encode('utf-8'), adr)
        if queues[queue_name].empty()==True:
            locker.acquire()
            print("Удаление очереди", queue_name)
            del queues[queue_name]
            locker.release()
while True:
    msg, adr=server.recvfrom(1024)
    if adr not in connections:
        print(adr, "connected")
        connections.append(adr)
    msg = msg.decode('utf-8')
    if adr in recv_list:
        recv_dict[adr]=msg
        recv_list.remove(adr)
    else:
        t = threading.Thread(target=q, args=(adr, msg)).start()