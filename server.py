import shared
import socket
import threading
import json

printqueue = shared.printqueue()

HOST, PORT = "", 3001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen(100)
clients = []

class Client:
    def __init__(self, socket, hostname):
        self.socket = socket
        self.hostname = hostname
        self.authorised = False

def handler(client: Client):
    while True:
        try:
            data = client.socket.recv(1024).decode('utf-8')
            if not data:
                break

            printqueue.put(f"Received from {client.hostname}: {data}")

            data = json.loads(data)

            for recipient in clients:
                if client != recipient:
                    recipient.send(data.encode('utf-8'))

        except Exception as e:
            printqueue.put(f"Error: {str(e)}")
            break

    clients.remove(client)
    client.socket.close()

while True:
    printqueue.put("Waiting for a connection...")
    client_socket, address = server_socket.accept()

    data = client_socket.recv(1024).decode('utf-8')
    if data.startswith("hostname:"):
        hostname = data[9:]

        printqueue.put(f"Accepted connection from {hostname} at {address[0]}:{address[1]}")

        client = Client(client_socket, hostname)

        clients.append(client)

        client_handler = threading.Thread(target=handler, args=(client,))
        client_handler.start()
    else:
        printqueue.put(f"Bad hostname from {address}")
        client_socket.close()


