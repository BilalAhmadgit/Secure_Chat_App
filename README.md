# Secure Chat Application with ChaCha20 and Socket Communication

## 📌 Overview
A secure, real-time chat application that leverages **ChaCha20-Poly1305 encryption** and **Diffie-Hellman (DH) key exchange** to ensure end-to-end encrypted communication. The application supports multiple interfaces, including a **desktop GUI (Tkinter)** and a **web-based interface (Flask + Socket.IO)**, providing users with a seamless and secure messaging experience.

---

## 🔐 Key Features
- **End-to-End Encryption**: Messages are encrypted using **ChaCha20-Poly1305**, ensuring confidentiality and integrity.
- **Secure Key Exchange**: **Diffie-Hellman key exchange** is used to derive shared keys without transmitting them over the network.
- **Multi-Platform Support**: 
  - Desktop client built with **Tkinter**.
  - Web interface using **Flask and Socket.IO** for real-time communication.
- **Real-Time Messaging**: Low-latency message exchange with support for multiple concurrent users.
- **User-Friendly Interface**: Clean, intuitive UI with a WhatsApp-like dark theme.

---

## 🛠️ Technologies Used
- **Programming Language**: Python
- **Cryptography**: `cryptography` library (ChaCha20-Poly1305, DH key exchange)
- **Networking**: `socket` module for TCP/IP communication, `Flask-SocketIO` for WebSocket support
- **GUI**: 
  - Desktop: `Tkinter`
  - Web: `Flask`, `HTML`, `JavaScript`
- **Concurrency**: `threading` for handling multiple clients

---

## 📂 Project Structure
```
Secure_Chat_Application/
├── server.py              # Main server script (handles connections and encryption)
├── client_1.py            # Desktop client (Tkinter GUI)
├── client_2.py            # Alternate desktop client (optional)
├── app.py                 # Web server (Flask + Socket.IO)
├── secure_crypto.py       # Cryptographic functions (DH, ChaCha20)
├── templates/             # Flask HTML templates
│   ├── login.html         # Login page
│   └── chat.html          # Chat interface
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Required libraries: Install via `pip install -r requirements.txt`  
  (Example requirements: `flask`, `flask-socketio`, `cryptography`)

### Running the Application
1. **Start the Server**:
   ```bash
   python server.py
   ```
   The server will start on a local IP (e.g., `192.168.1.X:42000`).

2. **Launch Desktop Clients**:
   ```bash
   python client_1.py
   ```
   Enter the server IP, port, and your name when prompted.

3. **Launch the Web Interface**:
   ```bash
   python app.py
   ```
   Access the chat at `http://<server-ip>:5000` in your browser.

---

## 🔧 How It Works
1. **Key Exchange**:  
   - Clients and server perform a DH key exchange to derive a shared secret key.
2. **Message Encryption**:  
   - Messages are encrypted with ChaCha20-Poly1305 before transmission.
3. **Real-Time Communication**:  
   - The server routes encrypted messages to all connected clients.
4. **Decryption**:  
   - Clients decrypt received messages using the shared key.

---

## 📊 Performance Metrics
| Metric                  | Result          |
|-------------------------|-----------------|
| Encryption Time         | ~1.5 ms         |
| Decryption Time         | ~1.4 ms         |
| Latency (LAN)           | < 50 ms         |
| Concurrent Clients      | 10+             |

---

## 🔮 Future Enhancements
- **Perfect Forward Secrecy (PFS)**: Regularly rotate keys for added security.
- **Group Messaging**: Extend support for multi-user chats.
- **Mobile App**: Port to Android/iOS using frameworks like Kivy.
- **File Sharing**: Encrypted file transfer capability.
- **User Authentication**: Implement OAuth or password-based login.

---

## 📚 References
1. [ChaCha20-Poly1305 RFC 8439](https://datatracker.ietf.org/doc/html/rfc8439)
2. [Diffie-Hellman Key Exchange (MDN)](https://developer.mozilla.org/en-US/docs/Web/Security/Key_Exchange/Diffie-Hellman)
3. [Python Cryptography Library](https://cryptography.io/en/latest/)
4. [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)

---

## 👥 Contributors
- Kishor Kumar Nair  
- Vishwa Teja Jetti  
- Bilal Shaikh  
- Sai Nandan Reddy  
- **Guide**: Mr. Olusola Agboola  

---

## 📜 License
This project is open-source under the MIT License. See [LICENSE](LICENSE) for details.
