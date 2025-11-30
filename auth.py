"""
==============================================================================
JWT AUTHENTICATION MODULE FOR STEGANOGRAPHY APPLICATION
==============================================================================

This module handles all authentication related functionality using JWT
(JSON Web Tokens). It provides secure user authentication with support
for access tokens and refresh tokens.

Main Features:
    - Access tokens: Short lived tokens (15 minutes) for API access
    - Refresh tokens: Long lived tokens (30 days) for getting new access tokens
    - Token validation and verification
    - Rate limiting to prevent abuse
    - Security best practices implementation

Security Notes:
    - Always use environment variable for JWT_SECRET_KEY in production
    - Access tokens expire quickly to limit damage if compromised
    - Refresh tokens are stored in database and can be revoked

Compatible with PythonAnywhere deployment.
==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import jwt
import secrets
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from flask import request, jsonify, g


# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# Secret key for signing JWT tokens
# WARNING: In production always set JWT_SECRET_KEY environment variable
# The default key here is only for development and testing
JWT_SECRET_KEY = os.environ.get(
    'JWT_SECRET_KEY', 
    'dev-secret-key-change-in-production-12345678901234567890'
)

# Algorithm used for JWT signing (HS256 is secure and widely supported)
JWT_ALGORITHM = 'HS256'

# How long access tokens stay valid (15 minutes is a good balance)
ACCESS_TOKEN_EXPIRY_MINUTES = 15

# How long refresh tokens stay valid (30 days allows infrequent logins)
REFRESH_TOKEN_EXPIRY_DAYS = 30

# Token type identifiers (used to tell tokens apart)
TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_REFRESH = 'refresh'


# ==============================================================================
# CUSTOM EXCEPTION CLASSES
# ==============================================================================

class JWTError(Exception):
    """Base exception class for all JWT related errors."""
    pass


class TokenExpiredError(JWTError):
    """Raised when a token has passed its expiration time."""
    pass


class InvalidTokenError(JWTError):
    """Raised when a token is malformed or has wrong type."""
    pass


# ==============================================================================
# JWT MANAGER CLASS
# ==============================================================================

class JWTManager:
    """
    Main class for handling JWT token operations.
    
    This class provides static methods for creating, validating, and
    managing JWT tokens. It handles both access tokens (for API calls)
    and refresh tokens (for getting new access tokens).
    
    All methods are static because we do not need to store any state.
    """
    
    # --------------------------------------------------------------------------
    # Token Creation Methods
    # --------------------------------------------------------------------------
    
    @staticmethod
    def create_access_token(user_id: int, username: str, email: str) -> str:
        """
        Create a short lived access token for API authentication.
        
        Access tokens are used for making API requests. They contain user
        information and expire quickly (15 minutes) for security.
        
        Args:
            user_id: The user's database ID number
            username: The user's username string
            email: The user's email address
            
        Returns:
            A JWT token string that can be used in Authorization header
        """
        now = datetime.now(timezone.utc)
        
        # Build the token payload with all necessary claims
        payload = {
            'sub': str(user_id),  # JWT standard requires 'sub' to be a string
            'user_id': user_id,   # Keep numeric ID for convenience in code
            'username': username,
            'email': email,
            'type': TOKEN_TYPE_ACCESS,
            'iat': now,           # Issued at time
            'exp': now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
            'jti': secrets.token_hex(16)  # Unique token ID for tracking
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: int) -> Tuple[str, datetime]:
        """
        Create a long lived refresh token for getting new access tokens.
        
        Refresh tokens live longer (30 days) and are used only to get
        new access tokens. They are stored in the database so they can
        be revoked if needed.
        
        Args:
            user_id: The user's database ID number
            
        Returns:
            A tuple containing:
            - The refresh token string
            - The expiration datetime for database storage
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
    
    # --------------------------------------------------------------------------
    # Token Validation Methods
    # --------------------------------------------------------------------------
    
    @staticmethod
    def decode_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        This method checks that the token is valid, not expired, and is
        the expected type (access or refresh).
        
        Args:
            token: The JWT token string to decode
            token_type: Expected type ('access' or 'refresh')
            
        Returns:
            Dictionary containing all the token payload data
            
        Raises:
            TokenExpiredError: If the token has expired
            InvalidTokenError: If the token is invalid or wrong type
        """
        try:
            # Decode the token and verify signature
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM],
                options={
                    'require': ['sub', 'type', 'iat', 'exp', 'jti']
                }
            )
            
            # Make sure token type matches what we expect
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
        Extract JWT token from the Authorization header.
        
        Looks for a header in format: "Bearer <token>"
        
        Returns:
            The token string if found, or None if not present
        """
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
        
        # Split header into parts (should be "Bearer" and the token)
        parts = auth_header.split()
        
        # Validate format
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    @staticmethod
    def validate_access_token() -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate access token from the current request header.
        
        This is a convenience method that combines getting the token
        from header and validating it.
        
        Returns:
            A tuple containing:
            - Boolean indicating if token is valid
            - Message describing the result
            - Token payload if valid, None otherwise
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


# ==============================================================================
# ROUTE DECORATOR FUNCTIONS
# ==============================================================================

def jwt_required(f):
    """
    Decorator that requires valid JWT token for route access.
    
    Use this decorator on routes that need authentication. If no valid
    token is provided, it returns a 401 Unauthorized response.
    
    The current user information is stored in Flask's g object and can
    be accessed in the route function.
    
    Usage Example:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            user_id = g.current_user['user_id']
            return f"Hello user {user_id}"
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
        
        # Store user info in Flask's g object for the route to access
        g.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def jwt_optional(f):
    """
    Decorator for routes where authentication is optional.
    
    Use this on routes that work for both logged in and anonymous users.
    If a valid token is provided, user info is available in g.current_user.
    If no token or invalid token, g.current_user is None.
    
    Usage Example:
        @app.route('/optional-auth')
        @jwt_optional
        def optional_auth_route():
            if g.current_user:
                return f"Hello {g.current_user['username']}"
            else:
                return "Hello anonymous user"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, _, payload = JWTManager.validate_access_token()
        g.current_user = payload if is_valid else None
        return f(*args, **kwargs)
    
    return decorated_function


# ==============================================================================
# HELPER FUNCTIONS FOR GETTING CURRENT USER
# ==============================================================================

def get_current_user_id() -> Optional[int]:
    """
    Get the current authenticated user's ID.
    
    Call this inside a route that uses @jwt_required or @jwt_optional
    to get the logged in user's ID number.
    
    Returns:
        Integer user ID if logged in, None if not authenticated
    """
    if hasattr(g, 'current_user') and g.current_user:
        # Try numeric user_id first (more convenient)
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
    """
    Get the current authenticated user's username.
    
    Call this inside a route that uses @jwt_required or @jwt_optional
    to get the logged in user's username string.
    
    Returns:
        Username string if logged in, None if not authenticated
    """
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user.get('username')
    return None


# ==============================================================================
# TOKEN BLACKLIST CLASS
# ==============================================================================

class TokenBlacklist:
    """
    In memory storage for invalidated tokens.
    
    When a user logs out, their token is added here so it cannot be
    used again even if it has not expired yet. This is important for
    security when a user wants to end their session immediately.
    
    Note: This simple implementation stores tokens in memory, which
    means they are lost when the server restarts. For production with
    multiple server workers, consider using Redis or database storage.
    
    Class Attributes:
        _blacklist: Set of (token_jti, expiry) tuples
        _blacklist_cleanup_threshold: Max items before cleanup runs
    """
    
    _blacklist = set()
    _blacklist_cleanup_threshold = 1000
    
    @classmethod
    def add(cls, token_jti: str, expiry: datetime):
        """
        Add a token to the blacklist.
        
        Args:
            token_jti: The unique token identifier (jti claim)
            expiry: When the token expires (for cleanup purposes)
        """
        cls._blacklist.add((token_jti, expiry))
        
        # Clean up old entries if we have too many
        if len(cls._blacklist) > cls._blacklist_cleanup_threshold:
            cls.cleanup()
    
    @classmethod
    def is_blacklisted(cls, token_jti: str) -> bool:
        """
        Check if a token is in the blacklist.
        
        Args:
            token_jti: The unique token identifier to check
            
        Returns:
            True if token is blacklisted and should be rejected
        """
        return any(jti == token_jti for jti, _ in cls._blacklist)
    
    @classmethod
    def cleanup(cls):
        """
        Remove expired entries from blacklist to save memory.
        
        This runs automatically when the blacklist gets too large.
        Tokens that have already expired do not need to be blacklisted
        anymore since they would be rejected anyway.
        """
        now = datetime.now(timezone.utc)
        cls._blacklist = {(jti, exp) for jti, exp in cls._blacklist if exp > now}


# ==============================================================================
# AUTHENTICATION RESPONSE HELPERS
# ==============================================================================

def create_auth_response(user_id: int, username: str, email: str) -> Dict[str, Any]:
    """
    Create a complete authentication response with all tokens.
    
    This is used after successful login or signup to give the client
    everything they need for authenticated API access.
    
    Args:
        user_id: The user's database ID
        username: The user's username
        email: The user's email address
        
    Returns:
        Dictionary containing:
        - access_token: For API authentication
        - refresh_token: For getting new access tokens
        - token_type: Always "Bearer"
        - expires_in: Access token lifetime in seconds
        - refresh_expires_in: Refresh token lifetime in seconds
        - user: Object with user information
    """
    access_token = JWTManager.create_access_token(user_id, username, email)
    refresh_token, refresh_expiry = JWTManager.create_refresh_token(user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRY_MINUTES * 60,  # Convert to seconds
        'refresh_expires_in': REFRESH_TOKEN_EXPIRY_DAYS * 24 * 60 * 60,  # Convert to seconds
        'user': {
            'id': user_id,
            'username': username,
            'email': email
        }
    }


def refresh_access_token(refresh_token: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Get a new access token using a refresh token.
    
    When an access token expires, the client can use this to get a
    new one without making the user log in again.
    
    Args:
        refresh_token: The refresh token string
        
    Returns:
        Tuple containing:
        - Boolean success indicator
        - Message describing result
        - New token dictionary if successful, None otherwise
    """
    # Import here to avoid circular imports
    from database import SessionManager, UserManager
    
    try:
        # Decode and validate the refresh token
        payload = JWTManager.decode_token(refresh_token, TOKEN_TYPE_REFRESH)
        user_id = payload['sub']
        
        # Check that session is still valid in database
        session_user_id = SessionManager.validate_session(refresh_token)
        if not session_user_id or session_user_id != user_id:
            return False, "Invalid or expired session", None
        
        # Get user info to create new access token
        user = UserManager.get_user_by_id(user_id)
        if not user:
            return False, "User not found", None
        
        # Check if account is still active
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


# ==============================================================================
# RATE LIMITING
# ==============================================================================

class RateLimiter:
    """
    Simple rate limiter to prevent abuse of API endpoints.
    
    This limits how many requests a client can make in a given time
    window. It helps protect against brute force attacks and denial
    of service attempts.
    
    Note: This implementation stores data in memory, so limits are
    not shared between server workers. For production, consider using
    Redis for distributed rate limiting.
    
    Class Attributes:
        _requests: Dictionary mapping client keys to request timestamps
    """
    
    _requests = {}
    
    @classmethod
    def check(cls, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if a request is allowed within rate limits.
        
        Args:
            key: Unique identifier for the client (usually IP + endpoint)
            limit: Maximum requests allowed in the window
            window_seconds: Size of the time window in seconds
            
        Returns:
            Tuple containing:
            - Boolean indicating if request is allowed
            - Number of remaining requests (0 if not allowed)
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        
        # Get or create request list for this client
        if key not in cls._requests:
            cls._requests[key] = []
        
        # Remove requests that are outside the time window
        cls._requests[key] = [t for t in cls._requests[key] if t > window_start]
        
        # Check if we are at the limit
        current_count = len(cls._requests[key])
        if current_count >= limit:
            return False, 0
        
        # Add current request and return remaining count
        cls._requests[key].append(now)
        
        return True, limit - current_count - 1
    
    @classmethod
    def cleanup(cls):
        """
        Remove old entries to free memory.
        
        This should be called periodically in long running applications
        to prevent memory from growing indefinitely.
        """
        now = datetime.now(timezone.utc)
        hour_ago = now - timedelta(hours=1)
        
        # Find and remove empty or old entries
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
    
    Use this decorator to limit how often clients can call an endpoint.
    If the limit is exceeded, returns a 429 Too Many Requests response.
    
    Args:
        limit: Maximum number of requests allowed (default 60)
        window: Time window in seconds (default 60 = 1 minute)
        
    Usage Example:
        @app.route('/api/login')
        @rate_limit(limit=10, window=60)  # 10 requests per minute
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP address (consider proxy headers)
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            # Create unique key for this client and endpoint
            key = f"{client_ip}:{request.endpoint}"
            
            # Check rate limit
            is_allowed, remaining = RateLimiter.check(key, limit, window)
            
            if not is_allowed:
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please try again later.',
                    'code': 'RATE_LIMITED'
                }), 429
            
            # Call the actual route function
            response = f(*args, **kwargs)
            
            # Handle both tuple responses and regular responses
            if isinstance(response, tuple):
                resp, status = response
            else:
                resp = response
                status = 200
            
            return resp, status
        
        return decorated_function
    return decorator


# ==============================================================================
# END OF FILE
# ==============================================================================
