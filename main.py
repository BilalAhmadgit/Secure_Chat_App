import streamlit as st
import socket
import threading
import queue
import secure_crypto as crypto

# Queue for thread-safe message updates
message_queue = queue.Queue()

st.set_page_config(page_title="Entice Chat Web", layout="centered")
st.title("🔐 Entice Chat - Secure Web Client")

# Session defaults
if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.messages = []
    st.session_state.client = None
    st.session_state.shared_key = None
    st.session_state.name = ""

# Input fields
host = st.text_input("Server IP", value="127.0.0.1")
port = st.number_input("Server Port", min_value=1024, max_value=65535, value=42000)
name = st.text_input("Your Name", value="Guest")
password = st.text_input("Connection Password", type="password")

# Authentication password (can be moved to env var or config file)
EXPECTED_PASSWORD = "Bilal@123"


# Connect button
if st.button("Connect") and not st.session_state.connected:
    if password != EXPECTED_PASSWORD:
        st.error("Incorrect password. Access denied.")
    else:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))

            # DH key exchange
            private_key, public_key = crypto.generate_dh_key_pair()
            client.send(crypto.serialize_public_key(public_key))
            peer_bytes = client.recv(4096)
            peer_public_key = crypto.deserialize_public_key(peer_bytes)
            shared_key = crypto.derive_shared_key(private_key, peer_public_key)

            # Save state
            st.session_state.client = client
            st.session_state.shared_key = shared_key
            st.session_state.connected = True
            st.session_state.name = name
            st.success(f"Connected as {name} to {host}:{port}")

            # Start receiving thread
            def receive():
                message_queue.put(f"✅ Connected as {name}")
                while True:
                    try:
                        data = client.recv(4096)
                        if not data:
                            break
                        msg = crypto.decrypt_message(shared_key, data)
                        message_queue.put(msg)
                    except Exception as e:
                        message_queue.put(f"[ERROR] {str(e)}")
                        break

            threading.Thread(target=receive, daemon=True).start()

        except Exception as e:
            st.error(f"Connection failed: {e}")

# Chat UI
if st.session_state.connected:
    while not message_queue.empty():
        st.session_state.messages.append(message_queue.get())

    for msg in st.session_state.messages:
        st.markdown(f"`{msg}`")

    user_input = st.text_input("Type a message:", key="chat_input")
    if st.button("Send"):
        if user_input:
            try:
                full_msg = f"{st.session_state.name}: {user_input}"
                st.session_state.messages.append(full_msg)
                encrypted = crypto.encrypt_message(st.session_state.shared_key, full_msg)
                st.session_state.client.send(encrypted)
            except Exception as e:
                st.error(f"Failed to send message: {e}")
