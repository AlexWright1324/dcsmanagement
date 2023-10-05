import asyncio
import websockets
import platform

async def connect_and_reconnect():
    while True:
        try:
            async with websockets.connect("ws://localhost:8765") as websocket:
                hostname = platform.node()
                await websocket.send(hostname)
                print(f"Connected to server from {hostname}")

                prompt = "Login: "
                while True:
                    message = input(prompt)
                    if message == "":
                        break

                    await websocket.send(message)
                    response = await websocket.recv()
                    print(response)
                    if response == "authorised":
                        prompt = "Command: "
        except Exception as e:
            print(f"Error connecting to server: {e}")
        
        await asyncio.sleep(5)  # Retry connection every 5 seconds

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_and_reconnect())