import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
from datetime import datetime

# Server code
def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 5555))  # Bind to all interfaces
        server.listen()
        
        clients = {}
        
        def broadcast(message, sender_socket):
            for client_socket in clients:
                if client_socket != sender_socket:
                    try:
                        client_socket.send(message.encode('utf-8'))
                    except:
                        client_socket.close()
                        del clients[client_socket]
        
        def handle_client(client_socket, addr):
            try:
                client_socket.send("NAME".encode('utf-8'))
                name = client_socket.recv(1024).decode('utf-8')
                if not name:
                    client_socket.close()
                    return
                clients[client_socket] = name
                broadcast(f"{name} joined!", client_socket)
                
                while True:
                    message = client_socket.recv(1024).decode('utf-8')
                    if message:
                        broadcast(f"{name}: {message}", client_socket)
                    else:
                        break
            except:
                if client_socket in clients:
                    broadcast(f"{clients[client_socket]} left!", client_socket)
                    del clients[client_socket]
                    client_socket.close()
        
        while True:
            client_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.daemon = True
            thread.start()
    except Exception as e:
        print(f"Server error: {str(e)}")

# Client GUI code
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Chat App")
        self.root.geometry("400x600")
        self.root.configure(bg="#ECE5DD")
        
        # Socket setup
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TEntry", padding=10)
        self.style.configure("TButton", padding=10)
        
        # Username entry screen
        self.create_login_screen()
    
    def create_login_screen(self):
        self.login_frame = tk.Frame(self.root, bg="#ECE5DD")
        self.login_frame.pack(fill="both", expand=True)
        
        # Modern WhatsApp-like header
        tk.Label(self.login_frame, text="Chat App", font=("Helvetica", 20, "bold"), 
                bg="#ECE5DD", fg="#128C7E").pack(pady=20)
        
        tk.Label(self.login_frame, text="Enter your username:", 
                font=("Helvetica", 12), bg="#ECE5DD").pack(pady=10)
        
        self.username_entry = ttk.Entry(self.login_frame, width=30, 
                                      font=("Helvetica", 12))
        self.username_entry.pack(pady=10)
        
        ttk.Button(self.login_frame, text="Connect", 
                  command=self.connect_to_server).pack(pady=10)
    
    def create_chat_screen(self):
        # Clear login screen
        self.login_frame.destroy()
        
        # Main chat frame
        self.chat_frame = tk.Frame(self.root, bg="#ECE5DD")
        self.chat_frame.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(self.chat_frame, bg="#128C7E")
        header.pack(fill="x")
        tk.Label(header, text="Chat App", font=("Helvetica", 14, "bold"), 
                bg="#128C7E", fg="white").pack(pady=10, padx=10, side="left")
        
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=20, 
            font=("Helvetica", 12),
            bg="white",
            bd=0
        )
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.chat_area.config(state='disabled')
        
        # Message input frame
        input_frame = tk.Frame(self.chat_frame, bg="#ECE5DD")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.message_entry = ttk.Entry(input_frame, width=30, 
                                     font=("Helvetica", 12))
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.message_entry.bind("<Return>", self.send_message)
        
        send_button = ttk.Button(input_frame, text="Send", 
                               command=self.send_message)
        send_button.pack(side="right")
    
    def connect_to_server(self):
        username = self.username_entry.get().strip()
        if not username:
            tk.messagebox.showerror("Input Error", "Please enter a username")
            return
        
        try:
            self.client.connect(('192.168.0.176', 5555))  # Your server's local IP
            self.client.send(username.encode('utf-8'))
            self.connected = True
            self.create_chat_screen()
            
            # Start receiving messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            tk.messagebox.showerror("Connection Error", 
                                  f"Unable to connect to server: {str(e)}")
    
    def send_message(self, event=None):
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if message:
            try:
                self.client.send(message.encode('utf-8'))
                self.display_message(f"You: {message}")
                self.message_entry.delete(0, tk.END)
            except:
                self.connected = False
                tk.messagebox.showerror("Error", "Connection lost")
    
    def receive_messages(self):
        while self.connected:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
            except:
                self.connected = False
                break
    
    def display_message(self, message):
        self.chat_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    # Run server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Run client GUI
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()