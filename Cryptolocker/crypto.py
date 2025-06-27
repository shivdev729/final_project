import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
import json
import struct
import time
from metastore import add_entry
from metastore import delete_entry_by_hash

class HashMismatchError(RuntimeError):
    """Raised when the hash of the decrypted file does not match the original hash."""
    pass

def _derive_key(key_str: str) -> bytes:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(key_str.encode('utf-8'))
    return digest.finalize()

def encrypt_file(key_str: str, input_filepath: str, output_filepath: str) -> None:
    """Encrypts a file using AES-256-CBC. Writes to output_filepath."""
    key = _derive_key(key_str)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    # Prepare metadata
    # Calculate SHA-256 hash of the original file
    hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
    with open(input_filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    file_hash = hasher.finalize().hex()

    metadata = {
        "filename": os.path.basename(input_filepath),
        "timestamp": time.time(),
        "hash": file_hash,
    }
    add_entry(metadata)
    metadata_json = json.dumps(metadata).encode('utf-8')
    metadata_len = len(metadata_json)
    header = struct.pack('>I', metadata_len)  # 4-byte big-endian unsigned int

    with open(input_filepath, 'rb') as f:
        plaintext = f.read()
    padded_data = padder.update(plaintext) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_filepath, 'wb') as f:
        f.write(header)
        f.write(metadata_json)
        f.write(iv)
        f.write(ciphertext)

def decrypt_file(key_str: str, input_filepath: str, output_filepath: str) -> None:
    """Decrypts a file encrypted with AES-256-CBC. Writes to output_filepath."""
    try:
        key = _derive_key(key_str)
        with open(input_filepath, 'rb') as f:
            # Read metadata length (4 bytes)
            header = f.read(4)
            if len(header) != 4:
                raise RuntimeError("Invalid file format: missing metadata length header.")
            metadata_len = struct.unpack('>I', header)[0]
            # Read metadata
            metadata_json = f.read(metadata_len)
            if len(metadata_json) != metadata_len:
                raise RuntimeError("Invalid file format: incomplete metadata.")
            metadata = json.loads(metadata_json.decode('utf-8'))
            # Read IV
            iv = f.read(16)
            if len(iv) != 16:
                raise RuntimeError("Invalid file format: missing IV.")
            # Read ciphertext
            ciphertext = f.read()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        # Verify hash
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(plaintext)
        calculated_hash = hasher.finalize().hex()
        if calculated_hash != metadata.get("hash"):
            raise HashMismatchError("Hash mismatch: file may be corrupted or tampered with.")
        with open(output_filepath, 'wb') as f:
            f.write(plaintext)
            # Try to delete entry by hash, raise error if not found
            delete_entry_by_hash(metadata.get("hash"))
            return metadata
    except Exception as e:
        raise RuntimeError(f"Error decrypting file: {e}")
