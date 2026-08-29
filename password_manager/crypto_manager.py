"""
Cryptographic operations for password encryption and decryption
"""

import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib


class CryptoManager:
    """Handles all cryptographic operations for the password manager"""
    
    SALT_LENGTH = 32
    IV_LENGTH = 16
    KEY_LENGTH = 32
    ITERATIONS = 100000
    
    @staticmethod
    def generate_salt() -> bytes:
        """Generate a random salt for key derivation"""
        return os.urandom(CryptoManager.SALT_LENGTH)
    
    @staticmethod
    def generate_iv() -> bytes:
        """Generate a random initialization vector"""
        return os.urandom(CryptoManager.IV_LENGTH)
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=CryptoManager.KEY_LENGTH,
            salt=salt,
            iterations=CryptoManager.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def encrypt_data(data: str, password: str) -> dict:
        """Encrypt data using AES-256-CBC"""
        salt = CryptoManager.generate_salt()
        iv = CryptoManager.generate_iv()
        key = CryptoManager.derive_key(password, salt)
        
        # Pad data to block size
        padded_data = CryptoManager._pad_data(data.encode())
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'salt': base64.b64encode(salt).decode(),
            'iv': base64.b64encode(iv).decode()
        }
    
    @staticmethod
    def decrypt_data(encrypted_dict: dict, password: str) -> str:
        """Decrypt data using AES-256-CBC"""
        try:
            encrypted_data = base64.b64decode(encrypted_dict['encrypted_data'])
            salt = base64.b64decode(encrypted_dict['salt'])
            iv = base64.b64decode(encrypted_dict['iv'])
            
            key = CryptoManager.derive_key(password, salt)
            
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            data = CryptoManager._unpad_data(padded_data)
            return data.decode()
        except Exception as e:
            raise ValueError("Failed to decrypt data. Invalid password or corrupted data.")
    
    @staticmethod
    def hash_master_password(password: str) -> dict:
        """Hash master password for verification"""
        salt = CryptoManager.generate_salt()
        key = CryptoManager.derive_key(password, salt)
        password_hash = hashlib.sha256(key).hexdigest()
        
        return {
            'hash': password_hash,
            'salt': base64.b64encode(salt).decode()
        }
    
    @staticmethod
    def verify_master_password(password: str, stored_hash: dict) -> bool:
        """Verify master password against stored hash"""
        try:
            salt = base64.b64decode(stored_hash['salt'])
            key = CryptoManager.derive_key(password, salt)
            password_hash = hashlib.sha256(key).hexdigest()
            return password_hash == stored_hash['hash']
        except:
            return False
    
    @staticmethod
    def _pad_data(data: bytes) -> bytes:
        """Apply PKCS7 padding to data"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    @staticmethod
    def _unpad_data(padded_data: bytes) -> bytes:
        """Remove PKCS7 padding from data"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]