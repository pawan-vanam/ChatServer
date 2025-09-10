import os
from flask import Flask, request
from flask_socketio import SocketIO, emit
import eventlet
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', path='/socket.io', logger=True, engineio_logger=True)

# Store connected users
connected_users = set()

@app.route("/")
def index():
    logger.info("Received request to /")
    return "Chat server is running..."

@app.errorhandler(400)
def bad_request(e):
    logger.error(f"400 Bad Request: {str(e)}, Headers: {request.headers}")
    return {"error": str(e)}, 400

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connect_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    for user_id in connected_users.copy():
        emit('login_status', {"user_id": user_id, "status": "offline"}, broadcast=True)
        connected_users.discard(user_id)

@socketio.on('message')
def handle_message(msg):
    logger.info(f"Message received: {msg}")
    socketio.send(msg, broadcast=True)

@socketio.on('login_status')
def handle_login_status(data):
    user_id = data.get("user_id")
    status = data.get("status")
    logger.info(f"Login status: {user_id} is {status}")
    if status == "online":
        connected_users.add(user_id)
    else:
        connected_users.discard(user_id)
    socketio.emit('login_status', {"user_id": user_id, "status": status}, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
