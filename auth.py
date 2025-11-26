"""
JWT Authentication Module for Steganography Application

This module provides JWT (JSON Web Token) based authentication with:
- Access tokens (short-lived)
- Refresh tokens (long-lived, stored in database)
- Token validation and refresh
- Security best practices

Compatible with PythonAnywhere deployment.
"""

import jwt
import secrets
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from flask import request, jsonify, g

# JWT Configuration
# Use a fixed secret key for development, or use environment variable for production
# WARNING: In production, always use a secure environment variable!
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production-12345678901234567890')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 30

# Token types
TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_REFRESH = 'refresh'


class JWTError(Exception):
    """Base exception for JWT errors."""
    pass


class TokenExpiredError(JWTError):
    """Token has expired."""
    pass


class InvalidTokenError(JWTError):
    """Token is invalid."""
    pass


class JWTManager:
    """Handles JWT token creation and validation."""
    
    @staticmethod
    def create_access_token(user_id: int, username: str, email: str) -> str:
        """
        Create a short-lived access token.
        
        Args:
            user_id: User's database ID
            username: User's username
            email: User's email
            
        Returns:
            JWT access token string
        """
        now = datetime.now(timezone.utc)
        payload = {
            'sub': str(user_id),  # JWT standard requires 'sub' to be a string
            'user_id': user_id,   # Keep numeric ID for convenience
            'username': username,
            'email': email,
            'type': TOKEN_TYPE_ACCESS,
            'iat': now,
            'exp': now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
            'jti': secrets.token_hex(16)  # Unique token ID
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: int) -> Tuple[str, datetime]:
        """
        Create a long-lived refresh token.
        
        Args:
            user_id: User's database ID
            
        Returns:
            Tuple of (refresh_token, expiry_datetime)
        """
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
        
        payload = {
            'sub': str(user_id),  # JWT standard requires 'sub' to be a string
            'user_id': user_id,   # Keep numeric ID for convenience
            'type': TOKEN_TYPE_REFRESH,
            'iat': now,
            'exp': expiry,
            'jti': secrets.token_hex(16)
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token, expiry
    
    @staticmethod
    def decode_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload
            
        Raises:
            TokenExpiredError: Token has expired
            InvalidTokenError: Token is invalid or wrong type
        """
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM],
                options={
                    'require': ['sub', 'type', 'iat', 'exp', 'jti']
                }
            )
            
            # Verify token type
            if payload.get('type') != token_type:
                raise InvalidTokenError(f"Invalid token type. Expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_token_from_header() -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Expected format: "Bearer <token>"
        
        Returns:
            Token string or None if not found
        """
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    @staticmethod
    def validate_access_token() -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate access token from request header.
        
        Returns:
            Tuple of (is_valid, message, payload or None)
        """
        token = JWTManager.get_token_from_header()
        
        if not token:
            return False, "No token provided", None
        
        try:
            payload = JWTManager.decode_token(token, TOKEN_TYPE_ACCESS)
            return True, "Token is valid", payload
        except TokenExpiredError:
            return False, "Token has expired", None
        except InvalidTokenError as e:
            return False, str(e), None


def jwt_required(f):
    """
    Decorator to protect routes that require authentication.
    
    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            user_id = g.current_user['sub']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message, payload = JWTManager.validate_access_token()
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'code': 'UNAUTHORIZED'
            }), 401
        
        # Store user info in Flask's g object for access in route
        g.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def jwt_optional(f):
    """
    Decorator for routes where authentication is optional.
    
    If valid token is provided, g.current_user will be set.
    If no token or invalid token, g.current_user will be None.
    
    Usage:
        @app.route('/optional-auth')
        @jwt_optional
        def optional_auth_route():
            if g.current_user:
                # User is logged in
                ...
            else:
                # Anonymous user
                ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, _, payload = JWTManager.validate_access_token()
        g.current_user = payload if is_valid else None
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user_id() -> Optional[int]:
    """Get the current authenticated user's ID."""
    if hasattr(g, 'current_user') and g.current_user:
        # Try numeric user_id first, then fall back to converting sub
        user_id = g.current_user.get('user_id')
        if user_id is not None:
            return user_id
        # Fall back to converting 'sub' (which is a string) to int
        sub = g.current_user.get('sub')
        if sub is not None:
            try:
                return int(sub)
            except (ValueError, TypeError):
                pass
    return None


def get_current_username() -> Optional[str]:
    """Get the current authenticated user's username."""
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user.get('username')
    return None


# ============================================================================
# Token Blacklist (for logout functionality)
# ============================================================================

class TokenBlacklist:
    """
    In-memory token blacklist for invalidated tokens.
    
    Note: For production with multiple workers, use Redis or database.
    This simple implementation works for single-worker deployments.
    """
    
    _blacklist = set()
    _blacklist_cleanup_threshold = 1000
    
    @classmethod
    def add(cls, token_jti: str, expiry: datetime):
        """Add a token JTI to the blacklist."""
        cls._blacklist.add((token_jti, expiry))
        
        # Cleanup old entries if too many
        if len(cls._blacklist) > cls._blacklist_cleanup_threshold:
            cls.cleanup()
    
    @classmethod
    def is_blacklisted(cls, token_jti: str) -> bool:
        """Check if a token JTI is blacklisted."""
        return any(jti == token_jti for jti, _ in cls._blacklist)
    
    @classmethod
    def cleanup(cls):
        """Remove expired entries from blacklist."""
        now = datetime.now(timezone.utc)
        cls._blacklist = {(jti, exp) for jti, exp in cls._blacklist if exp > now}


# ============================================================================
# Auth Response Helpers
# ============================================================================

def create_auth_response(user_id: int, username: str, email: str) -> Dict[str, Any]:
    """
    Create authentication response with access and refresh tokens.
    
    Args:
        user_id: User's database ID
        username: User's username
        email: User's email
        
    Returns:
        Dictionary with tokens and user info
    """
    access_token = JWTManager.create_access_token(user_id, username, email)
    refresh_token, refresh_expiry = JWTManager.create_refresh_token(user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRY_MINUTES * 60,  # seconds
        'refresh_expires_in': REFRESH_TOKEN_EXPIRY_DAYS * 24 * 60 * 60,  # seconds
        'user': {
            'id': user_id,
            'username': username,
            'email': email
        }
    }


def refresh_access_token(refresh_token: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token string
        
    Returns:
        Tuple of (success, message, new_tokens_dict or None)
    """
    from database import SessionManager, UserManager
    
    try:
        # Decode refresh token
        payload = JWTManager.decode_token(refresh_token, TOKEN_TYPE_REFRESH)
        user_id = payload['sub']
        
        # Validate session in database
        session_user_id = SessionManager.validate_session(refresh_token)
        if not session_user_id or session_user_id != user_id:
            return False, "Invalid or expired session", None
        
        # Get user info
        user = UserManager.get_user_by_id(user_id)
        if not user:
            return False, "User not found", None
        
        if not user.get('is_active', True):
            return False, "Account is deactivated", None
        
        # Create new access token
        new_access_token = JWTManager.create_access_token(
            user_id, 
            user['username'], 
            user['email']
        )
        
        return True, "Token refreshed", {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRY_MINUTES * 60
        }
        
    except TokenExpiredError:
        return False, "Refresh token has expired. Please login again.", None
    except InvalidTokenError as e:
        return False, str(e), None


# ============================================================================
# Rate Limiting (Simple Implementation)
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    Note: For production with multiple workers, use Redis.
    """
    
    _requests = {}
    
    @classmethod
    def check(cls, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique key for the client (e.g., IP address)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        
        # Get or create request list for this key
        if key not in cls._requests:
            cls._requests[key] = []
        
        # Filter out old requests
        cls._requests[key] = [t for t in cls._requests[key] if t > window_start]
        
        # Check limit
        current_count = len(cls._requests[key])
        if current_count >= limit:
            return False, 0
        
        # Add current request
        cls._requests[key].append(now)
        
        return True, limit - current_count - 1
    
    @classmethod
    def cleanup(cls):
        """Remove old entries to free memory."""
        now = datetime.now(timezone.utc)
        hour_ago = now - timedelta(hours=1)
        
        keys_to_remove = []
        for key, timestamps in cls._requests.items():
            cls._requests[key] = [t for t in timestamps if t > hour_ago]
            if not cls._requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del cls._requests[key]


def rate_limit(limit: int = 60, window: int = 60):
    """
    Decorator to apply rate limiting to a route.
    
    Args:
        limit: Maximum requests per window
        window: Time window in seconds
        
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as key
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            key = f"{client_ip}:{request.endpoint}"
            
            is_allowed, remaining = RateLimiter.check(key, limit, window)
            
            if not is_allowed:
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please try again later.',
                    'code': 'RATE_LIMITED'
                }), 429
            
            response = f(*args, **kwargs)
            
            # Add rate limit headers if it's a tuple response
            if isinstance(response, tuple):
                resp, status = response
            else:
                resp = response
                status = 200
            
            return resp, status
        
        return decorated_function
    return decorator
