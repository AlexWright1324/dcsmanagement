from schema import Schema, And, Use, Or

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
    "authorised": bool
    }
)

command_schema = Schema({
    "command": And(str, Use(str.lower),
                lambda m: m in ("logoff" , "rm", "ls steam", "ls lutris")),
    "target": [str]
    }
)
listclients_schema = Schema({
    "command": lambda m: m in ("listclients")
})

clientcommand_schema = Schema({
    "command": And(str, Use(str.lower),
                lambda m: m in ("logoff" , "rm", "ls steam", "ls lutris"))
    }
)

admin_schema = Or(login_schema, command_schema)

#response_schema = BASED ON TARGETS SERVER / CLIENT