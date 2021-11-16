from socket import *

HOST = '127.0.0.1'
PORT = 5555


with socket(AF_INET, SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall('Hello, sockets!'.encode())
    data = sock.recv(256)  # while True:
    print(data.decode())
