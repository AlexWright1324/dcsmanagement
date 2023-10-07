import asyncio
import websockets
import platform
import json
from shared import action_schema
from schema import SchemaError
from os import system

async def connect_and_reconnect():
    while True:
        try:
            async with websockets.connect("ws://localhost:3000") as websocket:
                msg = {
                    "mode": "background",
                    "hostname": platform.node()
                }
                await websocket.send(json.dumps(msg))
                print("Connected to server")

                async for message in websocket:
                    data = json.loads(message)
                    try:
                        data = action_schema.validate(data)
                        if data["action"] == "logoff":
                            system("qdbus-qt5 org.kde.ksmserver /KSMServer logout 1 0 1")
                    except SchemaError:
                        print("False Schema")
        except websockets.ConnectionClosedError:
            print("Connection to the server closed.")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(5)  # Retry connection every 5 seconds

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_and_reconnect())