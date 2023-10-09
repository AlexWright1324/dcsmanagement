import asyncio
import websockets
import json
from schema import SchemaError
from shared import initial_schema, command_server_schema, command_client_schema

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
        await websocket.wait_closed()
    except websockets.exceptions.ConnectionClosedError:
        pass


async def handle_admin(websocket, admin):
    async for message in websocket:
        try:
            message = json.loads(message)
            message = command_server_schema.validate(message)
            command = message["command"]
            command = command_client.validate(command)
            if "targets" in message:
                socks = set()
                for key, client in clients.items():
                    if client["hostname"] in message["targets"]:
                        socks.add(key)
                await websockets.broadcast(socks, json.dumps(command))
	    elif command["command"] == "listclients":
                hostnames = {"hostnames": [i["hostname"] for i in clients.values()]}
                await websocket.send(json.dumps(hostnames))

        except json.JSONDecodeError as e:
            print("Invalid JSON from {client['hostname']}: {e}")

        except SchemaError as e:
            print(f"Schema Error from {client['hostname']}: {e}")

        except Exception as e:
            print(f"Error from {client['hostname']}: {e}")

async def main():
    await websockets.serve(handle_client, "0.0.0.0", 3000)

if __name__ == "__main__":
    asyncio.run(main())
