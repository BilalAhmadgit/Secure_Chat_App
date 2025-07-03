from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import socket as sock
import binascii
from secure_crypto import decrypt_message  # Make sure this exists and is correct

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}         # sid -> name
sockets_by_name = {} # name -> sid
public_keys = {}     # sid -> public key (JWK string)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['server_ip'] = request.form['server_ip']
        session['server_port'] = request.form['server_port']
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', name=session['name'])

@socketio.on('connect')
def handle_connect():
    print(f"[CONNECTED] {request.sid}")
    emit('users_updated', list(clients.values()), broadcast=True)

@socketio.on('register')
def handle_register(data):
    clients[request.sid] = data['name']
    sockets_by_name[data['name']] = request.sid
    public_keys[request.sid] = data['publicKey']
    print(f"[REGISTER] {data['name']} ({request.sid})")
    emit('users_updated', list(clients.values()), broadcast=True)

@socketio.on('exchange_keys')
def handle_key_exchange(target_user):
    if target_user in sockets_by_name:
        emit('peer_key', {
            'user': clients[request.sid],
            'key': public_keys[request.sid]
        }, room=sockets_by_name[target_user])

@socketio.on('send_message')
def handle_message(data):
    sender = clients[request.sid]
    recipient = data.get('recipient')
    log = data.get('log', {})

    try:
        nonce = binascii.unhexlify(data.get('nonce'))
        ciphertext = binascii.unhexlify(data.get('ciphertext'))
        encrypted_data = nonce + ciphertext

        # 🔐 Replace this with actual shared key logic (from DH)
        shared_key = b'your_32_byte_shared_key_here'  # e.g. derived from DH exchange

        plaintext = decrypt_message(shared_key, encrypted_data)
    except Exception as e:
        print(f"[ERROR] Failed to decrypt message: {e}")
        plaintext = "[DECRYPTION FAILED]"

    # Debug logs
    print("\nEncrypting Message:")
    print("Plaintext:", log.get('plaintext'))
    print("Nonce:", data.get('nonce'))
    print("Ciphertext:", data.get('ciphertext'))
    print("Final Encrypted Data:", log.get('finalData'), "\n")

    print("Decrypting Message:")
    print("Nonce:", data.get('nonce'))
    print("Ciphertext:", data.get('ciphertext'))
    print("Plaintext:", plaintext)
    print(f"[MESSAGE] {sender}: {plaintext}\n")

    recipient_sid = sockets_by_name.get(recipient)
    if recipient_sid:
        emit('message', {
            'sender': sender,
            'ciphertext': data.get('ciphertext'),
            'nonce': data.get('nonce')
        }, room=recipient_sid)

        emit('message', {
            'sender': sender,
            'ciphertext': data.get('ciphertext'),
            'nonce': data.get('nonce')
        }, room=request.sid)
    else:
        print(f"[ERROR] {recipient} is not online.")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in clients:
        name = clients.pop(request.sid)
        sockets_by_name.pop(name, None)
        public_keys.pop(request.sid, None)
        print(f"[DISCONNECT] {name}")
        emit('users_updated', list(clients.values()), broadcast=True)

if __name__ == '__main__':
    hostname = sock.gethostname()
    local_ip = sock.gethostbyname(hostname)
    print(f"Web server running at http://{local_ip}:5000")
    socketio.run(app, host=local_ip, port=5000, debug=True)
