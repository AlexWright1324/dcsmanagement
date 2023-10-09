import asyncio
import websockets
import json
from schema import SchemaError
from shared import initial_schema, command_schema

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
            if data["password"] == "password":
                await handle_admin(websocket, client)
            else:
                await websocket.send("unauthorised")

        print(f"{client['hostname']} disconnected")

    except json.JSONDecodeError:
        print("Invalid JSON received.")

    except SchemaError as e:
        print(f"Schema Error: {e}")

    except Exception as e:
        print(f"Error: {e}")

async def handle_background(websocket, client):
    try:
        while True:
            await asyncio.sleep(0)
    except websockets.exceptions.ConnectionClosedError:
        pass


async def handle_admin(websocket, admin):
    async for message in websocket:
        message = json.loads(message)
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

async def main():
    await websockets.serve(handle_client, "localhost", 3000)

if __name__ == "__main__":
    asyncio.run(main())