"""
SQLite Database Models for Steganography Application

This module provides database models and utilities for:
- User authentication and management
- Operation history tracking
- Session management

Compatible with PythonAnywhere deployment.
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import json

# Database configuration - use instance folder for PythonAnywhere compatibility
DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'steganography.db')

# Ensure database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with all required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                profile_picture TEXT,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Sessions table (for JWT refresh tokens)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                refresh_token TEXT UNIQUE NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_valid BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Operation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                operation_type TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                input_preview TEXT,
                output_preview TEXT,
                is_encrypted BOOLEAN DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(refresh_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON operation_history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created ON operation_history(created_at)')
        
        conn.commit()


# ============================================================================
# Password Hashing Utilities
# ============================================================================

def generate_salt() -> str:
    """Generate a cryptographically secure salt."""
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    """Hash password using PBKDF2 with SHA-256."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations for security
    ).hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Verify password against stored hash."""
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


# ============================================================================
# User Management
# ============================================================================

class UserManager:
    """Handles all user-related database operations."""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 30
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format and requirements."""
        if not username:
            return False, "Username is required"
        if len(username) < UserManager.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {UserManager.MIN_USERNAME_LENGTH} characters"
        if len(username) > UserManager.MAX_USERNAME_LENGTH:
            return False, f"Username cannot exceed {UserManager.MAX_USERNAME_LENGTH} characters"
        if not username.isalnum() and '_' not in username:
            return False, "Username can only contain letters, numbers, and underscores"
        if username[0].isdigit():
            return False, "Username cannot start with a number"
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format."""
        if not email:
            return False, "Email is required"
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        if len(email) > 255:
            return False, "Email is too long"
        # Basic email format check
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return False, "Invalid email format"
        if '.' not in parts[1] or parts[1].startswith('.') or parts[1].endswith('.'):
            return False, "Invalid email domain"
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if not password:
            return False, "Password is required"
        if len(password) < UserManager.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {UserManager.MIN_PASSWORD_LENGTH} characters"
        if len(password) > UserManager.MAX_PASSWORD_LENGTH:
            return False, f"Password cannot exceed {UserManager.MAX_PASSWORD_LENGTH} characters"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not has_upper:
            return False, "Password must contain at least one uppercase letter"
        if not has_lower:
            return False, "Password must contain at least one lowercase letter"
        if not has_digit:
            return False, "Password must contain at least one number"
        if not has_special:
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        return True, ""
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> tuple[bool, str, Optional[int]]:
        """
        Create a new user account.
        
        Returns:
            tuple: (success, message, user_id or None)
        """
        # Validate inputs
        valid, msg = UserManager.validate_username(username)
        if not valid:
            return False, msg, None
        
        valid, msg = UserManager.validate_email(email)
        if not valid:
            return False, msg, None
        
        valid, msg = UserManager.validate_password(password)
        if not valid:
            return False, msg, None
        
        # Check for existing user
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                         (username.lower(), email.lower()))
            if cursor.fetchone():
                return False, "Username or email already exists", None
            
            # Create user
            salt = generate_salt()
            password_hash = hash_password(password, salt)
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, salt)
                    VALUES (?, ?, ?, ?)
                ''', (username.lower(), email.lower(), password_hash, salt))
                conn.commit()
                return True, "Account created successfully", cursor.lastrowid
            except sqlite3.IntegrityError:
                return False, "Username or email already exists", None
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Authenticate a user.
        
        Returns:
            tuple: (success, message, user_data or None)
        """
        if not username_or_email or not password:
            return False, "Username/email and password are required", None
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Find user
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, is_active, 
                       failed_login_attempts, locked_until
                FROM users 
                WHERE username = ? OR email = ?
            ''', (username_or_email.lower(), username_or_email.lower()))
            
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid username/email or password", None
            
            # Check if account is active
            if not user['is_active']:
                return False, "Account is deactivated. Please contact support.", None
            
            # Check if account is locked
            if user['locked_until']:
                locked_until = datetime.fromisoformat(user['locked_until'])
                if locked_until > datetime.utcnow():
                    remaining = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
                    return False, f"Account is locked. Try again in {remaining} minutes.", None
                else:
                    # Unlock account
                    cursor.execute('''
                        UPDATE users SET locked_until = NULL, failed_login_attempts = 0
                        WHERE id = ?
                    ''', (user['id'],))
            
            # Verify password
            if not verify_password(password, user['salt'], user['password_hash']):
                # Increment failed attempts
                new_attempts = user['failed_login_attempts'] + 1
                
                if new_attempts >= UserManager.MAX_FAILED_ATTEMPTS:
                    lock_until = datetime.utcnow() + timedelta(minutes=UserManager.LOCKOUT_DURATION_MINUTES)
                    cursor.execute('''
                        UPDATE users SET failed_login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (new_attempts, lock_until.isoformat(), user['id']))
                    conn.commit()
                    return False, f"Too many failed attempts. Account locked for {UserManager.LOCKOUT_DURATION_MINUTES} minutes.", None
                else:
                    cursor.execute('''
                        UPDATE users SET failed_login_attempts = ?
                        WHERE id = ?
                    ''', (new_attempts, user['id']))
                    conn.commit()
                    remaining = UserManager.MAX_FAILED_ATTEMPTS - new_attempts
                    return False, f"Invalid password. {remaining} attempts remaining.", None
            
            # Successful login - reset failed attempts and update last login
            cursor.execute('''
                UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), user['id']))
            conn.commit()
            
            return True, "Login successful", {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, created_at, last_login, is_active, settings
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
    
    @staticmethod
    def update_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
        """Update user password."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current password info
            cursor.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            # Verify current password
            if not verify_password(current_password, user['salt'], user['password_hash']):
                return False, "Current password is incorrect"
            
            # Validate new password
            valid, msg = UserManager.validate_password(new_password)
            if not valid:
                return False, msg
            
            # Update password
            new_salt = generate_salt()
            new_hash = hash_password(new_password, new_salt)
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
            ''', (new_hash, new_salt, user_id))
            conn.commit()
            
            return True, "Password updated successfully"
    
    @staticmethod
    def delete_user(user_id: int, password: str) -> tuple[bool, str]:
        """Delete user account (requires password confirmation)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            if not verify_password(password, user['salt'], user['password_hash']):
                return False, "Password is incorrect"
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            
            return True, "Account deleted successfully"


# ============================================================================
# Session Management
# ============================================================================

class SessionManager:
    """Handles session/refresh token management."""
    
    REFRESH_TOKEN_EXPIRY_DAYS = 30
    
    @staticmethod
    def create_session(user_id: int, device_info: str = None, ip_address: str = None) -> str:
        """Create a new session and return refresh token."""
        refresh_token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=SessionManager.REFRESH_TOKEN_EXPIRY_DAYS)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (user_id, refresh_token, device_info, ip_address, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, refresh_token, device_info, ip_address, expires_at.isoformat()))
            conn.commit()
        
        return refresh_token
    
    @staticmethod
    def validate_session(refresh_token: str) -> Optional[int]:
        """Validate refresh token and return user_id if valid."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, expires_at, is_valid
                FROM sessions WHERE refresh_token = ?
            ''', (refresh_token,))
            
            session = cursor.fetchone()
            
            if not session:
                return None
            
            if not session['is_valid']:
                return None
            
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < datetime.utcnow():
                # Invalidate expired session
                cursor.execute('UPDATE sessions SET is_valid = 0 WHERE refresh_token = ?', (refresh_token,))
                conn.commit()
                return None
            
            return session['user_id']
    
    @staticmethod
    def invalidate_session(refresh_token: str) -> bool:
        """Invalidate a specific session (logout)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_valid = 0 WHERE refresh_token = ?', (refresh_token,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def invalidate_all_user_sessions(user_id: int) -> int:
        """Invalidate all sessions for a user (logout everywhere)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_valid = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def get_user_sessions(user_id: int) -> List[Dict]:
        """Get all active sessions for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, device_info, ip_address, created_at, expires_at
                FROM sessions 
                WHERE user_id = ? AND is_valid = 1 AND expires_at > ?
                ORDER BY created_at DESC
            ''', (user_id, datetime.utcnow().isoformat()))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove expired sessions from database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM sessions WHERE expires_at < ? OR is_valid = 0
            ''', (datetime.utcnow().isoformat(),))
            conn.commit()
            return cursor.rowcount


# ============================================================================
# Operation History
# ============================================================================

class HistoryManager:
    """Handles operation history tracking."""
    
    MAX_PREVIEW_LENGTH = 100
    MAX_HISTORY_ITEMS = 100  # Per user
    
    @staticmethod
    def add_operation(
        user_id: int,
        operation_type: str,  # 'encode' or 'decode'
        algorithm: str,       # 'zwc' or 'lsb'
        input_data: str = None,
        output_data: str = None,
        is_encrypted: bool = False,
        metadata: Dict = None
    ) -> int:
        """Add an operation to history."""
        # Truncate previews
        input_preview = (input_data[:HistoryManager.MAX_PREVIEW_LENGTH] + '...') if input_data and len(input_data) > HistoryManager.MAX_PREVIEW_LENGTH else input_data
        output_preview = (output_data[:HistoryManager.MAX_PREVIEW_LENGTH] + '...') if output_data and len(output_data) > HistoryManager.MAX_PREVIEW_LENGTH else output_data
        
        # For images, just store a note
        if algorithm == 'lsb':
            input_preview = '[Image Data]'
            output_preview = '[Image Data]'
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO operation_history 
                (user_id, operation_type, algorithm, input_preview, output_preview, is_encrypted, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                operation_type, 
                algorithm, 
                input_preview, 
                output_preview, 
                is_encrypted,
                json.dumps(metadata) if metadata else None
            ))
            
            # Cleanup old entries if over limit
            cursor.execute('''
                DELETE FROM operation_history 
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM operation_history 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                )
            ''', (user_id, user_id, HistoryManager.MAX_HISTORY_ITEMS))
            
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_user_history(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get operation history for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, operation_type, algorithm, input_preview, output_preview, 
                       is_encrypted, metadata, created_at
                FROM operation_history 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            results = []
            for row in cursor.fetchall():
                item = dict(row)
                if item['metadata']:
                    item['metadata'] = json.loads(item['metadata'])
                results.append(item)
            
            return results
    
    @staticmethod
    def get_history_count(user_id: int) -> int:
        """Get total history count for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM operation_history WHERE user_id = ?', (user_id,))
            return cursor.fetchone()[0]
    
    @staticmethod
    def delete_history_item(user_id: int, history_id: int) -> bool:
        """Delete a specific history item."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM operation_history WHERE id = ? AND user_id = ?
            ''', (history_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def clear_user_history(user_id: int) -> int:
        """Clear all history for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM operation_history WHERE user_id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict:
        """Get statistics for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total operations
            cursor.execute('SELECT COUNT(*) FROM operation_history WHERE user_id = ?', (user_id,))
            total = cursor.fetchone()[0]
            
            # By type
            cursor.execute('''
                SELECT operation_type, COUNT(*) as count 
                FROM operation_history WHERE user_id = ?
                GROUP BY operation_type
            ''', (user_id,))
            by_type = {row['operation_type']: row['count'] for row in cursor.fetchall()}
            
            # By algorithm
            cursor.execute('''
                SELECT algorithm, COUNT(*) as count 
                FROM operation_history WHERE user_id = ?
                GROUP BY algorithm
            ''', (user_id,))
            by_algorithm = {row['algorithm']: row['count'] for row in cursor.fetchall()}
            
            # Encrypted count
            cursor.execute('''
                SELECT COUNT(*) FROM operation_history 
                WHERE user_id = ? AND is_encrypted = 1
            ''', (user_id,))
            encrypted = cursor.fetchone()[0]
            
            return {
                'total_operations': total,
                'encodes': by_type.get('encode', 0),
                'decodes': by_type.get('decode', 0),
                'text_operations': by_algorithm.get('zwc', 0),
                'image_operations': by_algorithm.get('lsb', 0),
                'encrypted_operations': encrypted
            }


# Initialize database on module import
init_database()
