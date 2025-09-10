from flask import Flask, request
from flask_sock import Sock
import json
import os

app = Flask(__name__)
sock = Sock(app)

# This dictionary will store connected clients, mapping user_id to their websocket connection.
connected_clients = {}

@app.route('/health')
def health_check():
    """Responds to Render's health checks."""
    return "OK", 200

@sock.route('/ws')
def chat_socket(ws):
    """Handles all websocket connections and message broadcasting."""
    user_id = None
    try:
        # The first message from the client should be its user_id for registration.
        message = ws.receive(timeout=10) # Add a timeout for registration
        data = json.loads(message)
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = ws
            print(f"[+] User '{user_id}' connected. Total clients: {len(connected_clients)}")

        # Listen for subsequent messages from this client.
        while True:
            message = ws.receive() # This will now wait indefinitely without timing out the worker
            data = json.loads(message)
            if data.get("type") == "chat_message":
                receiver_id = data.get("receiver_id")
                
                # Check if the receiver is connected.
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    try:
                        receiver_ws.send(json.dumps(data))
                        print(f"[*] Message from {user_id} to {receiver_id} relayed.")
                    except Exception as e:
                        print(f"[!] Failed to send message to {receiver_id}: {e}")
                else:
                    print(f"[-] User {receiver_id} is not connected.")

    except Exception as e:
        # This will catch timeouts, disconnections, and other errors.
        print(f"[!] An error occurred for user {user_id}: {e}")
    finally:
        # Unregister client upon disconnection.
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"[-] User '{user_id}' disconnected. Total clients: {len(connected_clients)}")

if __name__ == "__main__":
    # This part is for local testing and is not used by Gunicorn on Render.
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    port = int(os.environ.get("PORT", 5000))
    server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
    print(f"Server listening on port {port}...")
    server.serve_forever()

