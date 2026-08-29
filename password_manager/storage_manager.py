"""
Data storage and retrieval operations with encryption
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from .crypto_manager import CryptoManager


class StorageManager:
    """Manages encrypted storage of password data"""
    
    def __init__(self, data_file='passwords.json', master_file='master.json'):
        self.data_file = data_file
        self.master_file = master_file
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        data_dir = os.path.dirname(self.data_file) or '.'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_master_password(self, password: str) -> bool:
        """Save hashed master password"""
        try:
            master_data = CryptoManager.hash_master_password(password)
            master_data['created_at'] = datetime.now().isoformat()
            
            with open(self.master_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving master password: {e}")
            return False
    
    def verify_master_password(self, password: str) -> bool:
        """Verify master password against stored hash"""
        try:
            if not os.path.exists(self.master_file):
                return False
            
            with open(self.master_file, 'r') as f:
                master_data = json.load(f)
            
            return CryptoManager.verify_master_password(password, master_data)
        except Exception as e:
            print(f"Error verifying master password: {e}")
            return False
    
    def has_master_password(self) -> bool:
        """Check if master password exists"""
        return os.path.exists(self.master_file)
    
    def save_passwords(self, passwords: List[Dict], master_password: str) -> bool:
        """Save encrypted password data"""
        try:
            # Add metadata
            data = {
                'passwords': passwords,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            json_data = json.dumps(data, indent=2)
            encrypted_data = CryptoManager.encrypt_data(json_data, master_password)
            
            with open(self.data_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving passwords: {e}")
            return False
    
    def load_passwords(self, master_password: str) -> List[Dict]:
        """Load and decrypt password data"""
        try:
            if not os.path.exists(self.data_file):
                return []
            
            with open(self.data_file, 'r') as f:
                encrypted_data = json.load(f)
            
            decrypted_json = CryptoManager.decrypt_data(encrypted_data, master_password)
            data = json.loads(decrypted_json)
            
            return data.get('passwords', [])
        except Exception as e:
            print(f"Error loading passwords: {e}")
            return []
    
    def backup_data(self, backup_file: str) -> bool:
        """Create a backup of the encrypted data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                return True
            return False
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False