# WhatsApp-Like Streamlit Client with Auto-Send on Enter
import streamlit as st
import socket
import threading
import secure_crypto as crypto
import queue
from datetime import datetime

# Setup
st.set_page_config(page_title="Entice Chat - WhatsApp Style", layout="centered")
st.markdown("""
    <style>
    .message-right {
        background-color: #dcf8c6;
        padding: 8px;
        border-radius: 10px;
        margin: 5px;
        text-align: right;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .message-left {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 10px;
        margin: 5px;
        text-align: left;
        max-width: 70%;
        float: left;
        clear: both;
    }
    .chat-container {
        background-color: #ece5dd;
        padding: 10px;
        height: 500px;
        overflow-y: scroll;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Globals
message_queue = queue.Queue()

if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.messages = []
    st.session_state.client = None
    st.session_state.shared_key = None
    st.session_state.name = ""
if 'relay_ready' not in st.session_state:
    st.session_state.relay_ready = False

# Inputs
host = st.text_input("Server IP", value="")
port = st.number_input("Server Port", value=42000)
name = st.text_input("Your Name", value="Client2")

# Connect
if st.button("Connect") and not st.session_state.connected:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        private_key, public_key = crypto.generate_dh_key_pair()
        client.send(crypto.serialize_public_key(public_key))
        peer_bytes = client.recv(4096)
        peer_public_key = crypto.deserialize_public_key(peer_bytes)
        shared_key = crypto.derive_shared_key(private_key, peer_public_key)

        st.session_state.client = client
        st.session_state.shared_key = shared_key
        st.session_state.connected = True
        st.session_state.name = name
        st.session_state.messages = []
        st.session_state.relay_ready = True

        st.success(f"Connected to {host}:{port} as {name}")

        def receive():
            message_queue.put(f"🟢 Connected to {host}:{port} as {name}")
            while True:
                try:
                    data = client.recv(4096)
                    if not data:
                        break
                    msg = crypto.decrypt_message(shared_key, data)
                    message_queue.put(msg)
                    st.rerun()
                except Exception as e:
                    message_queue.put(f"[ERROR] {str(e)}")
                    break

        threading.Thread(target=receive, daemon=True).start()

    except Exception as e:
        st.error(f"Connection failed: {e}")

# Chat Interface
if st.session_state.connected:
    while not message_queue.empty():
        st.session_state.messages.append(message_queue.get())

    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if ":" in msg:
                user, message = msg.split(":", 1)
                timestamp = datetime.now().strftime("%I:%M %p")
                if user.strip() == st.session_state.name:
                    st.markdown(f"""
                        <div class='message-right'>
                            <b>{user.strip()}</b>: {message.strip()}<br>
                            <small>{timestamp}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='message-left'>
                            <b>{user.strip()}</b>: {message.strip()}<br>
                            <small>{timestamp}</small>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.write(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.relay_ready:
        user_input = st.text_input("Type a message", key="input")
        if user_input:  # Auto send on Enter
            try:
                full_msg = f"{st.session_state.name}: {user_input}"
                encrypted = crypto.encrypt_message(st.session_state.shared_key, full_msg)
                st.session_state.client.send(encrypted)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to send message: {e}")
    else:
        st.warning("Waiting for the other client to connect...")
