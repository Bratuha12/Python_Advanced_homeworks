from socket import *

HOST = '127.0.0.1'  # '0.0.0.0'
PORT = 5555


def handle_connection(client, addr):
    while True:
        data = client.recv(256)  # waiting for data
        if not data:
            break
        data = f'Эти данные отправлены обратно - {data.decode()}'
        data = data.encode()
        client.sendall(data)


def start_server():
    with create_server((HOST, PORT)) as sock:
        print(f'Listening on {HOST}: {PORT}')
        while True:
            client, addr = sock.accept()  # waiting for connection
            with client:
                host, port = addr
                print(f'Connected from {host}:{port}')
                handle_connection(client, addr)


if __name__ == '__main__':
    start_server()
