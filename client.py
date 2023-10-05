import shared
import socket
import platform
import threading
import json
from time import sleep

printqueue = shared.printqueue()

HOST, PORT = "127.0.0.1", 3001

def connect():
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((HOST, PORT))
            server.send(f"hostname:{platform.node()}".encode())
            return server
        except Exception as e:
            printqueue.put(f"Error: {str(e)}")
            printqueue.put("Reconnecting in 5 seconds...")
            sleep(5)

def receive(server):
    while True:
        try:
            data = server.recv(1024).decode('utf-8')
            if not data:
                break

            printqueue.put(f"Received: {data}")

            data = json.loads(data)

        except Exception as e:
            printqueue.put(f"Error: {str(e)}")
            break

    printqueue.put("Reconnecting...")
    server.close()
    server = connect()

server = connect()

receive = threading.Thread(target=receive, args=(server,), daemon=True)
receive.start()

while True:
    message = input("say: ")
    if message.lower() == 'quit':
        break
    server.send(message.encode())

server.close()