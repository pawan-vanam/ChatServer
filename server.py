from flask import Flask, request
from flask_sock import Sock
import json

app = Flask(__name__)
sock = Sock(app)

# This dictionary will store connected clients, mapping user_id to their websocket connection.
connected_clients = {}

@app.route('/health')
def health_check():
    """Responds to Render's health check pings."""
    return "OK", 200

@sock.route('/ws')
def chat_socket(ws):
    """Handles all websocket connections and real-time message relaying."""
    user_id = None
    try:
        # The first message from the client should be its user_id for registration.
        message = ws.receive(timeout=10)
        data = json.loads(message)
        if data.get("type") == "register":
            user_id = data["user_id"]
            connected_clients[user_id] = ws
            print(f"[+] User '{user_id}' connected. Total clients: {len(connected_clients)}")

        # Listen for subsequent messages from this client.
        while True:
            message = ws.receive()
            data = json.loads(message)
            message_type = data.get("type")
            receiver_id = data.get("receiver_id")

            # Relay chat messages, edits, and deletes to the recipient if they are online.
            if message_type in ["chat_message", "edit_message", "delete_message"]:
                if receiver_id in connected_clients:
                    receiver_ws = connected_clients[receiver_id]
                    try:
                        receiver_ws.send(json.dumps(data))
                        print(f"Relayed '{message_type}' from {user_id} to {receiver_id}.")
                    except Exception as e:
                        print(f"Error sending to {receiver_id}: {e}")
                else:
                    print(f"User {receiver_id} is not connected. Message not relayed.")

    except Exception as e:
        print(f"An error occurred with user {user_id}: {e}")
    finally:
        # Unregister client upon disconnection.
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]
            print(f"[-] User '{user_id}' disconnected. Total clients: {len(connected_clients)}")

if __name__ == "__main__":
    # This part is for local testing and is not used by Gunicorn on Render.
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    print("Server starting on http://localhost:5000")
    server.serve_forever()

