import asyncio
import websockets
import platform
import json
from shared import command_client_schema
from schema import SchemaError
from os import system, listdir

async def connect_and_reconnect():
    while True:
        try:
            async with websockets.connect("ws://mc.uwcs.co.uk:3000") as websocket:
                msg = {
                    "mode": "background",
                    "hostname": platform.node()
                }
                await websocket.send(json.dumps(msg))

                print("Connected to server")

                async for message in websocket:
                    try:
                        data = json.loads(message)
                        data = command_client_schema.validate(data)
                        if data["command"] == "logout":
                            force = 1

                            if "args" in data and "force" in data["args"]:
                                force = 0
                            system(f"qdbus-qt5 org.kde.ksmserver /KSMServer logout {force} 0 1")
                        elif data["command"] == "ls":
                            listeam = listdir("~/.var/")
                            lilutris = listdir("~/.var/")
                            msg = {"steam": listeam, "lutris": lilutris}
                            await websocket.send(json.dumps(msg))
                    except json.JSONDecodeError as e:
                        print("JSON Error: {e}")
                    except SchemaError as e:
                        print("Schema Error: {e}")
                        # Shouldnt trust the server

        except websockets.ConnectionClosedError:
            print("Connection to the server closed.")

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(5)  # Retry connection every 5 seconds

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_and_reconnect())
