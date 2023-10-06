import asyncio
import websockets
import platform
import json
from shared import authorised_schema
from schema import SchemaError

async def connect_and_reconnect():
    while True:
        try:
            async with websockets.connect("ws://localhost:3000") as websocket:
                msg = {
                    "mode": "admin",
                    "hostname": platform.node()
                }
                await websocket.send(json.dumps(msg))
                print("Connected to server")

                authorised = False

                while not authorised:
                    password = input("Enter password: ")
                    login = {
                        "login": password
                    }
                    await websocket.send(json.dumps(login))

                    data = await websocket.recv()
                    try:
                        data = json.loads(data)
                        data = authorised_schema.validate(data)
                        if data["response"] == "authorised":
                            authorised = True
                            while True:
                                command = input("Enter a command: ")
                                await websocket.send(json.dumps({"command": command}))
                        else:
                            print("Wrong password. Please re-login.")
                    except SchemaError:
                        print("False Schema")

        except websockets.ConnectionClosedError:
            print("Connection to the server closed.")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(5)  # Retry connection every 5 seconds

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_and_reconnect())