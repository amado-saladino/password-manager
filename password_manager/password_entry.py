"""
Password entry data model and operations
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, List
import re


class PasswordEntry:
    """Represents a single password entry"""
    
    def __init__(self, username: str, password: str, website: str = "", 
                 notes: str = "", entry_id: str = None):
        self.id = entry_id or str(uuid.uuid4())
        self.username = username
        self.password = password
        self.website = website
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary for storage"""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'website': self.website,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PasswordEntry':
        """Create entry from dictionary"""
        entry = cls(
            username=data.get('username', ''),
            password=data.get('password', ''),
            website=data.get('website', ''),
            notes=data.get('notes', ''),
            entry_id=data.get('id')
        )
        
        # Parse timestamps if available
        if 'created_at' in data:
            try:
                entry.created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        if 'updated_at' in data:
            try:
                entry.updated_at = datetime.fromisoformat(data['updated_at'])
            except:
                pass
        
        return entry
    
    def update(self, username: str = None, password: str = None, 
               website: str = None, notes: str = None):
        """Update entry fields"""
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if website is not None:
            self.website = website
        if notes is not None:
            self.notes = notes
        
        self.updated_at = datetime.now()
    
    def matches_search(self, query: str) -> bool:
        """Check if entry matches search query"""
        query = query.lower()
        return (query in self.username.lower() or 
                query in self.website.lower() or 
                query in self.notes.lower())
    
    def __str__(self) -> str:
        """String representation of the entry"""
        return f"PasswordEntry(username='{self.username}', website='{self.website}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class PasswordManager:
    """Manages password entries and operations"""
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.entries = []
        self.master_password = None
    
    def authenticate(self, master_password: str) -> bool:
        """Authenticate with master password"""
        if self.storage_manager.verify_master_password(master_password):
            self.master_password = master_password
            self.load_entries()
            return True
        return False
    
    def setup_master_password(self, master_password: str) -> bool:
        """Set up initial master password"""
        if self.storage_manager.save_master_password(master_password):
            self.master_password = master_password
            return True
        return False
    
    def load_entries(self):
        """Load password entries from storage"""
        if not self.master_password:
            return
        
        password_dicts = self.storage_manager.load_passwords(self.master_password)
        self.entries = [PasswordEntry.from_dict(data) for data in password_dicts]
    
    def save_entries(self) -> bool:
        """Save password entries to storage"""
        if not self.master_password:
            return False
        
        password_dicts = [entry.to_dict() for entry in self.entries]
        return self.storage_manager.save_passwords(password_dicts, self.master_password)
    
    def add_entry(self, username: str, password: str, website: str = "", notes: str = "") -> PasswordEntry:
        """Add a new password entry"""
        entry = PasswordEntry(username, password, website, notes)
        self.entries.append(entry)
        self.save_entries()
        return entry
    
    def get_entry_by_id(self, entry_id: str) -> Optional[PasswordEntry]:
        """Get entry by ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def get_entries_by_username(self, username: str) -> list:
        """Get entries by username (partial match)"""
        return [entry for entry in self.entries 
                if username.lower() in entry.username.lower()]
    
    def get_entries_by_website(self, website: str) -> list:
        """Get entries by website (partial match)"""
        return [entry for entry in self.entries 
                if website.lower() in entry.website.lower()]
    
    def search_entries(self, query: str) -> list:
        """Search entries by username, website, or notes with enhanced functionality"""
        if not query.strip():
            return []
        
        # Split query into tokens for multi-term search
        tokens = [token.strip().lower() for token in query.split() if token.strip()]
        
        results = []
        for entry in self.entries:
            # Check if all tokens match somewhere in the entry
            entry_text = f"{entry.username} {entry.website} {entry.notes}".lower()
            
            if all(token in entry_text for token in tokens):
                results.append(entry)
        
        # Sort results by relevance (exact matches first, then partial)
        def relevance_score(entry):
            score = 0
            entry_text = f"{entry.username} {entry.website} {entry.notes}".lower()
            
            # Exact website match gets highest score
            if query.lower() == entry.website.lower():
                score += 100
            
            # Exact username match gets high score
            if query.lower() == entry.username.lower():
                score += 80
            
            # Website contains query gets medium score
            if query.lower() in entry.website.lower():
                score += 50
            
            # Username contains query gets medium score
            if query.lower() in entry.username.lower():
                score += 40
            
            # Notes contain query gets lower score
            if query.lower() in entry.notes.lower():
                score += 20
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)
    
    def advanced_search(self, **criteria) -> list:
        """Advanced search with specific criteria"""
        results = self.entries.copy()
        
        if 'username' in criteria and criteria['username']:
            username_query = criteria['username'].lower()
            results = [e for e in results if username_query in e.username.lower()]
        
        if 'website' in criteria and criteria['website']:
            website_query = criteria['website'].lower()
            results = [e for e in results if website_query in e.website.lower()]
        
        if 'notes' in criteria and criteria['notes']:
            notes_query = criteria['notes'].lower()
            results = [e for e in results if notes_query in e.notes.lower()]
        
        if 'created_after' in criteria and criteria['created_after']:
            results = [e for e in results if e.created_at >= criteria['created_after']]
        
        if 'created_before' in criteria and criteria['created_before']:
            results = [e for e in results if e.created_at <= criteria['created_before']]
        
        return results
    
    def get_website_suggestions(self, partial_website: str) -> List[str]:
        """Get website suggestions based on partial input"""
        if not partial_website:
            return []
        
        partial = partial_website.lower()
        websites = set()
        
        for entry in self.entries:
            if entry.website and partial in entry.website.lower():
                websites.add(entry.website)
        
        return sorted(list(websites))
    
    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """Update an existing entry"""
        entry = self.get_entry_by_id(entry_id)
        if entry:
            entry.update(**kwargs)
            self.save_entries()
            return True
        return False
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry"""
        entry = self.get_entry_by_id(entry_id)
        if entry:
            self.entries.remove(entry)
            self.save_entries()
            return True
        return False
    
    def get_all_entries(self) -> list:
        """Get all password entries"""
        return self.entries.copy()