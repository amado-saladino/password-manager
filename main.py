#!/usr/bin/env python3
"""
Secure Password Manager - Main Entry Point

A comprehensive CLI password manager with encryption, secure storage,
and password generation capabilities.

Features:
- Master password authentication
- AES-256 encryption for all stored data
- Secure password generation with customizable options
- Username/password mapping and management
- Search and filtering capabilities
- Import/export functionality
- Password strength analysis and security auditing
- Modular architecture for maintainability

Usage:
    python main.py

Requirements:
    - Python 3.7+
    - cryptography library

Author: Password Manager Team
Version: 1.0.0
"""

import sys
import os

# Add the password_manager package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from password_manager.cli_interface import CLIInterface
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required dependencies are installed.")
    print("Run: pip install cryptography")
    sys.exit(1)


def main():
    """Main entry point for the password manager application"""
    try:
        # Create and run the CLI interface
        cli = CLIInterface()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using Password Manager!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
