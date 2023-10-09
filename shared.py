from schema import Schema, Or, Optional

"""
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
"""

initial_schema = Schema(Or({
    "mode": "background",
    "hostname": str,
}, {
    "mode": "admin",
    "hostname": str,
    "password": str
}))

command_client_schema = Schema({
    "command": str,
    "args": Optional([str])
})

command_server_schema = Schema({
    "targets": [str],
    "command": command_client_schema
})

client_response_schema = Schema(Or({
    "error": None,
    "result": dict # TODO
}, {
    "error": str
}, only_one=True))

server_response_schema = Schema([{
    "hostname": str,
    "response": client_response_schema
}])

"""
authorised_schema = Schema({
    "response": lambda m: m in ("authorised", "unauthorised")
    }
)

command_schema = Schema({
    "command": And(str, Use(str.lower),
                lambda m: m in ("logoff" , "listclient")),
    Optional("targets"): [str]
    }
)

action_schema = Schema({
    "action": And(str, Use(str.lower),
                lambda m: m in ("logoff")),
    }
)
"""