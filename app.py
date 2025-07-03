from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import socket as sock
import base64

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

@socketio.on('register')
def handle_register(data):
    clients[request.sid] = data['name']
    sockets_by_name[data['name']] = request.sid
    public_keys[request.sid] = data['publicKey']
    print(f"[REGISTER] {data['name']} ({request.sid})")
    emit('users_updated', list(clients.values()), broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    sender = session.get('name')
    recipient = data.get('recipient')
    ciphertext = data.get('ciphertext')
    nonce = data.get('nonce')
    plaintext = data.get('plaintext')
    log = data.get('log', {})

    print("\n[ENCRYPTION] Encrypted message from {}:".format(sender))
    print("- Plaintext:", log.get('plaintext'))
    print("- Nonce:", log.get('nonce'))
    print("- Ciphertext:", log.get('ciphertext'))
    print("- Final Encrypted Data:", log.get('finalData'), "\n")

    if recipient in connected_users:
        recipient_sid = connected_users[recipient]['sid']
        emit('message', {
            'sender': sender,
            'ciphertext': ciphertext,
            'nonce': nonce
        }, room=recipient_sid)



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
