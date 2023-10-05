import asyncio
import websockets
import json

class Client:
    def __init__(self, hostname):
        self.hostname = hostname
        self.authorised = False
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

clients = {}

async def handle_client(websocket, path):
    try:
        hostname = await websocket.recv()
        
        client = Client(hostname)
        clients[websocket] = client

        print(f"{client.hostname} connected")
        
        async for message in websocket:
            if message == "xa6Ev8ae":
                client.authorised = True
                print(f"{client.hostname} authorised")
                await websocket.send(f"authorised")
            elif message == "list":
                if not client.authorised:
                    await websocket.send("unauthorised")
                else:
                    hostnames = json.dumps([i.toJSON() for i in clients.values()])
                    await websocket.send(hostnames)
            else:
                break
    except Exception as e:
        print(f"Error with client from {hostname}: {e}")
    finally:
        del clients[websocket]
        print(f"{hostname} disconnected")

# Start the WebSocket server
start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()