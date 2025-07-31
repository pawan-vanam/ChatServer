import os
from flask import Flask
from flask_socketio import SocketIO
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return "Chat server is running..."

@socketio.on('message')
def handle_message(msg):
    print("Message: ", msg)
    socketio.send(msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Use PORT env variable
    socketio.run(app, host="0.0.0.0", port=port)  # ✅ Not hardcoded 8080
