import tkinter as tk
from tkinter import simpledialog
import sys, time
from socket import *
from threading import Thread
import secure_crypto as crypto

# Popup to ask Server IP, Port, and Name
startup = tk.Tk()
startup.withdraw()
HOST = simpledialog.askstring("Server IP", "Enter Server IP:", parent=startup)
PORT = int(simpledialog.askstring("Port", "Enter Server Port:", parent=startup))
NAME = simpledialog.askstring("Name", "Enter your name:", parent=startup)
startup.destroy()

BUFFER_SIZE = 4096
ADDRESS = (HOST, PORT)

CLIENT = socket(AF_INET, SOCK_STREAM)
CLIENT.connect(ADDRESS)

private_key, public_key = crypto.generate_dh_key_pair()
CLIENT.send(crypto.serialize_public_key(public_key))
peer_bytes = CLIENT.recv(BUFFER_SIZE)
peer_public_key = crypto.deserialize_public_key(peer_bytes)
shared_key = crypto.derive_shared_key(private_key, peer_public_key)

# WhatsApp-like Dark Theme
BG_COLOR = "#121212"
TEXT_COLOR = "#E0E0E0"
BUTTON_COLOR = "#25D366"
ENTRY_BG = "#1E1E1E"
FONT = ("Helvetica", 14)

# Main Window
top = tk.Tk()
top.title("Secure Chat - " + NAME)
top.configure(bg=BG_COLOR)
top.geometry("500x600")

def receive():
    msg_list.insert(tk.END, f"\u2705 Welcome, {NAME}!")
    msg_list.insert(tk.END, "\U0001F7E2 You are online.")
    while True:
        try:
            data = CLIENT.recv(BUFFER_SIZE)
            if not data:
                break
            decrypted = crypto.decrypt_message(shared_key, data)
            msg_list.insert(tk.END, decrypted)
            msg_list.yview(tk.END)
        except Exception as e:
            msg_list.insert(tk.END, f"[ERROR] {str(e)}")
            break

def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    if msg:
        full_msg = f"{NAME}: {msg}"
        msg_list.insert(tk.END, full_msg)
        encrypted = crypto.encrypt_message(shared_key, full_msg)
        CLIENT.send(encrypted)
        msg_list.yview(tk.END)

def on_closing(event=None):
    msg_list.insert(tk.END, "\u26D4 You went offline.")
    time.sleep(1)
    CLIENT.close()
    top.quit()
    sys.exit()

# Message Frame
messages_frame = tk.Frame(top, bg=BG_COLOR)
scrollbar = tk.Scrollbar(messages_frame)
msg_list = tk.Listbox(messages_frame, height=25, width=70, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, yscrollcommand=scrollbar.set, highlightthickness=0, selectbackground=BUTTON_COLOR)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
messages_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Entry Field
entry_frame = tk.Frame(top, bg=BG_COLOR)
my_msg = tk.StringVar()
entry_field = tk.Entry(entry_frame, textvariable=my_msg, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT, relief=tk.FLAT)
entry_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
entry_field.bind("<Return>", send)
send_button = tk.Button(entry_frame, text="Send", command=send, bg=BUTTON_COLOR, fg="white", font=FONT, relief=tk.FLAT)
send_button.pack(side=tk.RIGHT)
entry_frame.pack(padx=10, pady=10, fill=tk.X)

# Event Bindings
top.protocol("WM_DELETE_WINDOW", on_closing)
receive_thread = Thread(target=receive)
receive_thread.start()

# Start GUI
tk.mainloop()
