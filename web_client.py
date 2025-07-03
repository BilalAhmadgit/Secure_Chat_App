import streamlit as st
import socket
import threading
import secure_crypto as crypto

# Streamlit settings
st.title("Secure Chat - Streamlit Interface")

if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.messages = []

HOST = st.text_input("Enter server host", "127.0.0.1")
PORT = st.number_input("Enter port", value=42000)
NAME = st.text_input("Enter your name")

if st.button("Connect") and not st.session_state.connected:
    try:
        CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT.connect((HOST, PORT))

        # Key exchange
        private_key, public_key = crypto.generate_dh_key_pair()
        CLIENT.send(crypto.serialize_public_key(public_key))
        peer_bytes = CLIENT.recv(4096)
        peer_public_key = crypto.deserialize_public_key(peer_bytes)
        shared_key = crypto.derive_shared_key(private_key, peer_public_key)

        st.session_state.CLIENT = CLIENT
        st.session_state.shared_key = shared_key
        st.session_state.connected = True
        st.success("Connected successfully!")

        def receive_messages():
            while True:
                try:
                    data = CLIENT.recv(4096)
                    if not data:
                        break
                    msg = crypto.decrypt_message(shared_key, data)
                    st.session_state.messages.append(msg)
                    st.experimental_rerun()
                except:
                    break

        threading.Thread(target=receive_messages, daemon=True).start()

    except Exception as e:
        st.error(f"Connection error: {e}")

if st.session_state.connected:
    for msg in st.session_state.messages:
        st.write(msg)

    user_input = st.text_input("Type your message:")
    if st.button("Send"):
        if user_input:
            full_msg = f"{NAME}: {user_input}"
            st.session_state.messages.append(full_msg)
            encrypted = crypto.encrypt_message(st.session_state.shared_key, full_msg)
            st.session_state.CLIENT.send(encrypted)
