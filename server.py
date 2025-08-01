import os
from flask import Flask
from flask_socketio import SocketIO, emit
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store connected users
connected_users = set()

@app.route("/")
def index():
    return "Chat server is running..."

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('message')
def handle_message(msg):
    print("Message received: ", msg)
    socketio.send(msg, broadcast=True)

@socketio.on('login_status')
def handle_login_status(data):
    user_id = data.get("user_id")
    status = data.get("status")
    if status == "online":
        connected_users.add(user_id)
    else:
        connected_users.discard(user_id)
    print(f"Login status: {user_id} is {status}")
    socketio.emit('login_status', {"user_id": user_id, "status": status}, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
