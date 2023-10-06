from schema import Schema, And, Use, Or, Optional

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

initial_schema = Schema({
    "mode": And(str, Use(str.lower),
                lambda m: m in ("background" , "admin")),
    "hostname": str,
    }
)

login_schema = Schema({
    "login": str
    }
)

authorised_schema = Schema({
    "response": lambda m: m in ("authorised", "unauthorised")
    }
)

command_schema = Schema({
    "command": And(str, Use(str.lower),
                lambda m: m in ("logoff" , "rm", "ls steam", "ls lutris")),
    "target": Optional([str])
    }
)

admin_schema = Or(login_schema, command_schema)

#response_schema = BASED ON TARGETS SERVER / CLIENT