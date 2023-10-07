import asyncio
import websockets
import json
from schema import SchemaError
from shared import initial_schema, login_schema, command_schema

clients = {}

async def handle_client(websocket, _path):
    try:
        data = json.loads(await websocket.recv())
        data = initial_schema.validate(data)
        client = {"hostname": data["hostname"]}
        print(f"{client['hostname']} connected")
        if data["mode"] == "background":
            clients[websocket] = client
            await handle_background(websocket, client)
            del clients[websocket]
        elif data["mode"] == "admin":
            client["authorised"] = False
            await handle_admin(websocket, client)
    except SchemaError as e:
        print(f"Schema Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"{client['hostname']} disconnected")


async def handle_background(websocket, client):
    async for message in websocket:
        pass

async def handle_admin(websocket, admin):
    async for message in websocket:
        message = json.loads(message)
        if login_schema.is_valid(message):
            message = login_schema.validate(message)
            if admin["authorised"]:
                print(f"{admin.hostname} already authorised")
                response = {"response" : "authorised"}
                await websocket.send(json.dumps(response))
            elif message["login"] == "xa6Ev8ae":
                admin["authorised"] = True
                print(f"{admin['hostname']} now authorised")
                response = {"response" : "authorised"}
                await websocket.send(json.dumps(response))
            else:
                response = {"response" : "unauthorised"}
                await websocket.send(json.dumps(response))
        elif admin["authorised"]:
            message = command_schema.validate(message)
            if message["command"] == "listclients":
                hostnames = {"hostnames": [i["hostname"] for i in clients.values()]}
                await websocket.send(json.dumps(hostnames))
            elif message["command"] == "logoff":
                data = {"action": "logoff"}
                if "targets" in message:
                    for sock, client in clients.pairs():
                        if client["hostname"] in message["targets"]:
                            await sock.send(json.dumps(data))
                else:
                    woadmin = list(clients.keys())
                    if admin["hostname"] in woadmin:
                        woadmin.remove(admin["hostname"])
                    websockets.broadcast(woadmin, json.dumps(data))
        else:
            response = {"response" : "unauthorised"}
            await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_client, "localhost", 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
