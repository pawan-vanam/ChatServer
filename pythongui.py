import sys
import cv2
import uuid
import socket
import threading
import pickle
import struct
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

PORT = 9999
BUFFER_SIZE = 65536

class VideoCall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Meeting")
        self.setGeometry(200, 200, 800, 600)

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Buttons
        self.btn_new_meet = QPushButton("📞 New Meeting")
        self.btn_join = QPushButton("🔗 Join with Meeting ID")
        self.meeting_input = QLineEdit()
        self.meeting_input.setPlaceholderText("Enter Meeting ID to Join")

        # Video Display
        self.local_video = QLabel("Local Video")
        self.remote_video = QLabel("Remote Video")
        self.local_video.setFixedSize(320, 240)
        self.remote_video.setFixedSize(320, 240)

        # Mic/Camera/Leave buttons
        self.btn_mic = QPushButton("🎤 Mic On")
        self.btn_camera = QPushButton("🎥 Camera On")
        self.btn_leave = QPushButton("🚪 Leave")

        self.layout.addWidget(self.btn_new_meet)
        self.layout.addWidget(self.meeting_input)
        self.layout.addWidget(self.btn_join)
        self.layout.addWidget(self.local_video)
        self.layout.addWidget(self.remote_video)

        nav = QHBoxLayout()
        nav.addWidget(self.btn_mic)
        nav.addWidget(self.btn_camera)
        nav.addWidget(self.btn_leave)
        self.layout.addLayout(nav)

        # Flags
        self.camera_on = True
        self.mic_on = True
        self.running = False

        self.btn_new_meet.clicked.connect(self.start_meeting)
        self.btn_join.clicked.connect(self.join_meeting)
        self.btn_camera.clicked.connect(self.toggle_camera)
        self.btn_mic.clicked.connect(self.toggle_mic)
        self.btn_leave.clicked.connect(self.leave_meeting)

    def start_meeting(self):
        self.meeting_id = str(uuid.uuid4())[:8]
        print(f"[STARTED] Meeting ID: {self.meeting_id}")
        self.running = True
        threading.Thread(target=self.start_video_server, daemon=True).start()
        self.start_local_camera()

    def join_meeting(self):
        self.server_ip = self.meeting_input.text()
        self.running = True
        threading.Thread(target=self.start_video_client, daemon=True).start()
        self.start_local_camera()

    def toggle_camera(self):
        self.camera_on = not self.camera_on
        self.btn_camera.setText("🎥 Camera On" if self.camera_on else "🚫 Camera Off")

    def toggle_mic(self):
        self.mic_on = not self.mic_on
        self.btn_mic.setText("🎤 Mic On" if self.mic_on else "🔇 Mic Off")

    def leave_meeting(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()
        self.local_video.clear()
        self.remote_video.clear()
        print("[LEFT] Meeting Ended")

    def start_local_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        if not self.camera_on or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if ret:
            rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape
            img = QImage(rgb_img.data, w, h, ch * w, QImage.Format_RGB888)
            self.local_video.setPixmap(QPixmap.fromImage(img).scaled(320, 240))

    def start_video_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", PORT))
        print("[WAITING] For participant to join...")
        while self.running:
            try:
                msg, addr = s.recvfrom(BUFFER_SIZE)
                frame = pickle.loads(msg)
                np_frame = cv2.imdecode(frame, 1)
                self.display_remote_frame(np_frame)
            except:
                pass

    def start_video_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                data = pickle.dumps(imgencode)
                client_socket.sendto(data, (self.server_ip, PORT))

    def display_remote_frame(self, frame):
        rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        img = QImage(rgb_img.data, w, h, ch * w, QImage.Format_RGB888)
        self.remote_video.setPixmap(QPixmap.fromImage(img).scaled(320, 240))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VideoCall()
    win.show()
    sys.exit(app.exec_())
