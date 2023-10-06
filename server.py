import asyncio
import websockets
import json
from schema import Schema_Error
from shared import initial_schema, admin_schema

clients = {}

async def handle_client(websocket, _path):
    try:
        data = await websocket.recv()
	data = initial_schema.validate(data)
	client = {"hostname": data["hostname"]}
        print(f"{client["hostname"]} connected")
	match data["mode"]:
            case "background":
		clients[websocket] = client
                handle_background(websocket, client)
		del clients[websocket]
            case "admin":
                handle_admin(websocket, client)
    except Schema_Error as e:
        print(f"Schema Error: {e}")
    except Exception as e:
        print(f"Error with client from {hostname}: {e}")
    finally:
        print(f"{hostname} disconnected")

def handle_admin(websocket, admin):
        async for message in websocket:
            message = admin_schema.validate(message)
            if "login" in message:
                if admin["authorised"]:
                    print(f"{client.hostname} already authorised")
                    response = {"response" : "authorised"}
                    await websocket.send(json.dumps(response))
                elif message["login"] == hash("xa6Ev8ae"):
                    admin["authorised"] = True
                    print(f"{client.hostname} now authorised")
                    response = {"response" : "authorised"}
                    await websocket.send(json.dumps(response))
                else:
                    response = {"response" : "unauthorised"}
                    await websocket.send(json.dumps(response))
            elif admin["authorised"]:
                match message["command"]:
                    case "listclients":
                        hostnames = {"hostnames": [i["hostname"] for i in clients.values()]}
                        await websocket.send(json.dumps(hostnames))
                    case "logoff":
                        data = {"action": "logoff"}
                        if "targets" in message:
                            for sock, client in clients.pairs():
                                if client["hostname"] in message["targets"]:
                                    await sock.send(json.dumps(data))
                        else:
                            woadmin = clients.keys()
                            woadmin.remove(admin["hostname"])
                            await websocket.broadcast(woadmin, json.dumps(data))
            else:
                response = {"response" : "unauthorised"}
                await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_client, "localhost", 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
