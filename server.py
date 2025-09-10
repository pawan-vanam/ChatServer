import asyncio
import websockets
import json
import http

# This dictionary will store connected clients, mapping user_id to their websocket connection.
connected_clients = {}

async def process_http_request(path, headers):
    """
    Handles all incoming HTTP requests.
    - Responds to Render's health check on '/health'.
    - Rejects other non-websocket HTTP requests to prevent crashes.
    """
    if path == "/health":
        return http.HTTPStatus.OK, [], b"OK\n"
    
    # If it's not a websocket upgrade request, it's likely a health check
    # to the root path or another unwanted HTTP request.
    if "Upgrade" not in headers or headers["Upgrade"].lower() != "websocket":
        # Return a simple 400 Bad Request response for any other HTTP GET/HEAD.
        return http.HTTPStatus.BAD_REQUEST, [], b"This is a WebSocket server.\n"

    # If the Upgrade header is present, let the websockets library handle it.
    return None

async def handler(websocket, path):
    """
    Handles actual websocket connections, registers clients, and broadcasts messages.
    """
    user_id = None
    try:
        message = await websocket.recv()
        data = json.loads(message)
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = websocket
            print(f"User {user_id} connected.")

        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "chat_message":
                receiver_id = data["receiver_id"]
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    await receiver_ws.send(json.dumps(data))
                    print(f"Message from {user_id} to {receiver_id} relayed.")
                else:
                    print(f"User {receiver_id} is not connected.")

    except websockets.exceptions.ConnectionClosedError:
        print(f"Connection closed for user {user_id}.")
    finally:
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"User {user_id} disconnected.")

async def main():
    port = 10000 
    host = '0.0.0.0'
    print(f"Starting websocket server on {host}:{port}...")
    
    # Use the more robust process_request function to handle all HTTP traffic.
    async with websockets.serve(handler, host, port, process_request=process_http_request):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

