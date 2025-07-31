import socket
import threading

clients = {}

def broadcast(message):
    for client_socket in list(clients):
        try:
            client_socket.send(message.encode('utf-8'))
        except:
            client_socket.close()
            del clients[client_socket]

def handle_client(client_socket, addr):
    try:
        #client_socket.send("NAME".encode('utf-8'))
        name = client_socket.recv(1024).decode('utf-8')
        if not name:
            client_socket.close()
            return
        clients[client_socket] = name
        broadcast(f"{name} joined the chat!")

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(f"{name}: {message}")
            else:
                break
    except:
        pass
    finally:
        if client_socket in clients:
            broadcast(f"{clients[client_socket]} left the chat.")
            del clients[client_socket]
            client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))  # Accept from all interfaces
    server.listen()

    print("Server started on port 8080...")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()
