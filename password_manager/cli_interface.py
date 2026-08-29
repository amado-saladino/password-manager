"""
Command-line interface for the password manager
"""

import getpass
import sys
import os
from typing import Optional
from datetime import datetime, timedelta
from .password_entry import PasswordManager
from .storage_manager import StorageManager
from .password_generator import PasswordGenerator


class CLIInterface:
    """Command-line interface for password manager"""
    
    def __init__(self):
        self.storage_manager = StorageManager()
        self.password_manager = PasswordManager(self.storage_manager)
        self.authenticated = False
    
    def run(self):
        """Main application loop"""
        self.print_banner()
        
        # Check if master password exists
        if not self.storage_manager.has_master_password():
            self.setup_master_password()
        else:
            self.authenticate()
        
        if self.authenticated:
            self.main_menu()
    
    def print_banner(self):
        """Print application banner"""
        print("=" * 60)
        print("🔐 SECURE PASSWORD MANAGER")
        print("=" * 60)
        print("A secure CLI password manager with encryption")
        print()
    
    def setup_master_password(self):
        """Set up initial master password"""
        print("🔧 INITIAL SETUP")
        print("Create a master password to secure your vault.")
        print("⚠️  Remember this password - it cannot be recovered!")
        print()
        
        while True:
            password = getpass.getpass("Enter master password: ")
            if len(password) < 8:
                print("❌ Master password must be at least 8 characters long.")
                continue
            
            confirm = getpass.getpass("Confirm master password: ")
            if password != confirm:
                print("❌ Passwords do not match. Please try again.")
                continue
            
            # Check password strength
            strength = PasswordGenerator.calculate_strength(password)
            print(f"Password strength: {strength['strength']} ({strength['score']}/{strength['max_score']})")
            
            if strength['score'] < 4:
                print("⚠️  Warning: Weak master password detected.")
                choice = input("Continue anyway? (y/N): ").lower()
                if choice != 'y':
                    continue
            
            if self.password_manager.setup_master_password(password):
                print("✅ Master password created successfully!")
                self.authenticated = True
                break
            else:
                print("❌ Failed to create master password. Please try again.")
    
    def authenticate(self):
        """Authenticate user with master password"""
        print("🔐 AUTHENTICATION")
        attempts = 3
        
        while attempts > 0:
            password = getpass.getpass("Enter master password: ")
            
            if self.password_manager.authenticate(password):
                print("✅ Authentication successful!")
                self.authenticated = True
                break
            else:
                attempts -= 1
                if attempts > 0:
                    print(f"❌ Invalid password. {attempts} attempts remaining.")
                else:
                    print("❌ Authentication failed. Exiting.")
                    sys.exit(1)
    
    def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            print("\n" + "=" * 40)
            print("📋 MAIN MENU")
            print("=" * 40)
            print("1. 📝 Add new password")
            print("2. 👀 View passwords")
            print("3. 🔍 Search passwords")
            print("4. 🔎 Advanced search")
            print("5. ✏️  Edit password")
            print("6. 🗑️  Delete password")
            print("7. 🎲 Generate password")
            print("8. 🔧 Settings")
            print("0. 🚪 Exit")
            print()
            
            choice = input("Select option (0-8): ").strip()
            
            if choice == '1':
                self.add_password()
            elif choice == '2':
                self.view_passwords()
            elif choice == '3':
                self.search_passwords()
            elif choice == '4':
                self.advanced_search()
            elif choice == '5':
                self.edit_password()
            elif choice == '6':
                self.delete_password()
            elif choice == '7':
                self.generate_password_menu()
            elif choice == '8':
                self.settings_menu()
            elif choice == '0':
                print("👋 Thank you for using password manager!")
                break
            else:
                print("❌ Invalid option. Please try again.")

    def get_multiline_input(self, allow_keep: bool = False, current_value: str = "") -> str:
        """Get multi-line text input from user until 'END' is typed on a new line."""
        lines = []
        first_line = True
        while True:
            try:
                line = input()
                if line.strip() == "END":
                    break
                if first_line and not line:
                    if allow_keep:
                        return current_value
                    else:
                        break
                first_line = False
                lines.append(line)
            except EOFError:
                break
        
        result = "\n".join(lines).strip()
        if allow_keep and not result and not lines:
            return current_value
        return result
    
    def add_password(self):
        """Add a new password entry"""
        print("\n📝 ADD NEW PASSWORD")
        print("-" * 30)
        
        username = input("Username/Email: ").strip()
        if not username:
            print("❌ Username cannot be empty.")
            return
        
        # Suggest websites based on existing entries
        website_input = input("Website (optional): ").strip()
        if website_input:
            suggestions = self.password_manager.get_website_suggestions(website_input)
            if suggestions:
                print(f"💡 Similar websites found: {', '.join(suggestions[:3])}")
        
        print("\nPassword options:")
        print("1. Enter manually")
        print("2. Generate automatically")
        
        choice = input("Choose option (1-2): ").strip()
        
        if choice == '2':
            password = self.generate_password_interactive()
            if not password:
                return
        else:
            password = getpass.getpass("Password: ")
            if not password:
                print("❌ Password cannot be empty.")
                return
        
        website = website_input
        print("Notes (optional - multi-line supported. Type 'END' on a new line when finished):")
        notes = self.get_multiline_input()
        
        entry = self.password_manager.add_entry(username, password, website, notes)
        print(f"✅ Password added successfully! (ID: {entry.id[:8]}...)")
    
    def view_passwords(self):
        """View all password entries with pagination"""
        entries = self.password_manager.get_all_entries()
        
        if not entries:
            print("\n📭 No passwords stored yet.")
            return
        
        print(f"\n👀 ALL PASSWORDS ({len(entries)} entries)")
        print("-" * 60)
        
        # Pagination
        page_size = 10
        total_pages = (len(entries) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(entries))
            page_entries = entries[start_idx:end_idx]
            
            print(f"\nPage {current_page} of {total_pages}")
            print("-" * 40)
            
            # Show summary list first
            for i, entry in enumerate(page_entries, start_idx + 1):
                print(f"{i}. {entry.username} - {entry.website or 'No website'} - {entry.created_at.strftime('%Y-%m-%d')}")
            
            print(f"\nOptions:")
            print(f"• Enter number (1-{end_idx}) to view details")
            if total_pages > 1:
                print(f"• [p]revious page, [n]ext page, [g]oto page")
            print(f"• [m]ain menu")
            
            choice = input("\nChoose: ").lower().strip()
            
            # Handle navigation
            if choice == 'm':
                break
            elif choice == 'n' and current_page < total_pages:
                current_page += 1
                continue
            elif choice == 'p' and current_page > 1:
                current_page -= 1
                continue
            elif choice == 'g' and total_pages > 1:
                try:
                    page = int(input(f"Go to page (1-{total_pages}): "))
                    if 1 <= page <= total_pages:
                        current_page = page
                        continue
                    else:
                        print("❌ Invalid page number.")
                        continue
                except ValueError:
                    print("❌ Invalid page number.")
                    continue
            
            # Handle entry selection
            try:
                entry_num = int(choice)
                if start_idx + 1 <= entry_num <= end_idx:
                    entry = entries[entry_num - 1]
                    self.view_single_entry(entry)
                else:
                    print("❌ Invalid entry number.")
            except ValueError:
                print("❌ Invalid option. Please try again.")
    
    def view_single_entry(self, entry):
        """View details of a single password entry"""
        print(f"\n📋 PASSWORD DETAILS")
        print("-" * 30)
        print(f"ID: {entry.id[:8]}...")
        print(f"Username: {entry.username}")
        print(f"Website: {entry.website or 'N/A'}")
        print(f"Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        if entry.notes:
            print("Notes:")
            for line in entry.notes.splitlines():
                print(f"  {line}")
        
        show_password = input("\nShow password? (y/N): ").lower() == 'y'
        if show_password:
            print(f"Password: {entry.password}")
        
        input("\nPress Enter to continue...")
    
    def search_passwords(self):
        """Enhanced search for password entries"""
        print("\n🔍 SEARCH PASSWORDS")
        print("-" * 30)
        print("💡 Tips:")
        print("  • Use multiple words to narrow results (e.g., 'google work')")
        print("  • Search works across username, website, and notes")
        print("  • Results are sorted by relevance")
        print()
        
        query = input("Enter search terms: ").strip()
        if not query:
            print("❌ Search term cannot be empty.")
            return
        
        results = self.password_manager.search_entries(query)
        
        if not results:
            print(f"❌ No passwords found matching '{query}'.")
            
            # Suggest similar websites
            suggestions = self.password_manager.get_website_suggestions(query)
            if suggestions:
                print(f"💡 Did you mean one of these websites?")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"   {i}. {suggestion}")
            return
        
        print(f"\n📋 SEARCH RESULTS ({len(results)} found for '{query}')")
        print("-" * 50)
        
        # Show summary list first
        for i, entry in enumerate(results, 1):
            print(f"{i}. {entry.username} - {entry.website or 'N/A'} - {entry.created_at.strftime('%Y-%m-%d')}")
        
        while True:
            print(f"\nOptions:")
            print(f"• Enter number (1-{len(results)}) to view details")
            print(f"• [m]ain menu")
            
            choice = input("\nChoose: ").lower().strip()
            
            if choice == 'm':
                break
            
            try:
                entry_num = int(choice)
                if 1 <= entry_num <= len(results):
                    entry = results[entry_num - 1]
                    self.view_single_entry(entry)
                else:
                    print("❌ Invalid entry number.")
            except ValueError:
                print("❌ Invalid option. Please try again.")
    
    def advanced_search(self):
        """Advanced search with multiple criteria"""
        print("\n🔎 ADVANCED SEARCH")
        print("-" * 30)
        print("Enter search criteria (leave blank to skip):")
        print()
        
        criteria = {}
        
        username = input("Username contains: ").strip()
        if username:
            criteria['username'] = username
        
        website = input("Website contains: ").strip()
        if website:
            criteria['website'] = website
        
        notes = input("Notes contain: ").strip()
        if notes:
            criteria['notes'] = notes
        
        # Date range search
        print("\nDate range (optional):")
        created_after = input("Created after (YYYY-MM-DD): ").strip()
        if created_after:
            try:
                criteria['created_after'] = datetime.strptime(created_after, '%Y-%m-%d')
            except ValueError:
                print("❌ Invalid date format. Skipping date filter.")
        
        created_before = input("Created before (YYYY-MM-DD): ").strip()
        if created_before:
            try:
                criteria['created_before'] = datetime.strptime(created_before, '%Y-%m-%d')
            except ValueError:
                print("❌ Invalid date format. Skipping date filter.")
        
        if not criteria:
            print("❌ No search criteria provided.")
            return
        
        results = self.password_manager.advanced_search(**criteria)
        
        if not results:
            print("❌ No passwords found matching the criteria.")
            return
        
        print(f"\n📋 ADVANCED SEARCH RESULTS ({len(results)} found)")
        print("-" * 50)
        
        # Show summary list first
        for i, entry in enumerate(results, 1):
            print(f"{i}. {entry.username} - {entry.website or 'N/A'} - {entry.created_at.strftime('%Y-%m-%d')}")
        
        while True:
            print(f"\nOptions:")
            print(f"• Enter number (1-{len(results)}) to view details")
            print(f"• [m]ain menu")
            
            choice = input("\nChoose: ").lower().strip()
            
            if choice == 'm':
                break
            
            try:
                entry_num = int(choice)
                if 1 <= entry_num <= len(results):
                    entry = results[entry_num - 1]
                    self.view_single_entry(entry)
                else:
                    print("❌ Invalid entry number.")
            except ValueError:
                print("❌ Invalid option. Please try again.")
    
    def edit_password(self):
        """Edit an existing password entry"""
        print("\n✏️  EDIT PASSWORD")
        print("-" * 30)
        
        # Allow search before editing
        search_query = input("Search for password to edit (or press Enter to browse all): ").strip()
        
        if search_query:
            entries = self.password_manager.search_entries(search_query)
            if not entries:
                print("❌ No passwords found matching your search.")
                return
        else:
            entries = self.password_manager.get_all_entries()
            if not entries:
                print("❌ No passwords stored yet.")
                return
        
        print(f"\nFound {len(entries)} password(s):")
        for i, entry in enumerate(entries[:10], 1):  # Show first 10
            print(f"{i}. {entry.username} - {entry.website or 'No website'} (ID: {entry.id[:8]}...)")
        
        if len(entries) > 10:
            print(f"... and {len(entries) - 10} more. Use search to narrow results.")
        
        try:
            choice = int(input(f"\nSelect password to edit (1-{min(len(entries), 10)}): "))
            if 1 <= choice <= min(len(entries), 10):
                entry = entries[choice - 1]
            else:
                print("❌ Invalid selection.")
                return
        except ValueError:
            print("❌ Invalid input.")
            return
        
        print(f"\nEditing entry for: {entry.username}")
        print("(Press Enter to keep current value)")
        
        new_username = input(f"Username [{entry.username}]: ").strip()
        new_password = getpass.getpass(f"Password [current hidden]: ")
        new_website = input(f"Website [{entry.website}]: ").strip()
        
        print(f"\nCurrent Notes:\n{entry.notes if entry.notes else '(None)'}")
        print("\nNotes [Press Enter to keep current, or enter new notes. Type 'END' on a new line when finished]:")
        new_notes = self.get_multiline_input(allow_keep=True, current_value=entry.notes)
        
        # Update only non-empty fields
        updates = {}
        if new_username:
            updates['username'] = new_username
        if new_password:
            updates['password'] = new_password
        if new_website:
            updates['website'] = new_website
        if new_notes != entry.notes:
            updates['notes'] = new_notes
        
        if updates:
            if self.password_manager.update_entry(entry.id, **updates):
                print("✅ Password updated successfully!")
            else:
                print("❌ Failed to update password.")
        else:
            print("ℹ️  No changes made.")
    
    def delete_password(self):
        """Delete a password entry"""
        print("\n🗑️  DELETE PASSWORD")
        print("-" * 30)
        
        # Allow search before deleting
        search_query = input("Search for password to delete (or press Enter to browse all): ").strip()
        
        if search_query:
            entries = self.password_manager.search_entries(search_query)
            if not entries:
                print("❌ No passwords found matching your search.")
                return
        else:
            entries = self.password_manager.get_all_entries()
            if not entries:
                print("❌ No passwords stored yet.")
                return
        
        print(f"\nFound {len(entries)} password(s):")
        for i, entry in enumerate(entries[:10], 1):  # Show first 10
            print(f"{i}. {entry.username} - {entry.website or 'No website'} (ID: {entry.id[:8]}...)")
        
        if len(entries) > 10:
            print(f"... and {len(entries) - 10} more. Use search to narrow results.")
        
        try:
            choice = int(input(f"\nSelect password to delete (1-{min(len(entries), 10)}): "))
            if 1 <= choice <= min(len(entries), 10):
                entry = entries[choice - 1]
            else:
                print("❌ Invalid selection.")
                return
        except ValueError:
            print("❌ Invalid input.")
            return
        
        print(f"\n⚠️  You are about to delete:")
        print(f"Username: {entry.username}")
        print(f"Website: {entry.website or 'N/A'}")
        
        confirm = input("\nAre you sure? Type 'DELETE' to confirm: ")
        if confirm == 'DELETE':
            if self.password_manager.delete_entry(entry.id):
                print("✅ Password deleted successfully!")
            else:
                print("❌ Failed to delete password.")
        else:
            print("ℹ️  Deletion cancelled.")
    
    def generate_password_menu(self):
        """Password generation menu"""
        print("\n🎲 PASSWORD GENERATOR")
        print("-" * 30)
        print("1. Quick generate (default settings)")
        print("2. Custom generate")
        print("3. Memorable password")
        print()
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == '1':
            try:
                password = PasswordGenerator.generate()
                self.display_generated_password(password)
            except Exception as e:
                print(f"❌ Error generating password: {e}")
        elif choice == '2':
            try:
                password = self.generate_password_interactive()
                if password:
                    self.display_generated_password(password)
            except Exception as e:
                print(f"❌ Error generating password: {e}")
        elif choice == '3':
            try:
                password = PasswordGenerator.generate_memorable_password()
                self.display_generated_password(password)
            except Exception as e:
                print(f"❌ Error generating memorable password: {e}")
        else:
            print("❌ Invalid option.")
    
    def generate_password_interactive(self) -> Optional[str]:
        """Interactive password generation with custom options"""
        print("\n🔧 CUSTOM PASSWORD GENERATION")
        print("-" * 40)
        
        try:
            length = int(input("Password length (8-64) [16]: ") or "16")
            if length < 8 or length > 64:
                print("❌ Length must be between 8 and 64.")
                return None
        except ValueError:
            print("❌ Invalid length.")
            return None
        
        include_uppercase = input("Include uppercase letters? (Y/n): ").lower() != 'n'
        include_lowercase = input("Include lowercase letters? (Y/n): ").lower() != 'n'
        include_numbers = input("Include numbers? (Y/n): ").lower() != 'n'
        include_symbols = input("Include symbols? (Y/n): ").lower() != 'n'
        exclude_similar = input("Exclude similar characters (i,l,1,L,o,0,O)? (y/N): ").lower() == 'y'
        
        try:
            password = PasswordGenerator.generate(
                length=length,
                include_uppercase=include_uppercase,
                include_lowercase=include_lowercase,
                include_numbers=include_numbers,
                include_symbols=include_symbols,
                exclude_similar=exclude_similar
            )
            return password
        except ValueError as e:
            print(f"❌ {e}")
            return None
    
    def display_generated_password(self, password: str):
        """Display generated password with strength analysis"""
        try:
            print(f"\n🔑 Generated Password: {password}")
            
            strength = PasswordGenerator.calculate_strength(password)
            print(f"💪 Strength: {strength['strength']} ({strength['score']}/{strength['max_score']})")
            
            # Safely handle feedback list
            if 'feedback' in strength and strength['feedback'] and len(strength['feedback']) > 0:
                print("💡 Suggestions:")
                for suggestion in strength['feedback']:
                    print(f"   • {suggestion}")
            
            print(f"\n📋 Password copied to display. Length: {len(password)} characters")
            
            save_choice = input("\nSave this password to vault? (y/N): ").lower()
            if save_choice == 'y':
                username = input("Username/Email: ").strip()
                if username:
                    website = input("Website (optional): ").strip()
                    print("Notes (optional - multi-line supported. Type 'END' on a new line when finished):")
                    notes = self.get_multiline_input()
                    entry = self.password_manager.add_entry(username, password, website, notes)
                    print(f"✅ Password saved! (ID: {entry.id[:8]}...)")
        except Exception as e:
            print(f"❌ Error displaying password: {e}")
    
    def settings_menu(self):
        """Settings and utilities menu"""
        print("\n🔧 SETTINGS")
        print("-" * 30)
        print("1. 📊 View statistics")
        print("2. 🔍 Password strength audit")
        print("3. 💾 Create backup")
        print("4. 🔄 Change master password")
        print("5. 🧹 Clear all data")
        print()
        
        choice = input("Choose option (1-5): ").strip()
        
        if choice == '1':
            self.show_statistics()
        elif choice == '2':
            self.password_audit()
        elif choice == '3':
            self.create_backup()
        elif choice == '4':
            self.change_master_password()
        elif choice == '5':
            self.clear_all_data()
        else:
            print("❌ Invalid option.")
    
    def show_statistics(self):
        """Show password vault statistics"""
        entries = self.password_manager.get_all_entries()
        
        print("\n📊 VAULT STATISTICS")
        print("-" * 30)
        print(f"Total passwords: {len(entries)}")
        
        if entries:
            # Password strength distribution
            strength_counts = {'Very Weak': 0, 'Weak': 0, 'Fair': 0, 'Good': 0, 'Strong': 0, 'Very Strong': 0, 'Excellent': 0}
            
            for entry in entries:
                strength = PasswordGenerator.calculate_strength(entry.password)
                strength_counts[strength['strength']] += 1
            
            print("\nPassword strength distribution:")
            for strength, count in strength_counts.items():
                if count > 0:
                    print(f"  {strength}: {count}")
            
            # Average password length
            avg_length = sum(len(entry.password) for entry in entries) / len(entries)
            print(f"\nAverage password length: {avg_length:.1f} characters")
            
            # Websites with passwords
            websites = set(entry.website for entry in entries if entry.website)
            print(f"Unique websites: {len(websites)}")
            
            # Most common websites
            if websites:
                website_counts = {}
                for entry in entries:
                    if entry.website:
                        website_counts[entry.website] = website_counts.get(entry.website, 0) + 1
                
                print("\nMost used websites:")
                sorted_websites = sorted(website_counts.items(), key=lambda x: x[1], reverse=True)
                for website, count in sorted_websites[:5]:
                    print(f"  {website}: {count} password(s)")
    
    def password_audit(self):
        """Audit password strength and security"""
        entries = self.password_manager.get_all_entries()
        
        if not entries:
            print("\n❌ No passwords to audit.")
            return
        
        print("\n🔍 PASSWORD SECURITY AUDIT")
        print("-" * 40)
        
        weak_passwords = []
        duplicate_passwords = {}
        
        for entry in entries:
            strength = PasswordGenerator.calculate_strength(entry.password)
            
            # Check for weak passwords
            if strength['score'] < 4:
                weak_passwords.append((entry, strength))
            
            # Check for duplicates
            if entry.password in duplicate_passwords:
                duplicate_passwords[entry.password].append(entry)
            else:
                duplicate_passwords[entry.password] = [entry]
        
        # Report weak passwords
        if weak_passwords:
            print(f"\n⚠️  WEAK PASSWORDS ({len(weak_passwords)} found):")
            for entry, strength in weak_passwords:
                print(f"  • {entry.username} ({entry.website or 'No website'}) - {strength['strength']}")
        
        # Report duplicate passwords
        duplicates = {pwd: entries for pwd, entries in duplicate_passwords.items() if len(entries) > 1}
        if duplicates:
            print(f"\n🔄 DUPLICATE PASSWORDS ({len(duplicates)} found):")
            for password, entries in duplicates.items():
                usernames = [f"{entry.username} ({entry.website or 'No website'})" for entry in entries]
                print(f"  • Used by: {', '.join(usernames)}")
        
        if not weak_passwords and not duplicates:
            print("\n✅ All passwords are strong and unique!")
    
    def create_backup(self):
        """Create a backup of the encrypted data"""
        filename = input("Backup filename [backup.json]: ").strip()
        if not filename:
            filename = "backup.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        if self.storage_manager.backup_data(filename):
            print(f"✅ Backup created successfully: {filename}")
            print("⚠️  This backup contains encrypted data and requires your master password to restore.")
        else:
            print("❌ Failed to create backup.")
    
    def change_master_password(self):
        """Change the master password"""
        print("\n🔄 CHANGE MASTER PASSWORD")
        print("-" * 40)
        print("⚠️  This will re-encrypt all your data with the new password.")
        
        # Verify current password
        current_password = getpass.getpass("Enter current master password: ")
        if not self.storage_manager.verify_master_password(current_password):
            print("❌ Invalid current password.")
            return
        
        # Get new password
        while True:
            new_password = getpass.getpass("Enter new master password: ")
            if len(new_password) < 8:
                print("❌ Password must be at least 8 characters long.")
                continue
            
            confirm_password = getpass.getpass("Confirm new master password: ")
            if new_password != confirm_password:
                print("❌ Passwords do not match.")
                continue
            
            break
        
        # Re-encrypt data with new password
        try:
            # Load data with old password
            entries = self.password_manager.get_all_entries()
            
            # Save new master password
            if not self.storage_manager.save_master_password(new_password):
                print("❌ Failed to save new master password.")
                return
            
            # Re-encrypt and save data
            password_dicts = [entry.to_dict() for entry in entries]
            if self.storage_manager.save_passwords(password_dicts, new_password):
                self.password_manager.master_password = new_password
                print("✅ Master password changed successfully!")
            else:
                print("❌ Failed to re-encrypt data.")
        except Exception as e:
            print(f"❌ Error changing master password: {e}")
    
    def clear_all_data(self):
        """Clear all stored data"""
        print("\n🧹 CLEAR ALL DATA")
        print("-" * 30)
        print("⚠️  This will permanently delete ALL your passwords!")
        print("This action cannot be undone.")
        
        confirm1 = input("\nType 'DELETE ALL' to confirm: ")
        if confirm1 != 'DELETE ALL':
            print("ℹ️  Operation cancelled.")
            return
        
        confirm2 = input("Are you absolutely sure? Type 'YES' to proceed: ")
        if confirm2 != 'YES':
            print("ℹ️  Operation cancelled.")
            return
        
        try:
            # Remove data files
            if os.path.exists(self.storage_manager.data_file):
                os.remove(self.storage_manager.data_file)
            if os.path.exists(self.storage_manager.master_file):
                os.remove(self.storage_manager.master_file)
            
            print("✅ All data cleared successfully!")
            print("👋 Please restart the application to set up a new master password.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error clearing data: {e}")