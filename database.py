"""
==============================================================================
DATABASE MODULE FOR STEGANOGRAPHY APPLICATION
==============================================================================

This module handles all database operations using SQLite. It provides
models and utilities for managing users, sessions, and operation history.

Main Features:
    - User management (create, authenticate, update, delete)
    - Session management for refresh tokens
    - Operation history tracking for logged in users
    - Password hashing with PBKDF2 and salt

Database Tables:
    - users: Store user accounts and credentials
    - sessions: Store refresh tokens and session info
    - operation_history: Track encoding/decoding operations
    - password_reset_tokens: For password recovery

Compatible with PythonAnywhere deployment.
==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import json


# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

# Database files are stored in the instance folder
# This keeps them separate from code and is standard Flask practice
DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'steganography.db')

# Make sure the database folder exists
os.makedirs(DATABASE_DIR, exist_ok=True)


# ==============================================================================
# DATABASE CONNECTION HELPER
# ==============================================================================

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    This ensures connections are properly closed even if errors occur.
    Use it with the 'with' statement for automatic cleanup.
    
    Usage Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    
    Yields:
        sqlite3.Connection: Database connection with Row factory enabled
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    try:
        yield conn
    finally:
        conn.close()


# ==============================================================================
# DATABASE INITIALIZATION
# ==============================================================================

def init_database():
    """
    Create all required database tables if they do not exist.
    
    This function is safe to call multiple times. It uses
    CREATE TABLE IF NOT EXISTS so it will not destroy existing data.
    
    Tables Created:
        - users: User accounts
        - sessions: Login sessions and refresh tokens
        - operation_history: Record of encode/decode operations
        - password_reset_tokens: For password recovery feature
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # ---------------------------------------------------------------------
        # Users Table
        # Stores user account information and credentials
        # ---------------------------------------------------------------------
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
        
        # ---------------------------------------------------------------------
        # Sessions Table
        # Stores refresh tokens for JWT authentication
        # ---------------------------------------------------------------------
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
        
        # ---------------------------------------------------------------------
        # Operation History Table
        # Tracks encode/decode operations for logged in users
        # ---------------------------------------------------------------------
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
        
        # ---------------------------------------------------------------------
        # Password Reset Tokens Table
        # For password recovery functionality
        # ---------------------------------------------------------------------
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
        
        # ---------------------------------------------------------------------
        # Create Indexes for Better Query Performance
        # ---------------------------------------------------------------------
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(refresh_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON operation_history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created ON operation_history(created_at)')
        
        # ---------------------------------------------------------------------
        # Add total_points column to users table if it does not exist
        # This stores the cumulative points earned from challenges
        # ---------------------------------------------------------------------
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        conn.commit()


# ==============================================================================
# PASSWORD HASHING UTILITIES
# ==============================================================================

def generate_salt() -> str:
    """
    Generate a cryptographically secure random salt.
    
    The salt is used to make password hashes unique even if two users
    have the same password. This prevents rainbow table attacks.
    
    Returns:
        64 character hex string (32 bytes of random data)
    """
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    """
    Hash a password using PBKDF2 with SHA-256.
    
    PBKDF2 is designed to be slow, which makes brute force attacks
    much harder. We use 100,000 iterations for good security.
    
    Args:
        password: The plain text password to hash
        salt: Random salt string from generate_salt()
        
    Returns:
        Hex string of the password hash
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations for security
    ).hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """
    Check if a password matches a stored hash.
    
    Uses constant time comparison to prevent timing attacks.
    
    Args:
        password: Plain text password to verify
        salt: The salt used when hashing the original password
        password_hash: The stored hash to compare against
        
    Returns:
        True if password is correct, False otherwise
    """
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


# ==============================================================================
# USER MANAGER CLASS
# ==============================================================================

class UserManager:
    """
    Handles all user account database operations.
    
    This class provides static methods for creating users, authenticating
    logins, updating passwords, and deleting accounts. It includes input
    validation and security features like account lockout.
    
    Class Constants:
        MIN_PASSWORD_LENGTH: Minimum required password length (8)
        MAX_PASSWORD_LENGTH: Maximum allowed password length (128)
        MIN_USERNAME_LENGTH: Minimum required username length (3)
        MAX_USERNAME_LENGTH: Maximum allowed username length (30)
        MAX_FAILED_ATTEMPTS: Failed logins before lockout (5)
        LOCKOUT_DURATION_MINUTES: How long lockout lasts (15)
    """
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 30
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # --------------------------------------------------------------------------
    # Input Validation Methods
    # --------------------------------------------------------------------------
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Check if a username meets all requirements.
        
        Requirements:
            - Not empty
            - Between 3 and 30 characters
            - Only letters, numbers, and underscores
            - Cannot start with a number
        
        Args:
            username: The username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
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
        """
        Check if an email address is valid.
        
        This does basic format validation. It checks for @ and domain
        but does not verify if the email actually exists.
        
        Args:
            email: The email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        if len(email) > 255:
            return False, "Email is too long"
        # Check basic email structure
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return False, "Invalid email format"
        if '.' not in parts[1] or parts[1].startswith('.') or parts[1].endswith('.'):
            return False, "Invalid email domain"
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Check if a password meets security requirements.
        
        Requirements:
            - At least 8 characters
            - No more than 128 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character
        
        Args:
            password: The password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        if len(password) < UserManager.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {UserManager.MIN_PASSWORD_LENGTH} characters"
        if len(password) > UserManager.MAX_PASSWORD_LENGTH:
            return False, f"Password cannot exceed {UserManager.MAX_PASSWORD_LENGTH} characters"
        
        # Check for required character types
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
    
    # --------------------------------------------------------------------------
    # Account Creation
    # --------------------------------------------------------------------------
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> tuple[bool, str, Optional[int]]:
        """
        Create a new user account.
        
        Validates all inputs, checks for existing users, and creates
        the account with a hashed password.
        
        Args:
            username: Desired username
            email: User's email address
            password: Plain text password (will be hashed)
            
        Returns:
            Tuple of (success, message, user_id or None)
        """
        # Validate all inputs first
        valid, msg = UserManager.validate_username(username)
        if not valid:
            return False, msg, None
        
        valid, msg = UserManager.validate_email(email)
        if not valid:
            return False, msg, None
        
        valid, msg = UserManager.validate_password(password)
        if not valid:
            return False, msg, None
        
        # Try to create the user
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?', 
                (username.lower(), email.lower())
            )
            if cursor.fetchone():
                return False, "Username or email already exists", None
            
            # Hash password and create user
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
    
    # --------------------------------------------------------------------------
    # User Authentication
    # --------------------------------------------------------------------------
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Authenticate a user login attempt.
        
        Handles account lockout after too many failed attempts.
        Updates last login time on success.
        
        Args:
            username_or_email: Can be either username or email
            password: Plain text password to verify
            
        Returns:
            Tuple of (success, message, user_data dict or None)
        """
        if not username_or_email or not password:
            return False, "Username/email and password are required", None
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Find user by username or email
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
            
            # Check if account is locked from too many failed attempts
            if user['locked_until']:
                locked_until = datetime.fromisoformat(user['locked_until'])
                if locked_until > datetime.utcnow():
                    remaining = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
                    return False, f"Account is locked. Try again in {remaining} minutes.", None
                else:
                    # Lock period is over, reset the lock
                    cursor.execute('''
                        UPDATE users SET locked_until = NULL, failed_login_attempts = 0
                        WHERE id = ?
                    ''', (user['id'],))
            
            # Verify the password
            if not verify_password(password, user['salt'], user['password_hash']):
                # Password is wrong, increment failed attempts
                new_attempts = user['failed_login_attempts'] + 1
                
                if new_attempts >= UserManager.MAX_FAILED_ATTEMPTS:
                    # Lock the account
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
            
            # Password is correct, reset failed attempts and update last login
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
    
    # --------------------------------------------------------------------------
    # User Data Retrieval
    # --------------------------------------------------------------------------
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """
        Get user information by ID.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Dictionary with user info or None if not found
        """
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
    
    # --------------------------------------------------------------------------
    # Password Management
    # --------------------------------------------------------------------------
    
    @staticmethod
    def update_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
        """
        Change a user's password.
        
        Requires the current password for verification before allowing
        the change. Creates a new salt for the new password.
        
        Args:
            user_id: The user's database ID
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current password info
            cursor.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            # Verify current password is correct
            if not verify_password(current_password, user['salt'], user['password_hash']):
                return False, "Current password is incorrect"
            
            # Validate the new password meets requirements
            valid, msg = UserManager.validate_password(new_password)
            if not valid:
                return False, msg
            
            # Hash new password with new salt
            new_salt = generate_salt()
            new_hash = hash_password(new_password, new_salt)
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
            ''', (new_hash, new_salt, user_id))
            conn.commit()
            
            return True, "Password updated successfully"
    
    # --------------------------------------------------------------------------
    # Account Deletion
    # --------------------------------------------------------------------------
    
    @staticmethod
    def delete_user(user_id: int, password: str) -> tuple[bool, str]:
        """
        Delete a user account permanently.
        
        Requires password confirmation to prevent accidental deletion.
        
        Args:
            user_id: The user's database ID
            password: Password for confirmation
            
        Returns:
            Tuple of (success, message)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT password_hash, salt FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            # Verify password before deleting
            if not verify_password(password, user['salt'], user['password_hash']):
                return False, "Password is incorrect"
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            
            return True, "Account deleted successfully"


# ==============================================================================
# SESSION MANAGER CLASS
# ==============================================================================

class SessionManager:
    """
    Handles session and refresh token management.
    
    Sessions store refresh tokens which allow users to get new access
    tokens without logging in again. Each session tracks device info
    and can be individually revoked.
    
    Class Constants:
        REFRESH_TOKEN_EXPIRY_DAYS: How long refresh tokens last (30)
    """
    
    REFRESH_TOKEN_EXPIRY_DAYS = 30
    
    @staticmethod
    def create_session(user_id: int, device_info: str = None, ip_address: str = None) -> str:
        """
        Create a new session and return a refresh token.
        
        Args:
            user_id: The user's database ID
            device_info: Optional device/browser info (User-Agent)
            ip_address: Optional client IP address
            
        Returns:
            The refresh token string
        """
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
        """
        Check if a refresh token is valid.
        
        A token is valid if it exists, has not been invalidated, and
        has not expired.
        
        Args:
            refresh_token: The refresh token to validate
            
        Returns:
            User ID if valid, None otherwise
        """
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
            
            # Check if expired
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < datetime.utcnow():
                # Mark as invalid and return None
                cursor.execute('UPDATE sessions SET is_valid = 0 WHERE refresh_token = ?', (refresh_token,))
                conn.commit()
                return None
            
            return session['user_id']
    
    @staticmethod
    def invalidate_session(refresh_token: str) -> bool:
        """
        Invalidate a specific session (logout from one device).
        
        Args:
            refresh_token: The session's refresh token
            
        Returns:
            True if session was found and invalidated
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_valid = 0 WHERE refresh_token = ?', (refresh_token,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def invalidate_all_user_sessions(user_id: int) -> int:
        """
        Invalidate all sessions for a user (logout everywhere).
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Number of sessions invalidated
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_valid = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def get_user_sessions(user_id: int) -> List[Dict]:
        """
        Get all active sessions for a user.
        
        Useful for showing users where they are logged in.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            List of session dictionaries
        """
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
        """
        Remove expired sessions from database.
        
        Call this periodically to keep database size down.
        
        Returns:
            Number of sessions removed
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM sessions WHERE expires_at < ? OR is_valid = 0
            ''', (datetime.utcnow().isoformat(),))
            conn.commit()
            return cursor.rowcount


# ==============================================================================
# HISTORY MANAGER CLASS
# ==============================================================================

class HistoryManager:
    """
    Handles operation history tracking for users.
    
    When a logged in user encodes or decodes a message, the operation
    is recorded in history. This allows users to see their past work
    and provides statistics about their usage.
    
    Class Constants:
        MAX_PREVIEW_LENGTH: How much text to store in preview (100)
        MAX_HISTORY_ITEMS: Maximum items per user (100)
    """
    
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
        """
        Add an operation to user's history.
        
        Automatically truncates input/output data to save space.
        Also cleans up old entries if user has too many.
        
        Args:
            user_id: The user's database ID
            operation_type: Either 'encode' or 'decode'
            algorithm: Either 'zwc' (text) or 'lsb' (image)
            input_data: Preview of input data
            output_data: Preview of output data
            is_encrypted: Whether password encryption was used
            metadata: Additional info about the operation
            
        Returns:
            The ID of the new history entry
        """
        # Truncate previews to save database space
        input_preview = input_data
        if input_data and len(input_data) > HistoryManager.MAX_PREVIEW_LENGTH:
            input_preview = input_data[:HistoryManager.MAX_PREVIEW_LENGTH] + '...'
            
        output_preview = output_data
        if output_data and len(output_data) > HistoryManager.MAX_PREVIEW_LENGTH:
            output_preview = output_data[:HistoryManager.MAX_PREVIEW_LENGTH] + '...'
        
        # For images, just store a placeholder
        if algorithm == 'lsb':
            input_preview = '[Image Data]'
            output_preview = '[Image Data]'
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert the new operation
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
            
            # Clean up old entries if we have too many
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
        """
        Get operation history for a user.
        
        Results are ordered by most recent first.
        
        Args:
            user_id: The user's database ID
            limit: Maximum number of items to return
            offset: Number of items to skip (for pagination)
            
        Returns:
            List of history item dictionaries
        """
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
                # Parse metadata JSON if present
                if item['metadata']:
                    item['metadata'] = json.loads(item['metadata'])
                results.append(item)
            
            return results
    
    @staticmethod
    def get_history_count(user_id: int) -> int:
        """
        Get total number of history items for a user.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Total count of history items
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM operation_history WHERE user_id = ?', (user_id,))
            return cursor.fetchone()[0]
    
    @staticmethod
    def delete_history_item(user_id: int, history_id: int) -> bool:
        """
        Delete a specific history item.
        
        Only deletes if the item belongs to the specified user.
        
        Args:
            user_id: The user's database ID
            history_id: The history item's ID
            
        Returns:
            True if item was found and deleted
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM operation_history WHERE id = ? AND user_id = ?
            ''', (history_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def clear_user_history(user_id: int) -> int:
        """
        Delete all history for a user.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Number of items deleted
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM operation_history WHERE user_id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict:
        """
        Get statistics about a user's operations.
        
        Returns counts of different operation types and algorithms.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Dictionary with various statistics
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total operations count
            cursor.execute('SELECT COUNT(*) FROM operation_history WHERE user_id = ?', (user_id,))
            total = cursor.fetchone()[0]
            
            # Count by operation type (encode vs decode)
            cursor.execute('''
                SELECT operation_type, COUNT(*) as count 
                FROM operation_history WHERE user_id = ?
                GROUP BY operation_type
            ''', (user_id,))
            by_type = {row['operation_type']: row['count'] for row in cursor.fetchall()}
            
            # Count by algorithm (zwc vs lsb)
            cursor.execute('''
                SELECT algorithm, COUNT(*) as count 
                FROM operation_history WHERE user_id = ?
                GROUP BY algorithm
            ''', (user_id,))
            by_algorithm = {row['algorithm']: row['count'] for row in cursor.fetchall()}
            
            # Count of encrypted operations
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


# ==============================================================================
# MODULE INITIALIZATION
# ==============================================================================

# Initialize database tables when this module is imported
init_database()


# ==============================================================================
# END OF FILE
# ==============================================================================
