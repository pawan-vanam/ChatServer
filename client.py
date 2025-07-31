import socketio
import threading
import tkinter as tk
import customtkinter as ctk
from datetime import datetime

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chatify - Socket.IO")
        self.master.geometry("460x600")
        self.master.resizable(False, False)
        self.username = None
        self.sio = socketio.Client()

        self.setup_login()

    def setup_login(self):
        self.login_frame = ctk.CTkFrame(self.master, corner_radius=15)
        self.login_frame.pack(expand=True)

        title = ctk.CTkLabel(self.login_frame, text="💬 Chatify", font=("Segoe UI", 30, "bold"))
        title.pack(pady=(40, 20))

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter your name", font=("Segoe UI", 16), width=300)
        self.username_entry.pack(pady=10)

        self.join_button = ctk.CTkButton(self.login_frame, text="Join Chat", command=self.join_chat, font=("Segoe UI", 16), width=300)
        self.join_button.pack(pady=20)

    def join_chat(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            return

        self.login_frame.pack_forget()
        self.setup_chat_screen()

        self.sio.on('message', self.on_message)

        def connect_to_server():
            try:
                self.sio.connect("https://e3987f38-a3b3-4666-a61f-6e0e8c2cfb1f-00-36xaklllb1dtd.sisko.replit.dev/", transports=["websocket"])
                self.sio.send(f"{self.username} joined the chat!")
            except Exception as e:
                self.display_message(f"Connection error: {e}")

        threading.Thread(target=connect_to_server, daemon=True).start()

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.sio.send(f"{self.username}: {message}")
            self.display_message(f"{self.username}: {message}", is_self=True)
            self.message_entry.delete(0, tk.END)

    def on_message(self, message):
        self.display_message(message)

    def display_message(self, message, is_self=False):
        timestamp = datetime.now().strftime("%I:%M %p")

        if ": " in message:
            sender, content = message.split(": ", 1)
        else:
            sender, content = "Server", message

        if sender == self.username and not is_self:
            return

        container = ctk.CTkFrame(self.scrollable_chat, fg_color="transparent")
        container.pack(anchor="w", pady=5, padx=5, fill="x")

        bubble_color = "#DCF8C6" if sender == self.username else "#FFFFFF"
        bubble_frame = ctk.CTkFrame(container, fg_color=bubble_color, corner_radius=15)
        bubble_frame.pack(anchor="w", padx=5)

        sender_label = ctk.CTkLabel(bubble_frame, text=f"{sender} ({timestamp})", font=("Segoe UI", 12, "bold"), text_color="#555555")
        sender_label.pack(anchor="w", padx=10, pady=(5, 0))

        message_label = ctk.CTkLabel(bubble_frame, text=content, font=("Segoe UI", 16), text_color="#000000")
        message_label.pack(anchor="w", padx=10, pady=(0, 10))

        self.scrollable_chat._parent_canvas.yview_moveto(1.0)

    def setup_chat_screen(self):
        self.chat_frame = ctk.CTkFrame(self.master, corner_radius=0, fg_color="#F0F2F5")
        self.chat_frame.pack(fill="both", expand=True)

        self.scrollable_chat = ctk.CTkScrollableFrame(self.chat_frame, fg_color="#F0F2F5", corner_radius=0)
        self.scrollable_chat.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.bottom_frame = ctk.CTkFrame(self.chat_frame, fg_color="#E0E0E0", corner_radius=0)
        self.bottom_frame.pack(fill="x", side="bottom")

        self.message_entry = ctk.CTkEntry(self.bottom_frame, placeholder_text="Type your message", font=("Segoe UI", 16), width=350)
        self.message_entry.pack(side="left", padx=(10, 5), pady=10, fill="x", expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(self.bottom_frame, text="Send", command=self.send_message, font=("Segoe UI", 14))
        self.send_button.pack(side="right", padx=(5, 10), pady=10)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = ChatClient(root)
    root.mainloop()
