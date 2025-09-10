import asyncio
import websockets
import json
import http # Import the http module

# This dictionary will store connected clients, mapping user_id to their websocket connection.
connected_clients = {}

async def health_check(path, headers):
    """
    Responds to Render's health check pings.
    If the request path is '/health', it returns a 200 OK response.
    Otherwise, it allows the websocket connection to proceed.
    """
    if path == "/health":
        return http.HTTPStatus.OK, [], b"OK\n"
    return None # Let the main handler process the connection

async def handler(websocket, path):
    """
    Handles websocket connections, registers clients, and broadcasts messages.
    """
    user_id = None
    try:
        # The first message from the client should be its user_id for registration.
        message = await websocket.recv()
        data = json.loads(message)
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = websocket
            print(f"User {user_id} connected.")

        # Listen for subsequent messages from this client.
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "chat_message":
                receiver_id = data["receiver_id"]
                
                # Check if the receiver is connected.
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    # Forward the message to the receiver.
                    await receiver_ws.send(json.dumps(data))
                    print(f"Message from {user_id} to {receiver_id} relayed.")
                else:
                    print(f"User {receiver_id} is not connected.")

    except websockets.exceptions.ConnectionClosedError:
        print(f"Connection closed for user {user_id}.")
    finally:
        # Unregister client upon disconnection.
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"User {user_id} disconnected.")

async def main():
    # When deploying to Render, use port 10000 and host 0.0.0.0
    port = 10000 
    host = '0.0.0.0'
    print(f"Starting websocket server on {host}:{port}...")
    # Add the process_request parameter to handle health checks
    async with websockets.serve(handler, host, port, process_request=health_check):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

