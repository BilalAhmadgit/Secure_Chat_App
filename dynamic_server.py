import socket
import threading
import time

HOST = "0.0.0.0"  # Accept connections from any IP
PORT = 42000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # {client_socket: username}

def broadcast(message, sender_socket=None):
    for client_socket in list(clients.keys()):
        try:
            if client_socket != sender_socket:
                client_socket.send(message.encode())
        except:
            client_socket.close()
            if client_socket in clients:
                del clients[client_socket]

def broadcast_users():
    while True:
        users = list(clients.values())
        user_list_message = "USERS:" + ",".join(users)
        for client_socket in list(clients.keys()):
            try:
                client_socket.send(user_list_message.encode())
            except:
                client_socket.close()
                if client_socket in clients:
                    del clients[client_socket]
        time.sleep(5)  # Update every 5 seconds

def handle_client(client_socket, addr):
    try:
        username = client_socket.recv(1024).decode()
        clients[client_socket] = username
        print(f"[NEW CONNECTION] {username} from {addr}")

        broadcast(f"SERVER: {username} has joined the chat!")

        while True:
            message = client_socket.recv(1024).decode()
            if message.startswith("TYPING:") or message.startswith("STOP_TYPING:"):
                broadcast(message, sender_socket=client_socket)
            else:
                full_message = f"{username}: {message}"
                print(full_message)
                broadcast(full_message, sender_socket=client_socket)
    except Exception as e:
        print(f"[DISCONNECTED] {addr} - {e}")
    finally:
        if client_socket in clients:
            left_username = clients[client_socket]
            del clients[client_socket]
            broadcast(f"SERVER: {left_username} has left the chat.")
        client_socket.close()

def start_server():
    print(f"[STARTING] Server running on {HOST}:{PORT}")
    
    users_thread = threading.Thread(target=broadcast_users, daemon=True)
    users_thread.start()

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
