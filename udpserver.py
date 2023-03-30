import socket
import sys
import threading
import queue
import time
locker=threading.Lock()
queues=dict()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
connections=list()
def q(adr, msg):
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
        finally:
            server.sendto("Successfully added".encode('utf-8'), adr)
            time.sleep(10)
            #queues[queue_name].task_done()
    else:
        queue_name=msg
        if queue_name not in queues:
            server.sendto(("SERVER NOTIFICATION: Нет такой очереди").encode('utf-8'), adr)
            return
        print(adr, "берет из очереди", queue_name, )
        queues[queue_name].join
        try:
            server.sendto(queues[queue_name].get(block=True).encode('utf-8'), adr)
        except:
            server.sendto(("SERVER NOTIFICATION: Невозможно получить из очереди").encode('utf-8'), adr)
        if queues[queue_name].empty()==True:
            locker.acquire()
            print("Удаление очереди", queue_name)
            del queues[queue_name]
            locker.release()
while True:
    msg, adr=server.recvfrom(1024)
    msg = msg.decode('utf-8')
    if adr not in connections:
        print(adr, "connected")
        connections.append(adr)
    t = threading.Thread(target=q, args=(adr, msg)).start()