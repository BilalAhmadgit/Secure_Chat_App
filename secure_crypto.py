import os
import hashlib
import binascii
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    PublicFormat, Encoding, load_pem_public_key
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import serialization

# Load DH parameters (from dh_params.pem)
with open("dh_params.pem", "rb") as f:
    pem_data = f.read()
    dh_parameters = serialization.load_pem_parameters(pem_data, backend=default_backend())


def generate_dh_key_pair():
    """Generate a DH key pair."""
    private_key = dh_parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key):
    """Convert public key to PEM format (bytes)."""
    return public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)


def deserialize_public_key(peer_bytes):
    """Load a peer's public key from PEM bytes."""
    return load_pem_public_key(peer_bytes, backend=default_backend())


def derive_shared_key(private_key, peer_public_key):
    """Perform DH key exchange and derive a 32-byte shared key using SHA-256."""
    shared_secret = private_key.exchange(peer_public_key)
    return hashlib.sha256(shared_secret).digest()


def encrypt_message(key, plaintext):
    """Encrypt plaintext using ChaCha20-Poly1305. Returns nonce + ciphertext."""
    nonce = os.urandom(12)  # 96-bit nonce
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext.encode(), None)
    encrypted_data = nonce + ciphertext

    # Log the encryption process
    print("\n🔐 Encrypting Message:")
    print(f"Plaintext: {plaintext}")
    print(f"Nonce: {nonce.hex()}")
    print(f"Ciphertext (hex): {ciphertext.hex()}")
    print(f"Final Encrypted Data (hex): {encrypted_data.hex()}\n")

    return encrypted_data


def decrypt_message(key, data):
    """Decrypt ChaCha20-Poly1305 encrypted data (expects nonce + ciphertext)."""
    nonce = data[:12]
    ciphertext = data[12:]
    chacha = ChaCha20Poly1305(key)
    plaintext = chacha.decrypt(nonce, ciphertext, None).decode()

    # Log the decryption process
    print("\n🔓 Decrypting Message:")
    print(f"Nonce: {nonce.hex()}")
    print(f"Ciphertext (hex): {ciphertext.hex()}")
    print(f"Plaintext: {plaintext}\n")

    return plaintext
