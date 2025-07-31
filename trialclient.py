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
        self.master.resizable(True, True)
        self.username = None
        self.sio = socketio.Client()

        self.reply_to = None
        self.reply_label = None
        self.pinned_message_label = None
        self.active_menu = None

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
        # Bind Enter key to work when focused on username_entry
        self.username_entry.bind('<Return>', lambda event: self.join_chat())

        # Optional: set focus to username entry by default
        self.username_entry.focus_set()

    def join_chat(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            return

        self.login_frame.pack_forget()
        self.setup_chat_screen()

        self.sio.on('message', self.on_message)

        def connect_to_server():
            try:
                self.sio.connect("https://chatserver-iu2c.onrender.com", transports=["polling", "websocket"])
                self.sio.send(f"{self.username} joined the chat!")
            except Exception as e:
                self.display_message(f"Connection error: {e}")

        threading.Thread(target=connect_to_server, daemon=True).start()

    def set_reply(self, message):
        if ": " in message:
            sender, content = message.split(": ", 1)
        else:
            content = message

        self.reply_to = content
        if self.reply_label:
            self.reply_label.destroy()

        self.reply_label = ctk.CTkLabel(self.chat_frame, text=f"Replying to: {content}", text_color="gray", font=("Segoe UI", 12, "italic"))
        self.reply_label.pack(side="top", pady=(0, 5))

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            if self.reply_to:
                full_message = f"(Reply to: {self.reply_to})\n{self.username}: {message}"
            else:
                full_message = f"{self.username}: {message}"

            self.sio.send(full_message)
            self.display_message(full_message, is_self=True)
            self.message_entry.delete(0, tk.END)

            self.reply_to = None
            if self.reply_label:
                self.reply_label.destroy()
                self.reply_label = None

    def on_message(self, message):
        self.display_message(message)

    def delete_message_widget(self, widget):
        widget.destroy()

    def pin_message(self, message):
        if not self.pinned_message_label:
            self.pinned_frame.pack(fill="x", padx=0, pady=(0, 5))

        if self.pinned_message_label:
            self.pinned_message_label.destroy()

        self.pinned_message_label = ctk.CTkFrame(self.pinned_frame, fg_color="#f1f1f1")
        self.pinned_message_label.pack(fill="x", padx=10, pady=5)

        label = ctk.CTkLabel(
            self.pinned_message_label,
            text=f"📌 {message}",
            font=("Segoe UI", 14, "italic"),
            text_color="#222222",
            anchor="w"
        )
        label.pack(side="left", padx=5, pady=5)

        unpin_btn = ctk.CTkButton(
            self.pinned_message_label,
            text="Unpin",
            width=50,
            height=20,
            font=("Segoe UI", 12),
            command=self.unpin_message,
            fg_color="#DD4444",
            text_color="white",
            hover_color="#BB3333"
        )
        unpin_btn.pack(side="right", padx=5, pady=5)

    def unpin_message(self):
        if self.pinned_message_label:
            self.pinned_message_label.destroy()
            self.pinned_message_label = None
            self.pinned_frame.pack_forget()

    def show_message_options(self, event, widget, message):
        if self.active_menu:
            self.active_menu.destroy()

        self.active_menu = ctk.CTkToplevel(self.master)
        self.active_menu.wm_overrideredirect(True)
        self.active_menu.configure(bg="#2b2b2b")

        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        self.active_menu.geometry(f"140x135+{x}+{y}")

        def close_menu(e=None):
            if self.active_menu:
                self.active_menu.destroy()
                self.active_menu = None

        def make_button(text, command):
            btn = ctk.CTkButton(self.active_menu, text=text, command=lambda: [command(), close_menu()],
                                fg_color="#3a3a3a", hover_color="#5a5a5a", text_color="white", corner_radius=5)
            btn.pack(fill="x", padx=5, pady=4)

        make_button("💬 Reply", lambda: self.set_reply(message))
        make_button("📌 Pin", lambda: self.pin_message(message))
        make_button("❌ Delete", lambda: self.delete_message_widget(widget))

        self.active_menu.bind("<FocusOut>", close_menu)
        self.active_menu.focus_set()

    def display_message(self, message, is_self=False):
        timestamp = datetime.now().strftime("%I:%M %p")

        reply_part = ""
        content = message
        if message.startswith("(Reply to:"):
            try:
                reply_part, content = message.split(")\n", 1)
                reply_part += ")"
            except:
                content = message

        if ": " in content:
            sender, actual_message = content.split(": ", 1)
        else:
            sender, actual_message = "Server", content

        if sender == self.username and not is_self:
            return

        align = "e" if sender == self.username else "w"
        bubble_color = "#DCF8C6" if sender == self.username else "#FFFFFF"
        text_align = "right" if sender == self.username else "left"

        container = ctk.CTkFrame(self.scrollable_chat, fg_color="transparent")
        container.pack(anchor=align, pady=5, padx=10, fill="x")

        bubble_frame = ctk.CTkFrame(container, fg_color=bubble_color, corner_radius=15)
        bubble_frame.pack(anchor=align, padx=5)

        bubble_frame.bind("<Button-3>", lambda e, w=container, m=message: self.show_message_options(e, w, m))
        bubble_frame.bind("<Double-Button-1>", lambda e, msg=message: self.set_reply(msg))

        sender_label = ctk.CTkLabel(
            bubble_frame,
            text=f"{sender} ({timestamp})",
            font=("Segoe UI", 12, "bold"),
            text_color="#555555",
            justify=text_align
        )
        sender_label.pack(anchor=align, padx=10, pady=(5, 0))

        if reply_part:
            reply_box = ctk.CTkFrame(bubble_frame, fg_color="#E8E8E8", corner_radius=10)
            reply_box.pack(anchor=align, padx=10, pady=(0, 5), fill="x")
            reply_label = ctk.CTkLabel(reply_box, text=reply_part[11:-1], font=("Segoe UI", 12, "italic"), text_color="#333333", justify=text_align)
            reply_label.pack(anchor=align, padx=8, pady=4)

        message_label = ctk.CTkLabel(
            bubble_frame,
            text=actual_message,
            font=("Segoe UI", 16),
            text_color="#000000",
            justify=text_align
        )
        message_label.pack(anchor=align, padx=10, pady=(0, 10))

        self.scrollable_chat._parent_canvas.yview_moveto(1.0)

    def setup_chat_screen(self):
        self.chat_frame = ctk.CTkFrame(self.master, corner_radius=0, fg_color="#F0F2F5")
        self.chat_frame.pack(fill="both", expand=True)

        self.pinned_frame = ctk.CTkFrame(self.chat_frame, fg_color="#f1f1f1", corner_radius=0)
        # Don't pack initially

        self.scrollable_chat = ctk.CTkScrollableFrame(self.chat_frame, fg_color="#F0F2F5", corner_radius=0)
        self.scrollable_chat.pack(fill="both", expand=True, padx=10, pady=(0, 0))

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
