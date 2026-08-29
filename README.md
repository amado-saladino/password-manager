# 🔐 Secure Password Manager

A comprehensive command-line password manager built in Python with military-grade encryption and modular architecture.

## ✨ Features

### 🔒 Security
- **AES-256 encryption** for all stored passwords
- **PBKDF2 key derivation** with 100,000 iterations
- **Master password protection** with secure hashing
- **No plaintext storage** - everything is encrypted at rest

### 🎯 Core Functionality
- **Password Generation** with customizable options
- **Username/Password Mapping** for easy organization
- **Search and Filter** capabilities across all entries
- **Import/Export** functionality for data portability
- **Password Strength Analysis** with detailed feedback
- **Security Auditing** to identify weak or duplicate passwords

### 🏗️ Architecture
- **Modular Design** with clear separation of concerns
- **Hierarchical Code Organization** for maintainability
- **Comprehensive Error Handling** for robust operation
- **CLI Interface** with intuitive menu system

## 📋 Requirements

- Python 3.7 or higher
- `cryptography` library

## 🚀 Installation

1. **Clone or download** the password manager files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

## 🎮 Usage

### First Time Setup
1. Run `python main.py`
2. Create a master password (minimum 8 characters)
3. Start adding your passwords!

### Main Menu Options

| Option | Description |
|--------|-------------|
| 📝 Add new password | Create a new password entry |
| 👀 View passwords | Browse all stored passwords |
| 🔍 Search passwords | Find passwords by username, website, or notes |
| ✏️ Edit password | Modify existing password entries |
| 🗑️ Delete password | Remove password entries |
| 🎲 Generate password | Create secure passwords with custom options |
| 📤 Export data | Export passwords to JSON file |
| 📥 Import data | Import passwords from JSON file |
| 🔧 Settings | Access advanced features and utilities |

### Password Generation Options

#### Quick Generate
- Uses secure defaults (16 characters, mixed case, numbers, symbols)

#### Custom Generate
- **Length**: 8-64 characters
- **Character types**: Uppercase, lowercase, numbers, symbols
- **Exclude similar**: Option to avoid confusing characters (i, l, 1, L, o, 0, O)

#### Memorable Passwords
- Word-based passwords that are easier to remember
- Format: `Word1-Word2-Word3-Word4-99`

### Security Features

#### Password Strength Analysis
- Real-time strength scoring (0-7 scale)
- Detailed feedback for improvement
- Pattern detection for common weaknesses

#### Security Audit
- Identifies weak passwords (score < 4)
- Detects duplicate passwords across accounts
- Provides actionable recommendations

## 📁 Project Structure

```
password_manager/
├── __init__.py              # Package initialization
├── crypto_manager.py        # Encryption/decryption operations
├── password_generator.py    # Password generation utilities
├── storage_manager.py       # Data storage and retrieval
├── password_entry.py        # Password entry model and management
└── cli_interface.py         # Command-line interface

main.py                      # Application entry point
requirements.txt             # Python dependencies
README.md                    # This file
```

## 🔧 Module Overview

### `crypto_manager.py`
- **AES-256-CBC encryption** with random IV
- **PBKDF2 key derivation** for password-based encryption
- **Secure salt generation** for each encryption operation
- **Master password hashing** and verification

### `password_generator.py`
- **Customizable password generation** with multiple character sets
- **Password strength calculation** with detailed scoring
- **Memorable password generation** using word combinations
- **Pattern detection** for security analysis

### `storage_manager.py`
- **Encrypted data persistence** to local JSON files
- **Master password management** with secure hashing
- **Import/export functionality** for data portability
- **Backup creation** for data safety

### `password_entry.py`
- **Password entry data model** with metadata
- **CRUD operations** for password management
- **Search and filtering** capabilities
- **Data validation** and integrity checks

### `cli_interface.py`
- **Interactive menu system** with clear navigation
- **User input handling** with validation
- **Secure password input** (hidden from terminal)
- **Rich formatting** with emojis and colors

## 🛡️ Security Considerations

### Encryption Details
- **Algorithm**: AES-256 in CBC mode
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Salt**: 32 random bytes per encryption operation
- **IV**: 16 random bytes per encryption operation

### Data Protection
- **No plaintext storage**: All passwords encrypted before saving
- **Master password**: Never stored in plaintext, only hashed
- **Memory safety**: Sensitive data cleared when possible
- **File permissions**: Encrypted files have restricted access

### Best Practices
- **Strong master password**: Minimum 8 characters, complexity recommended
- **Regular backups**: Export data periodically
- **Secure environment**: Run on trusted systems only
- **Password hygiene**: Use unique, strong passwords for each account

## 📊 Example Usage

```bash
$ python main.py

============================================================
🔐 SECURE PASSWORD MANAGER
============================================================
A secure CLI password manager with encryption

🔐 AUTHENTICATION
Enter master password: ********
✅ Authentication successful!

========================================
📋 MAIN MENU
========================================
1. 📝 Add new password
2. 👀 View passwords
3. 🔍 Search passwords
4. ✏️ Edit password
5. 🗑️ Delete password
6. 🎲 Generate password
7. 📤 Export data
8. 📥 Import data
9. 🔧 Settings
0. 🚪 Exit

Select option (0-9): 1

📝 ADD NEW PASSWORD
------------------------------
Username/Email: john.doe@example.com

Password options:
1. Enter manually
2. Generate automatically
Choose option (1-2): 2

🔧 CUSTOM PASSWORD GENERATION
----------------------------------------
Password length (8-64) [16]: 20
Include uppercase letters? (Y/n): y
Include lowercase letters? (Y/n): y
Include numbers? (Y/n): y
Include symbols? (Y/n): y
Exclude similar characters (i,l,1,L,o,0,O)? (y/N): n

🔑 Generated Password: K8#mN2$vR9@pL5&wX3!z
💪 Strength: Very Strong (7/7)

Website (optional): example.com
Notes (optional): Main account
✅ Password added successfully! (ID: a1b2c3d4...)
```

## 🔄 Data Format

### Encrypted Storage
All data is stored in encrypted JSON format:

```json
{
  "encrypted_data": "base64-encoded-encrypted-data",
  "salt": "base64-encoded-salt",
  "iv": "base64-encoded-iv"
}
```

### Export Format
Exported data is in readable JSON format:

```json
{
  "passwords": [
    {
      "id": "unique-uuid",
      "username": "user@example.com",
      "password": "encrypted-password",
      "website": "example.com",
      "notes": "Account notes",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "exported_at": "2024-01-01T12:00:00",
  "version": "1.0"
}
```

## ⚠️ Important Notes

1. **Master Password Recovery**: There is no way to recover a forgotten master password. Keep it safe!

2. **Data Backup**: Regularly export your data to prevent loss.

3. **System Security**: Ensure your system is secure, as the application stores encrypted files locally.

4. **Dependencies**: The application requires the `cryptography` library for encryption operations.

## 🤝 Contributing

This password manager is designed with modularity in mind. Each component can be extended or modified independently:

- Add new encryption algorithms in `crypto_manager.py`
- Implement additional password generation methods in `password_generator.py`
- Extend storage backends in `storage_manager.py`
- Enhance the CLI interface in `cli_interface.py`

## 📄 License

This project is provided as-is for educational and personal use. Please review and test thoroughly before using for sensitive data.

---

**Remember**: Your security is only as strong as your master password. Choose wisely! 🔐