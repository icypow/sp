import socket
import sys
import threading
import queue
locker=threading.Lock()
queues=dict()
connections=list()
server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(((sys.argv[1]), int(sys.argv[2])))
def q():
    msg, adr=server.recvfrom(1024)
    msg = msg.decode('utf-8')
    if adr not in connections:
        print(adr, "connected")
        connections.append(adr)
    iterator=msg.find('+')
    if iterator != -1:
        queue_name, queue_msg = msg[:iterator], msg[iterator+1:]
        print("Сообщение", queue_msg, "от", adr, "в очередь", queue_name)
        if queue_name not in queues:
            locker.acquire()
            print("Создана новая очередь", queue_name)
            queues[queue_name]=queue.Queue()
            locker.release()
        queues[queue_name].join
        server.sendto("Successfully added".encode('utf-8'), adr)
        queues[queue_name].put(queue_msg)
    else:
        queue_name=msg
        if queue_name not in queues:
            server.sendto(("SERVER NOTIFICATION: Нет такой очереди").encode('utf-8'), adr)
            return
        print(adr, "берет из очереди", queue_name, )
        queues[queue_name].join
        server.sendto(queues[queue_name].get(block=True).encode('utf-8'), adr)
        if queues[queue_name].empty()==True:
            print("Удаление очереди", queue_name)
            del queues[queue_name]
while True:
    t1=threading.Thread(target=q()).start()