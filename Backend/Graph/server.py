import asyncio
import websockets

from graph import run_graph

async def handle_client(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received message: {message}")

            # Mock AI response
            response = run_graph(message)
            print("server.py")
            await websocket.send(response)
            print(f"Sent response: {response}")
    except websockets.ConnectionClosed:
        print("Client disconnected.")

async def main():
    async with websockets.serve(handle_client, "localhost", 8080):
        print("WebSocket server is running on ws://localhost:8080")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
