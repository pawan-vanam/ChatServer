import asyncio
import websockets
import json
import http

# This dictionary will store connected clients, mapping user_id to their websocket connection.
connected_clients = {}

async def health_check_handler(path, headers):
    """
    Handles incoming HTTP requests *before* they become websockets.
    This is crucial for responding to Render's health checks.
    """
    print(f"[*] Received pre-websocket request for path: {path}")
    if path == "/health":
        print("[+] Responding to health check with OK.")
        return http.HTTPStatus.OK, [], b"OK\n"
    
    # If the request is not for the health check path, we let the main
    # websocket handler take over by returning None.
    return None

async def chat_handler(websocket, path):
    """
    Handles the main logic for an active websocket connection.
    """
    user_id = None
    try:
        # The first message from the client is for registration
        registration_message = await websocket.recv()
        data = json.loads(registration_message)
        
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = websocket
            print(f"[+] User '{user_id}' registered and connected. Total clients: {len(connected_clients)}")
        else:
            print(f"[!] First message was not a registration. Closing connection.")
            return

        # Main loop to listen for messages from this client
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "chat_message":
                receiver_id = data.get("receiver_id")
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    await receiver_ws.send(json.dumps(data))
                    print(f"[*] Relayed message from '{user_id}' to '{receiver_id}'.")
                else:
                    print(f"[!] Could not relay message. Receiver '{receiver_id}' is not connected.")

    except websockets.exceptions.ConnectionClosedOK:
        print(f"[-] User '{user_id}' disconnected gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[!] User '{user_id}' disconnected with error: {e}")
    except Exception as e:
        print(f"[!!!] An unexpected error occurred with user '{user_id}': {e}")
    finally:
        # Unregister client upon disconnection
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"[-] User '{user_id}' unregistered. Total clients: {len(connected_clients)}")

async def main():
    port = 10000 
    host = '0.0.0.0'
    print(f"[*] Starting Chatify server on {host}:{port}...")
    
    # The `process_request` argument is the key. It runs `health_check_handler`
    # on every incoming connection before attempting a websocket handshake.
    async with websockets.serve(chat_handler, host, port, process_request=health_check_handler):
        await asyncio.Future()  # Keep the server running forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[*] Server is shutting down.")

