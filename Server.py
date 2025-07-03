from socket import *
from threading import Thread
import secure_crypto as crypto

client_sock = []
shared_keys = {}
BUFFER_SIZE = 4096

HOST = gethostbyname(gethostname())  # dynamically get local IP address
PORT = 42000         # server PORT (as per your latest setup)
ADDRESS = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Allow reusing the port immediately
SERVER.bind(ADDRESS)
SERVER.listen(10)

print(f"\n[SERVER STARTED] Listening on {HOST}:{PORT}")
print("[WAITING] Waiting for clients to connect...\n")

def handle_client(client, addr):
    try:
        print(f"[NEW CONNECTION] Client from {addr} connected.")

        # Key exchange
        pub_key = client.recv(BUFFER_SIZE)
        peer_public_key = crypto.deserialize_public_key(pub_key)
        private_key, public_key = crypto.generate_dh_key_pair()
        client.send(crypto.serialize_public_key(public_key))
        shared_key = crypto.derive_shared_key(private_key, peer_public_key)
        shared_keys[client] = shared_key
        client_sock.append(client)

        # Send welcome message
        welcome_message = "[SERVER] Welcome to the Secure Chat!"
        encrypted = crypto.encrypt_message(shared_key, welcome_message)
        client.send(encrypted)

        while True:
            try:
                msg = client.recv(BUFFER_SIZE)
                if not msg:
                    break

                decrypted = crypto.decrypt_message(shared_keys[client], msg)
                print(f"[MESSAGE] {decrypted}")
                broadcast(decrypted, sender=client)

            except Exception as e:
                print(f"[ERROR receiving/decrypting message from {addr}]: {e}")
                break

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        if client in client_sock:
            client_sock.remove(client)
        if client in shared_keys:
            del shared_keys[client]
        client.close()
        print(f"[DISCONNECTED] {addr}")

def broadcast(message, sender):
    for client in client_sock:
        if client != sender:
            try:
                encrypted = crypto.encrypt_message(shared_keys[client], message)
                client.send(encrypted)
            except Exception as e:
                print(f"[ERROR sending to client]: {e}")

while True:
    client, addr = SERVER.accept()
    Thread(target=handle_client, args=(client, addr), daemon=True).start()
