import threading
from queue import Queue

def printer(queue):
    while True:
        print(queue.get())

def printqueue() -> Queue:
    printqueue = Queue()
    thread = threading.Thread(target=printer, args=(printqueue,), daemon=True)
    thread.start()
    return printqueue