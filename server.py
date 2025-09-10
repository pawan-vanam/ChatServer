from flask import Flask
from flask_sock import Sock
import json

# 1. Initialize the Flask App and the WebSocket Extension
app = Flask(__name__)
sock = Sock(app)

# This dictionary will store connected clients (user_id -> websocket connection)
connected_clients = {}

# 2. Create a standard HTTP route for Render's health checks
@app.route('/health')
def health_check():
    """Responds to Render's HTTP health pings with a 200 OK."""
    print("[Health Check] Responded with OK.")
    return "OK", 200

# 3. Create the main WebSocket route for the chat
@sock.route('/ws')
def chat_socket(ws):
    """Handles the entire lifecycle of a WebSocket connection."""
    user_id = None
    try:
        # The first message from the client must be for registration
        registration_message = ws.receive(timeout=10) # Wait for 10 seconds
        data = json.loads(registration_message)
        
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = ws
            print(f"[+] User '{user_id}' connected. Total clients: {len(connected_clients)}")
        else:
            print("[!] First message was not a registration. Closing connection.")
            return # This closes the connection

        # Loop forever, listening for messages from this client
        while True:
            message = ws.receive()
            data = json.loads(message)

            if data.get("type") == "chat_message":
                receiver_id = data.get("receiver_id")
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    receiver_ws.send(json.dumps(data))
                    print(f"[*] Relayed message from '{user_id}' to '{receiver_id}'.")
                else:
                    print(f"[!] Receiver '{receiver_id}' not connected. Message not relayed.")
    
    except Exception as e:
        print(f"[!] An error occurred with user '{user_id}': {e}")
    finally:
        # When the loop breaks or an error occurs, unregister the client
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"[-] User '{user_id}' disconnected. Total clients: {len(connected_clients)}")

