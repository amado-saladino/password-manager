"""
Password generation utilities with customizable options
"""

import random
import string
import re


class PasswordGenerator:
    """Generates secure passwords with various options"""
    
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    NUMBERS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    SIMILAR_CHARS = "il1Lo0O"
    
    @staticmethod
    def generate(length=16, include_uppercase=True, include_lowercase=True,
                include_numbers=True, include_symbols=True, exclude_similar=False):
        """Generate a password with specified criteria"""
        
        if length < 4:
            raise ValueError("Password length must be at least 4 characters")
        
        character_set = ""
        required_chars = []
        
        if include_uppercase:
            character_set += PasswordGenerator.UPPERCASE
            required_chars.append(random.choice(PasswordGenerator.UPPERCASE))
        
        if include_lowercase:
            character_set += PasswordGenerator.LOWERCASE
            required_chars.append(random.choice(PasswordGenerator.LOWERCASE))
        
        if include_numbers:
            character_set += PasswordGenerator.NUMBERS
            required_chars.append(random.choice(PasswordGenerator.NUMBERS))
        
        if include_symbols:
            character_set += PasswordGenerator.SYMBOLS
            required_chars.append(random.choice(PasswordGenerator.SYMBOLS))
        
        if not character_set:
            raise ValueError("At least one character type must be selected")
        
        if exclude_similar:
            character_set = ''.join(char for char in character_set 
                                  if char not in PasswordGenerator.SIMILAR_CHARS)
            required_chars = [char for char in required_chars 
                            if char not in PasswordGenerator.SIMILAR_CHARS]
        
        # Generate remaining characters
        remaining_length = length - len(required_chars)
        if remaining_length > 0:
            additional_chars = [random.choice(character_set) for _ in range(remaining_length)]
            password_chars = required_chars + additional_chars
        else:
            password_chars = required_chars[:length]
        
        # Shuffle the password
        random.shuffle(password_chars)
        return ''.join(password_chars)
    
    @staticmethod
    def calculate_strength(password):
        """Calculate password strength and return score with description"""
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Use at least 8 characters")
        
        if len(password) >= 12:
            score += 1
        
        if len(password) >= 16:
            score += 1
        
        # Character diversity
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Include lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Include uppercase letters")
        
        if re.search(r'[0-9]', password):
            score += 1
        else:
            feedback.append("Include numbers")
        
        if re.search(r'[^a-zA-Z0-9]', password):
            score += 1
        else:
            feedback.append("Include special characters")
        
        # Pattern detection (deduct points)
        if re.search(r'(.)\1{2,}', password):
            score -= 1
            feedback.append("Avoid repeated characters")
        
        if re.search(r'123|abc|qwe|password', password.lower()):
            score -= 1
            feedback.append("Avoid common patterns")
        
        score = max(0, min(7, score))
        
        # strength_levels = [
        #     "Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong", "Excellent"
        # ]
        strength_levels = {
            1: "Very Weak",
            2: "Weak",
            3: "Fair",
            4: "Good",
            5: "Strong",
            6: "Very Strong",
            7: "Excellent"
        }
        
        
        return {
            'score': score,
            'max_score': 7,
            'strength': strength_levels[score],
            'feedback': feedback
        }
    
    @staticmethod
    def generate_memorable_password(num_words=4, separator='-', include_numbers=True):
        """Generate a memorable password using word combinations"""
        # Simple word list for memorable passwords
        words = [
            'apple', 'brave', 'cloud', 'dance', 'eagle', 'flame', 'grace', 'happy',
            'island', 'jungle', 'knight', 'light', 'magic', 'noble', 'ocean', 'peace',
            'quiet', 'river', 'storm', 'tiger', 'unity', 'voice', 'water', 'youth'
        ]
        
        selected_words = random.sample(words, num_words)
        
        # Capitalize first letter of each word
        selected_words = [word.capitalize() for word in selected_words]
        
        if include_numbers:
            selected_words.append(str(random.randint(10, 99)))
        
        return separator.join(selected_words)