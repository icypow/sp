import socket
import sys
import threading
import zlib
import hashlib
while True:
    str=hashlib.md5(input().encode('utf-8')).hexdigest()
    print(str, len(str))