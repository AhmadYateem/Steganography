"""
================================================================================
STEGANOGRAPHY WEB API - MAIN APPLICATION MODULE
================================================================================

This is the main Flask application that provides a complete REST API for
steganography operations. The API supports hiding and extracting secret
messages using both text and image based techniques.

MAIN FEATURES:
    1. Text Steganography    - Hide messages using zero width characters (ZWC)
    2. Image Steganography   - Hide messages using LSB (Least Significant Bit)
    3. AES 256 Encryption    - Optional password protection for all messages
    4. JWT Authentication    - Secure user sessions with access and refresh tokens
    5. Operation History     - Track all encode and decode operations per user
    6. AI Chatbot           - Get help with steganography questions
    7. Challenge System      - Practice and learn steganography techniques
    8. Multi File Stego      - Split secrets across multiple images

API ENDPOINTS OVERVIEW:

    System Endpoints:
        GET  /ping                  - Health check and version info
        GET  /api/limits            - Get system limits and recommendations
        GET  /api/algorithms        - List all available algorithms

    Steganography Endpoints:
        POST /api/encode            - Hide message in text or image
        POST /api/decode            - Extract hidden message from carrier
        POST /api/analyze           - Compare original and stego image quality

    Authentication Endpoints:
        POST /api/auth/signup       - Create new user account
        POST /api/auth/login        - Login and receive tokens
        POST /api/auth/refresh      - Get new access token
        POST /api/auth/logout       - End current session
        GET  /api/auth/me           - Get current user profile
        PUT  /api/auth/password     - Change account password
        DELETE /api/auth/account    - Delete account permanently
        GET  /api/auth/sessions     - List all active sessions

    History Endpoints:
        GET  /api/history           - Get operation history with pagination
        DELETE /api/history/:id     - Delete single history item
        DELETE /api/history         - Clear all user history
        GET  /api/history/stats     - Get usage statistics

    Advanced Features:
        POST /api/chatbot           - AI assistant for steganography help
        GET  /api/challenges        - Get practice challenges
        POST /api/challenges/:id/solve - Submit challenge solution
        POST /api/detect/image      - Detect stego in image
        POST /api/detect/text       - Detect stego in text
        POST /api/multi-encode      - Split secret across images
        POST /api/multi-decode      - Reconstruct secret from parts

Author: Steganography Team
Version: 2.0.0
================================================================================
"""


# ==============================================================================
# SECTION 1: IMPORTS AND DEPENDENCIES
# ==============================================================================
# All external and internal module imports are organized here.
# We import Flask for the web server, CORS for cross origin requests,
# and our custom modules for steganography, security, and database.
# ==============================================================================

# Standard library imports for core functionality
from flask import Flask, request, jsonify, send_file, send_from_directory, g, redirect
from flask_cors import CORS
import base64
import io
import os
import tempfile
from typing import Dict, Any
from PIL import Image

# Our steganography implementation modules
# These handle the actual encoding and decoding of messages
import text_stego      # Zero width character steganography for text
import image_stego     # LSB steganography for images
import security        # AES encryption and security utilities
import metrics         # Image quality metrics (PSNR, SSIM, MSE)

# Authentication and database modules
# These handle user accounts, sessions, and operation history
from auth import (
    JWTManager,              # JWT token management
    jwt_required,            # Decorator for protected routes
    jwt_optional,            # Decorator for optionally authenticated routes
    get_current_user_id,     # Get user ID from current request
    create_auth_response,    # Create login response with tokens
    refresh_access_token,    # Refresh expired access tokens
    rate_limit,              # Rate limiting decorator
    TokenBlacklist           # Manage invalidated tokens
)
from database import (
    UserManager,             # User account operations
    SessionManager,          # Session management
    HistoryManager,          # Operation history tracking
    init_database            # Database initialization
)


# ==============================================================================
# SECTION 2: APPLICATION INITIALIZATION
# ==============================================================================
# Initialize the Flask application, database, and configure security settings.
# ==============================================================================

# Initialize the database tables on startup
# This creates all required tables if they do not exist yet
init_database()

# Create the Flask application instance
# The static folder contains our frontend HTML, CSS, and JavaScript files
app = Flask(__name__, static_folder='static')

# Set maximum file upload size to 16 megabytes
# This prevents users from uploading very large files that could slow the server
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# JWT secret key for signing tokens
# In production this should be set via environment variable for security
# If not set, we generate a random key (but this means tokens will not persist across restarts)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', os.urandom(32).hex())

# Enable CORS (Cross Origin Resource Sharing) for all routes
# This allows the frontend to make requests from any domain
# The credentials support allows sending cookies and auth headers
CORS(app, supports_credentials=True, origins=['*'])


# ==============================================================================
# SECTION 3: SYSTEM LIMITS CONFIGURATION
# ==============================================================================
# Define all system limits in one place for easy configuration.
# These limits protect the server from abuse and ensure good performance.
# ==============================================================================

SYSTEM_LIMITS = {
    # File size limits
    'max_file_size_mb': 16,                    # Maximum upload size in megabytes
    'max_file_size_bytes': 16 * 1024 * 1024,   # Same limit in bytes for validation

    # Text length limits
    'max_text_message_length': 100000,         # 100KB max for cover text
    'max_secret_message_length': 50000,        # 50KB max for secret message

    # Image dimension limits
    'max_image_dimension': 4096,               # Maximum width or height in pixels
    'min_image_dimension': 10,                 # Minimum width or height in pixels

    # Supported formats
    'supported_image_formats': ['png', 'jpg', 'jpeg', 'bmp', 'gif'],

    # History limits
    'max_history_items': 100,                  # Maximum stored history per user

    # Rate limiting configuration (requests per time window)
    'rate_limits': {
        'encode': {'limit': 30, 'window': 60},   # 30 encodes per minute
        'decode': {'limit': 30, 'window': 60},   # 30 decodes per minute
        'auth': {'limit': 10, 'window': 60}      # 10 auth attempts per minute
    }
}


# ==============================================================================
# SECTION 4: UTILITY FUNCTIONS
# ==============================================================================
# Helper functions used throughout the application for common tasks like
# creating responses, encoding images, and validating input data.
# ==============================================================================

def error_response(message: str, status_code: int = 400, code: str = None) -> tuple:
    """
    Create a standardized error response for the API.

    All error responses follow the same format for consistency.
    This makes it easier for the frontend to handle errors.

    Args:
        message: Human readable error message to display
        status_code: HTTP status code (400 for bad request, 401 for auth error, etc)
        code: Optional error code for programmatic error handling

    Returns:
        Tuple of (JSON response, status code)
    """
    response = {'error': message, 'success': False}
    if code:
        response['code'] = code
    return jsonify(response), status_code


def success_response(data: Dict[str, Any], message: str = None) -> tuple:
    """
    Create a standardized success response for the API.

    All success responses include success=True and any additional data.

    Args:
        data: Dictionary of data to include in response
        message: Optional success message

    Returns:
        Tuple of (JSON response, 200 status code)
    """
    response = {'success': True, **data}
    if message:
        response['message'] = message
    return jsonify(response), 200


def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode a base64 encoded image string to raw bytes.

    Handles both raw base64 and data URL format (data:image/png;base64,xxx).
    The frontend may send images in either format.

    Args:
        base64_string: The base64 encoded image data

    Returns:
        Raw image bytes

    Raises:
        ValueError: If the base64 string is invalid
    """
    try:
        # Check if this is a data URL and extract just the base64 part
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 image data: {e}")


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to a base64 string.

    This is used to send processed images back to the frontend.

    Args:
        image_path: Path to the image file on disk

    Returns:
        Base64 encoded string of the image
    """
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('ascii')


def validate_image_dimensions(image_data: bytes) -> tuple[bool, str, dict]:
    """
    Validate that an image meets our size requirements and calculate capacity.

    This function checks that images are not too large or too small.
    It also calculates how many characters can be hidden in the image.

    Args:
        image_data: Raw bytes of the image file

    Returns:
        Tuple of (is_valid, message, info_dict)
        - is_valid: True if image passes validation
        - message: Error message if invalid, "Valid" if valid
        - info_dict: Image information including dimensions and capacity
    """
    try:
        from PIL import Image
        import io

        # Open image and get dimensions
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size

        # Check if image is too large
        max_dim = SYSTEM_LIMITS['max_image_dimension']
        if width > max_dim or height > max_dim:
            return False, f"Image too large. Maximum dimension is {max_dim}x{max_dim} pixels", {}

        # Check if image is too small
        min_dim = SYSTEM_LIMITS['min_image_dimension']
        if width < min_dim or height < min_dim:
            return False, f"Image too small. Minimum dimension is {min_dim}x{min_dim} pixels", {}

        # Calculate how many characters can be hidden
        # Each pixel has 3 color channels (RGB), each can store 1 bit
        capacity_bits = width * height * 3
        capacity_chars = capacity_bits // 8

        return True, "Valid", {
            'width': width,
            'height': height,
            'format': img.format,
            'mode': img.mode,
            'capacity_bytes': capacity_chars,
            'capacity_text': f"~{capacity_chars:,} characters"
        }
    except Exception as e:
        return False, f"Invalid image: {str(e)}", {}


def get_client_ip() -> str:
    """
    Get the client IP address from the request.

    This handles the case where the app is behind a proxy or load balancer.
    In that case, the real IP is in the X-Forwarded-For header.

    Returns:
        Client IP address as string
    """
    # Check for proxy header first
    if request.headers.get('X-Forwarded-For'):
        # The header can contain multiple IPs, we want the first one
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # Fall back to direct connection IP
    return request.remote_addr or 'unknown'


def safe_delete_file(filepath: str, max_retries: int = 5, delay: float = 0.1) -> bool:
    """
    Safely delete a temporary file with retries for Windows file locking.

    On Windows, files can sometimes be locked by other processes even after
    we close them. This function retries the deletion with small delays.

    Args:
        filepath: Path to the file to delete
        max_retries: How many times to try before giving up
        delay: Seconds to wait between retries

    Returns:
        True if file was deleted or does not exist, False if deletion failed
    """
    import time
    import gc

    # If file does not exist, consider it a success
    if not os.path.exists(filepath):
        return True

    # Try to delete with retries
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release any file handles
            gc.collect()
            os.unlink(filepath)
            return True
        except PermissionError:
            # File is still locked, wait and try again
            if attempt < max_retries - 1:
                time.sleep(delay)
            continue
        except Exception:
            # Some other error occurred
            return False

    return False


# ==============================================================================
# SECTION 5: FRONTEND AND STATIC FILE ROUTES
# ==============================================================================
# Routes for serving the frontend application and static files.
# ==============================================================================

@app.route('/')
def index():
    """
    Serve the main frontend application page.

    This is the entry point for users accessing the web interface.
    It returns the index.html file from the static folder.
    """
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """
    Serve static files like CSS, JavaScript, and images.

    This route handles requests for any file in the static folder.
    It checks that the path does not conflict with API routes.

    Args:
        filename: Path to the requested file
    """
    # Make sure we do not accidentally serve API routes as files
    if not filename.startswith('api/') and not filename.startswith('ping'):
        try:
            return send_from_directory('static', filename)
        except:
            pass
    # If file not found or is an API route, return 404
    from flask import abort
    abort(404)


@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check endpoint for monitoring.

    This endpoint can be used by load balancers, monitoring tools,
    or deployment scripts to check if the server is running.

    Returns:
        JSON with status, version, and available features
    """
    return jsonify({
        'status': 'ok',
        'message': 'Steganography API is running',
        'version': '2.0.0',
        'features': ['text_stego', 'image_stego', 'encryption', 'jwt_auth', 'history']
    })


# ==============================================================================
# SECTION 6: SYSTEM INFORMATION ENDPOINTS
# ==============================================================================
# Endpoints that provide information about system capabilities and limits.
# ==============================================================================

@app.route('/api/limits', methods=['GET'])
def get_limits():
    """
    Get system limits and recommendations.

    This endpoint tells the frontend what limits are in place so it can
    validate input before sending requests. It also provides recommendations
    for optimal usage.

    Returns:
        JSON with limits (file sizes, dimensions, etc) and recommendations
    """
    return success_response({
        'limits': {
            'max_file_size_mb': SYSTEM_LIMITS['max_file_size_mb'],
            'max_file_size_bytes': SYSTEM_LIMITS['max_file_size_bytes'],
            'max_text_length': SYSTEM_LIMITS['max_text_message_length'],
            'max_secret_length': SYSTEM_LIMITS['max_secret_message_length'],
            'max_image_dimension': SYSTEM_LIMITS['max_image_dimension'],
            'min_image_dimension': SYSTEM_LIMITS['min_image_dimension'],
            'supported_formats': SYSTEM_LIMITS['supported_image_formats'],
            'max_history_items': SYSTEM_LIMITS['max_history_items']
        },
        'recommendations': {
            'optimal_image_size': '1920x1080 or smaller for fast processing',
            'optimal_text_length': '1000-5000 characters for cover text',
            'password_strength': 'At least 8 characters with uppercase, lowercase, number, and special character'
        }
    })


# ==============================================================================
# SECTION 7: AUTHENTICATION ENDPOINTS
# ==============================================================================
# All user authentication related endpoints including signup, login, logout,
# token refresh, password change, and account deletion.
# These endpoints use JWT tokens for stateless authentication.
# ==============================================================================

@app.route('/api/auth/signup', methods=['POST'])
@rate_limit(limit=10, window=60)
def signup():
    """
    Create a new user account.

    This endpoint validates the username, email, and password,
    creates the user in the database, and returns authentication tokens.

    Request Body:
        username: String, 3 to 30 characters, alphanumeric and underscore only
        email: Valid email address
        password: At least 8 characters with uppercase, lowercase, digit, and special char

    Returns:
        User info and authentication tokens on success
        Error message if validation fails or username/email already exists
    """
    try:
        data = request.get_json()

        # Check that we received JSON data
        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        # Extract and clean the input fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Create the user account (validation happens in UserManager)
        success, message, user_id = UserManager.create_user(username, email, password)

        if not success:
            return error_response(message, 400, "SIGNUP_FAILED")

        # Create a session for the new user
        device_info = request.headers.get('User-Agent', 'Unknown')
        refresh_token = SessionManager.create_session(user_id, device_info, get_client_ip())

        # Generate JWT tokens for the user
        auth_data = create_auth_response(user_id, username.lower(), email.lower())
        auth_data['refresh_token'] = refresh_token

        return success_response(auth_data, "Account created successfully")

    except Exception as e:
        return error_response(f"Signup failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/login', methods=['POST'])
@rate_limit(limit=10, window=60)
def login():
    """
    Authenticate user and return tokens.

    Users can login with either their username or email address.
    On success, they receive access and refresh tokens.

    Request Body:
        username_or_email: The username or email to login with
        password: The user password

    Returns:
        Authentication tokens and user info on success
        Error message if credentials are invalid
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        # Both fields are required
        if not username_or_email or not password:
            return error_response("Username/email and password are required", 400, "MISSING_FIELDS")

        # Try to authenticate the user
        success, message, user_data = UserManager.authenticate_user(username_or_email, password)

        if not success:
            return error_response(message, 401, "AUTH_FAILED")

        # Create a new session for this login
        device_info = request.headers.get('User-Agent', 'Unknown')
        refresh_token = SessionManager.create_session(
            user_data['id'],
            device_info,
            get_client_ip()
        )

        # Generate JWT tokens
        auth_data = create_auth_response(
            user_data['id'],
            user_data['username'],
            user_data['email']
        )
        auth_data['refresh_token'] = refresh_token

        return success_response(auth_data, "Login successful")

    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/refresh', methods=['POST'])
@rate_limit(limit=30, window=60)
def refresh_token():
    """
    Get a new access token using a refresh token.

    Access tokens expire after 15 minutes. When they expire, the frontend
    can use this endpoint with the refresh token to get a new access token
    without requiring the user to login again.

    Request Body:
        refresh_token: The refresh token received at login

    Returns:
        New access token on success
        Error if refresh token is invalid or expired
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        refresh_token_str = data.get('refresh_token', '')

        if not refresh_token_str:
            return error_response("Refresh token is required", 400, "MISSING_TOKEN")

        # Try to refresh the access token
        success, message, tokens = refresh_access_token(refresh_token_str)

        if not success:
            return error_response(message, 401, "REFRESH_FAILED")

        return success_response(tokens, "Token refreshed")

    except Exception as e:
        return error_response(f"Token refresh failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Logout user and end the current session.

    This invalidates the refresh token so it cannot be used again.
    The user can also choose to logout from all devices at once.

    Request Body (optional):
        refresh_token: The refresh token to invalidate
        all_sessions: Set to true to logout from all devices

    Returns:
        Success message with count of sessions invalidated
    """
    try:
        data = request.get_json() or {}
        user_id = get_current_user_id()

        # Check if user wants to logout from all devices
        if data.get('all_sessions'):
            count = SessionManager.invalidate_all_user_sessions(user_id)
            return success_response({'sessions_invalidated': count}, f"Logged out from {count} sessions")

        # Otherwise just logout from this session
        refresh_token_str = data.get('refresh_token')
        if refresh_token_str:
            SessionManager.invalidate_session(refresh_token_str)

        return success_response({}, "Logged out successfully")

    except Exception as e:
        return error_response(f"Logout failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    """
    Get current user profile and statistics.

    Returns the user profile information and their usage statistics
    like total operations and favorite algorithms.

    Returns:
        User profile data and statistics
    """
    try:
        user_id = get_current_user_id()
        user = UserManager.get_user_by_id(user_id)

        if not user:
            return error_response("User not found", 404, "USER_NOT_FOUND")

        # Get statistics for this user
        stats = HistoryManager.get_user_stats(user_id)

        return success_response({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'last_login': user['last_login']
            },
            'stats': stats
        })

    except Exception as e:
        return error_response(f"Failed to get user info: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/password', methods=['PUT'])
@jwt_required
@rate_limit(limit=5, window=60)
def change_password():
    """
    Change the user password.

    Requires the current password for verification before setting the new one.
    Optionally can logout from all other sessions after changing password.

    Request Body:
        current_password: The current password for verification
        new_password: The new password (must meet requirements)
        logout_other_sessions: Optional, set true to invalidate other sessions

    Returns:
        Success message if password was changed
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return error_response("Both current and new password are required", 400, "MISSING_FIELDS")

        user_id = get_current_user_id()
        success, message = UserManager.update_password(user_id, current_password, new_password)

        if not success:
            return error_response(message, 400, "PASSWORD_CHANGE_FAILED")

        # Optionally invalidate all other sessions for security
        if data.get('logout_other_sessions'):
            SessionManager.invalidate_all_user_sessions(user_id)

        return success_response({}, message)

    except Exception as e:
        return error_response(f"Password change failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/account', methods=['DELETE'])
@jwt_required
@rate_limit(limit=3, window=60)
def delete_account():
    """
    Delete user account permanently.

    This is a destructive action that cannot be undone.
    Requires password confirmation for safety.

    Request Body:
        password: Current password to confirm the deletion

    Returns:
        Success message if account was deleted
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        password = data.get('password', '')

        if not password:
            return error_response("Password is required to confirm deletion", 400, "MISSING_PASSWORD")

        user_id = get_current_user_id()
        success, message = UserManager.delete_user(user_id, password)

        if not success:
            return error_response(message, 400, "DELETION_FAILED")

        return success_response({}, message)

    except Exception as e:
        return error_response(f"Account deletion failed: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/auth/sessions', methods=['GET'])
@jwt_required
def get_sessions():
    """
    Get all active sessions for the current user.

    This shows all devices and locations where the user is logged in.
    Useful for security to see if there are any unknown sessions.

    Returns:
        List of active sessions with device info and last activity
    """
    try:
        user_id = get_current_user_id()
        sessions = SessionManager.get_user_sessions(user_id)

        return success_response({
            'sessions': sessions,
            'count': len(sessions)
        })

    except Exception as e:
        return error_response(f"Failed to get sessions: {str(e)}", 500, "SERVER_ERROR")


# ==============================================================================
# SECTION 8: HISTORY ENDPOINTS
# ==============================================================================
# Endpoints for managing operation history. Users can view their past
# encode and decode operations, delete individual items, or clear all history.
# ==============================================================================

@app.route('/api/history', methods=['GET'])
@jwt_required
def get_history():
    """
    Get operation history for the current user.

    Returns a paginated list of past operations with details about
    what algorithm was used, whether encryption was enabled, etc.

    Query Parameters:
        limit: Number of items to return (default 50, max 100)
        offset: Starting position for pagination (default 0)

    Returns:
        List of history items with pagination info
    """
    try:
        user_id = get_current_user_id()

        # Parse pagination parameters with limits
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        # Get history from database
        history = HistoryManager.get_user_history(user_id, limit, offset)
        total = HistoryManager.get_history_count(user_id)

        return success_response({
            'history': history,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(history) < total
        })

    except Exception as e:
        return error_response(f"Failed to get history: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@jwt_required
def delete_history_item(history_id):
    """
    Delete a specific history item.

    Users can only delete their own history items.

    Args:
        history_id: The ID of the history item to delete

    Returns:
        Success message if deleted, error if not found
    """
    try:
        user_id = get_current_user_id()
        success = HistoryManager.delete_history_item(user_id, history_id)

        if not success:
            return error_response("History item not found", 404, "NOT_FOUND")

        return success_response({}, "History item deleted")

    except Exception as e:
        return error_response(f"Failed to delete history: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/history', methods=['DELETE'])
@jwt_required
def clear_history():
    """
    Clear all history for the current user.

    This deletes all operation history. This action cannot be undone.

    Returns:
        Count of items that were deleted
    """
    try:
        user_id = get_current_user_id()
        count = HistoryManager.clear_user_history(user_id)

        return success_response({'deleted': count}, f"Cleared {count} history items")

    except Exception as e:
        return error_response(f"Failed to clear history: {str(e)}", 500, "SERVER_ERROR")


@app.route('/api/history/stats', methods=['GET'])
@jwt_required
def get_history_stats():
    """
    Get usage statistics for the current user.

    Returns aggregated statistics about the user operations including
    total operations, most used algorithms, and encryption usage.

    Returns:
        Statistics object with usage metrics
    """
    try:
        user_id = get_current_user_id()
        stats = HistoryManager.get_user_stats(user_id)

        return success_response({'stats': stats})

    except Exception as e:
        return error_response(f"Failed to get stats: {str(e)}", 500, "SERVER_ERROR")


# ==============================================================================
# SECTION 9: ALGORITHM INFORMATION ENDPOINT
# ==============================================================================
# Provides information about available steganography algorithms.
# ==============================================================================

@app.route('/api/algorithms', methods=['GET'])
def get_algorithms():
    """
    List all available steganography algorithms.

    This endpoint returns detailed information about each algorithm
    including parameters, capabilities, and quality metrics.

    Returns:
        List of available algorithms with their specifications
    """
    algorithms = {
        'text': [
            {
                'id': 'zwc',
                'name': 'Zero-Width Characters (ZWC)',
                'description': 'Hide messages using invisible Unicode characters',
                'encoding_bits': [1, 2],
                'insertion_methods': ['append', 'between_words', 'distributed'],
                'supports_encryption': True
            }
        ],
        'image': [
            {
                'id': 'lsb',
                'name': 'Least Significant Bit (LSB)',
                'description': 'Hide messages in the least significant bits of image pixels',
                'bits_per_pixel': [1, 2, 3],
                'channels': ['blue', 'green', 'red'],
                'supports_encryption': True,
                'quality_metrics': ['MSE', 'PSNR', 'SSIM']
            }
        ]
    }

    return success_response({
        'algorithms': algorithms,
        'total_count': len(algorithms['text']) + len(algorithms['image'])
    })


# ==============================================================================
# SECTION 10: MESSAGE ENCODING ENDPOINT
# ==============================================================================
# The main endpoint for hiding secret messages in cover text or images.
# Supports both ZWC (text) and LSB (image) algorithms with optional encryption.
# ==============================================================================

@app.route('/api/encode', methods=['POST'])
@jwt_optional
def encode_message():
    """
    Hide a secret message in cover text or an image.

    This is the main encoding endpoint that supports two algorithms:
    1. ZWC (Zero Width Characters) for text steganography
    2. LSB (Least Significant Bit) for image steganography

    Both algorithms support optional password encryption using AES 256.

    Request Body for Text (ZWC):
        algorithm: "zwc"
        cover_text: The public visible text to hide message in
        secret_message: The message to hide
        password: Optional password for encryption
        encoding_bits: 1 or 2 bits per ZWC character (default 2)
        insertion_method: "append", "between_words", or "distributed"

    Request Body for Image (LSB):
        algorithm: "lsb"
        cover_image: Base64 encoded image data
        secret_message: The message to hide
        password: Optional password for encryption
        bits_per_pixel: 1, 2, or 3 bits per pixel (default 2)
        channel: 0 (red), 1 (green), or 2 (blue, default)

    Returns:
        Encoded stego text or stego image with operation details
    """
    try:
        data = request.get_json()

        # Validate that we received JSON data
        if not data:
            return error_response("No JSON data provided", 400, "INVALID_REQUEST")

        # Extract common parameters
        algorithm = data.get('algorithm', '').lower()
        secret_message = data.get('secret_message')
        password = data.get('password')

        # Secret message is always required
        if not secret_message:
            return error_response("'secret_message' is required", 400, "MISSING_FIELD")

        # Validate message length against limits
        if len(secret_message) > SYSTEM_LIMITS['max_secret_message_length']:
            return error_response(
                f"Secret message too long. Maximum is {SYSTEM_LIMITS['max_secret_message_length']:,} characters",
                400, "MESSAGE_TOO_LONG"
            )

        # Get current user ID if they are authenticated (for history tracking)
        user_id = get_current_user_id()

        # ======================================================================
        # TEXT STEGANOGRAPHY using Zero Width Characters (ZWC)
        # ======================================================================
        if algorithm == 'zwc':
            cover_text = data.get('cover_text')

            # Cover text is required for text steganography
            if not cover_text:
                return error_response("'cover_text' is required for text steganography", 400, "MISSING_FIELD")

            # Validate cover text length
            if len(cover_text) > SYSTEM_LIMITS['max_text_message_length']:
                return error_response(
                    f"Cover text too long. Maximum is {SYSTEM_LIMITS['max_text_message_length']:,} characters",
                    400, "TEXT_TOO_LONG"
                )

            # Get optional parameters with defaults
            encoding_bits = data.get('encoding_bits', 2)
            insertion_method = data.get('insertion_method', 'between_words')

            # Validate encoding bits (1 or 2)
            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2", 400, "INVALID_PARAM")

            # Validate insertion method
            if insertion_method not in ['append', 'between_words', 'distributed']:
                return error_response("Invalid insertion_method", 400, "INVALID_PARAM")

            # Encrypt the message if password is provided
            message_to_hide = secret_message
            if password:
                message_to_hide = security.encrypt_message(secret_message, password)

            # Perform the encoding using the text_stego module
            stego_text = text_stego.encode_message(
                cover_text=cover_text,
                secret_message=message_to_hide,
                encoding_bits=encoding_bits,
                insertion_method=insertion_method
            )

            # Save to history if user is authenticated
            if user_id:
                HistoryManager.add_operation(
                    user_id=user_id,
                    operation_type='encode',
                    algorithm='zwc',
                    input_data=cover_text,
                    output_data=stego_text,
                    is_encrypted=bool(password),
                    metadata={
                        'encoding_bits': encoding_bits,
                        'insertion_method': insertion_method,
                        'cover_length': len(cover_text),
                        'secret_length': len(secret_message)
                    }
                )

            # Return success with all relevant details
            return success_response({
                'stego_text': stego_text,
                'algorithm': 'zwc',
                'encrypted': bool(password),
                'encoding_bits': encoding_bits,
                'insertion_method': insertion_method,
                'cover_length': len(cover_text),
                'stego_length': len(stego_text),
                'message_length': len(secret_message),
                'history_saved': bool(user_id)
            }, message="Message encoded successfully in text")

        # ======================================================================
        # IMAGE STEGANOGRAPHY using Least Significant Bit (LSB)
        # ======================================================================
        elif algorithm == 'lsb':
            cover_image_b64 = data.get('cover_image')

            # Cover image is required for image steganography
            if not cover_image_b64:
                return error_response("'cover_image' (base64) is required for image steganography", 400, "MISSING_FIELD")

            # Get optional parameters with defaults
            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default to blue channel

            # Validate bits per pixel (1, 2, or 3)
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3", 400, "INVALID_PARAM")

            # Validate channel selection
            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)", 400, "INVALID_PARAM")

            # Decode the base64 image data
            cover_image_data = decode_base64_image(cover_image_b64)

            # Validate image dimensions against limits
            is_valid, msg, img_info = validate_image_dimensions(cover_image_data)
            if not is_valid:
                return error_response(msg, 400, "INVALID_IMAGE")

            # Create temporary files for processing
            # We need to save to disk because PIL and our image_stego module work with files
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as cover_temp:
                cover_temp.write(cover_image_data)
                cover_temp_path = cover_temp.name

            stego_temp_path = tempfile.mktemp(suffix='.png')

            try:
                # Encrypt the message if password is provided
                message_to_hide = secret_message
                if password:
                    message_to_hide = security.encrypt_message(secret_message, password)

                # Perform the LSB encoding
                result = image_stego.encode_lsb(
                    image_path=cover_temp_path,
                    message=message_to_hide,
                    output_path=stego_temp_path,
                    bits_per_pixel=bits_per_pixel,
                    channel=channel
                )

                # Encode the stego image back to base64 for the response
                stego_image_b64 = encode_image_to_base64(stego_temp_path)

                # Save to history if user is authenticated
                if user_id:
                    HistoryManager.add_operation(
                        user_id=user_id,
                        operation_type='encode',
                        algorithm='lsb',
                        input_data='[Image]',
                        output_data='[Image]',
                        is_encrypted=bool(password),
                        metadata={
                            'bits_per_pixel': bits_per_pixel,
                            'channel': ['red', 'green', 'blue'][channel],
                            'pixels_modified': result['pixels_modified'],
                            'capacity_used_percent': result['capacity_used_percent'],
                            'secret_length': len(secret_message),
                            'image_dimensions': f"{img_info['width']}x{img_info['height']}"
                        }
                    )

                # Return success with all relevant details
                return success_response({
                    'stego_image': stego_image_b64,
                    'algorithm': 'lsb',
                    'encrypted': bool(password),
                    'bits_per_pixel': bits_per_pixel,
                    'channel': channel,
                    'channel_name': ['red', 'green', 'blue'][channel],
                    'pixels_modified': result['pixels_modified'],
                    'capacity_used_percent': result['capacity_used_percent'],
                    'message_length': len(secret_message),
                    'image_info': img_info,
                    'history_saved': bool(user_id)
                }, message="Message encoded successfully in image")

            finally:
                # Always cleanup temporary files even if an error occurred
                safe_delete_file(cover_temp_path)
                safe_delete_file(stego_temp_path)

        else:
            # Unknown algorithm specified
            return error_response(f"Unknown algorithm: '{algorithm}'. Use 'zwc' or 'lsb'")

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Encoding failed: {str(e)}", 500)


# ==============================================================================
# SECTION 11: MESSAGE DECODING ENDPOINT
# ==============================================================================
# The main endpoint for extracting hidden messages from stego text or images.
# Supports both ZWC (text) and LSB (image) algorithms with optional decryption.
# ==============================================================================

@app.route('/api/decode', methods=['POST'])
@jwt_optional
def decode_message():
    """
    Extract a hidden message from stego text or image.

    This is the main decoding endpoint that reverses the encoding process.
    The algorithm and parameters must match what was used during encoding.

    Request Body for Text (ZWC):
        algorithm: "zwc"
        stego_text: The text containing hidden message
        password: Optional password if message was encrypted
        encoding_bits: Must match encoding setting (default 2)

    Request Body for Image (LSB):
        algorithm: "lsb"
        stego_image: Base64 encoded stego image
        password: Optional password if message was encrypted
        bits_per_pixel: Must match encoding setting (default 2)
        channel: Must match encoding setting (default 2 for blue)

    Returns:
        The extracted secret message
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No JSON data provided", 400, "INVALID_REQUEST")

        algorithm = data.get('algorithm', '').lower()
        password = data.get('password')

        # Get current user ID if authenticated
        user_id = get_current_user_id()

        # ======================================================================
        # TEXT STEGANOGRAPHY DECODING (ZWC)
        # ======================================================================
        if algorithm == 'zwc':
            stego_text = data.get('stego_text')

            if not stego_text:
                return error_response("'stego_text' is required", 400, "MISSING_FIELD")

            # Get encoding bits parameter (must match what was used for encoding)
            encoding_bits = data.get('encoding_bits', 2)

            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2", 400, "INVALID_PARAM")

            # Extract the hidden message from the text
            decoded_message = text_stego.decode_message(
                stego_text=stego_text,
                encoding_bits=encoding_bits
            )

            # Decrypt if password was provided
            if password:
                try:
                    decoded_message = security.decrypt_message(decoded_message, password)
                except ValueError as e:
                    return error_response(f"Decryption failed (wrong password?): {e}", 401, "DECRYPTION_FAILED")

            # Save to history if user is authenticated
            if user_id:
                HistoryManager.add_operation(
                    user_id=user_id,
                    operation_type='decode',
                    algorithm='zwc',
                    input_data=stego_text,
                    output_data=decoded_message,
                    is_encrypted=bool(password),
                    metadata={
                        'encoding_bits': encoding_bits,
                        'message_length': len(decoded_message)
                    }
                )

            return success_response({
                'secret_message': decoded_message,
                'algorithm': 'zwc',
                'decrypted': bool(password),
                'encoding_bits': encoding_bits,
                'message_length': len(decoded_message),
                'history_saved': bool(user_id)
            }, message="Message decoded successfully from text")

        # ======================================================================
        # IMAGE STEGANOGRAPHY DECODING (LSB)
        # ======================================================================
        elif algorithm == 'lsb':
            stego_image_b64 = data.get('stego_image')

            if not stego_image_b64:
                return error_response("'stego_image' (base64) is required", 400, "MISSING_FIELD")

            # Get parameters (must match encoding settings)
            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default to blue channel

            # Validate parameters
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3", 400, "INVALID_PARAM")

            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)", 400, "INVALID_PARAM")

            # Decode base64 image data
            stego_image_data = decode_base64_image(stego_image_b64)

            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_temp:
                stego_temp.write(stego_image_data)
                stego_temp_path = stego_temp.name

            try:
                # Extract the hidden message from the image
                decoded_message = image_stego.decode_lsb(
                    stego_image_path=stego_temp_path,
                    bits_per_pixel=bits_per_pixel,
                    channel=channel
                )

                # Decrypt if password was provided
                if password:
                    try:
                        decoded_message = security.decrypt_message(decoded_message, password)
                    except ValueError as e:
                        return error_response(f"Decryption failed (wrong password?): {e}", 401, "DECRYPTION_FAILED")

                # Save to history if user is authenticated
                if user_id:
                    HistoryManager.add_operation(
                        user_id=user_id,
                        operation_type='decode',
                        algorithm='lsb',
                        input_data='[Image]',
                        output_data=decoded_message,
                        is_encrypted=bool(password),
                        metadata={
                            'bits_per_pixel': bits_per_pixel,
                            'channel': ['red', 'green', 'blue'][channel],
                            'message_length': len(decoded_message)
                        }
                    )

                return success_response({
                    'secret_message': decoded_message,
                    'algorithm': 'lsb',
                    'decrypted': bool(password),
                    'bits_per_pixel': bits_per_pixel,
                    'channel': channel,
                    'channel_name': ['red', 'green', 'blue'][channel],
                    'message_length': len(decoded_message),
                    'history_saved': bool(user_id)
                }, message="Message decoded successfully from image")

            finally:
                # Cleanup temporary file
                safe_delete_file(stego_temp_path)

        else:
            return error_response(f"Unknown algorithm: '{algorithm}'. Use 'zwc' or 'lsb'", 400, "INVALID_ALGORITHM")

    except ValueError as e:
        return error_response(str(e), 400, "VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Decoding failed: {str(e)}", 500, "SERVER_ERROR")


# ==============================================================================
# SECTION 12: IMAGE QUALITY ANALYSIS ENDPOINT
# ==============================================================================
# Analyzes and compares original and stego images to measure quality metrics.
# ==============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze image quality metrics between original and stego images.

    This endpoint calculates quality metrics to measure how detectable
    the steganography modifications are. Lower changes mean better hiding.

    Metrics Calculated:
        MSE (Mean Squared Error): Average pixel difference, lower is better
        PSNR (Peak Signal to Noise Ratio): Higher means less visible changes
        SSIM (Structural Similarity): How similar images look, 1.0 is identical

    Request Body:
        original_image: Base64 encoded original image
        stego_image: Base64 encoded stego image

    Returns:
        Quality metrics and assessment of steganography detectability
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No JSON data provided")

        original_b64 = data.get('original_image')
        stego_b64 = data.get('stego_image')

        # Both images are required for comparison
        if not original_b64 or not stego_b64:
            return error_response("Both 'original_image' and 'stego_image' are required")

        # Decode the base64 images
        original_data = decode_base64_image(original_b64)
        stego_data = decode_base64_image(stego_b64)

        # Save to temporary files for processing
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as orig_temp:
            orig_temp.write(original_data)
            original_path = orig_temp.name

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_temp:
            stego_temp.write(stego_data)
            stego_path = stego_temp.name

        try:
            # Calculate quality metrics using our metrics module
            metrics_summary = metrics.calculate_metrics_summary(original_path, stego_path)

            return success_response({
                'metrics': metrics_summary
            }, message="Image quality analysis completed")

        finally:
            # Cleanup temporary files
            safe_delete_file(original_path)
            safe_delete_file(stego_path)

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Analysis failed: {str(e)}", 500)


# ==============================================================================
# SECTION 13: AI CHATBOT ENDPOINT
# ==============================================================================
# Provides an AI powered chatbot to help users understand steganography
# concepts and how to use the application features.
# ==============================================================================

@app.route('/api/chatbot', methods=['POST'])
@rate_limit(limit=20, window=60)  # Limit to 20 messages per minute
def chatbot():
    """
    AI chatbot endpoint for steganography questions.

    This endpoint connects to an AI model (LLaMA) to answer questions
    about steganography, encryption, and how to use this application.
    Falls back to basic responses if the AI service is unavailable.

    Request Body:
        message: The user question or message
        conversation_history: Optional list of previous messages for context

    Returns:
        AI generated response about steganography
    """
    try:
        from chatbot_ai import get_chatbot

        data = request.get_json()

        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")

        # Get and validate the user message
        user_message = data.get('message', '').strip()

        if not user_message:
            return error_response("'message' is required", 400, "MISSING_FIELD")

        # Limit message length to prevent abuse
        if len(user_message) > 500:
            return error_response("Message too long (max 500 characters)", 400, "MESSAGE_TOO_LONG")

        # Get previous conversation for context if provided
        conversation_history = data.get('conversation_history', [])

        # Get the chatbot instance
        bot = get_chatbot()

        # Generate AI response
        response = bot.chat(user_message, conversation_history)

        return success_response({
            'response': response,
            'model': 'AI-powered'
        }, message="Response generated successfully")

    except Exception as e:
        # If AI fails, return a helpful fallback response
        return success_response({
            'response': "I'm having trouble connecting right now. Please ask about: steganography basics, ZWC, LSB, encryption, or how to use this app.",
            'model': 'fallback',
            'error': str(e)
        }, message="Using fallback response")


# ==============================================================================
# SECTION 14: ADVANCED FEATURES ENDPOINTS
# ==============================================================================
# Endpoints for advanced steganography features including challenges,
# stego detection, and multi file encoding.
# ==============================================================================

# Import the advanced features modules
from features import (
    ChallengeManager,    # Practice challenges for learning
    StegoDetector,       # Detect steganography in files
    MultiFileStego       # Split secrets across multiple files
)

# Initialize the default challenges and fake leaderboard when the app starts
try:
    ChallengeManager.init_default_challenges()
    ChallengeManager.init_fake_leaderboard_users()
except:
    # Silently ignore if already initialized
    pass


# ------------------------------------------------------------------------------
# Challenge System Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    """
    Get list of steganography challenges for practice.

    Challenges help users learn steganography by solving puzzles.
    They can be filtered by difficulty level.

    Query Parameters:
        difficulty: Optional filter (easy, medium, hard)

    Returns:
        List of available challenges
    """
    try:
        difficulty = request.args.get('difficulty')
        challenges = ChallengeManager.get_challenges(difficulty)
        return success_response({'challenges': challenges})
    except Exception as e:
        return error_response(f"Failed to get challenges: {str(e)}", 500)


@app.route('/api/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """
    Get specific challenge details by ID.

    Returns the full challenge data including the stego content
    that the user needs to decode to find the answer.

    Args:
        challenge_id: The ID of the challenge to retrieve

    Returns:
        Challenge details or 404 if not found
    """
    try:
        challenge = ChallengeManager.get_challenge(challenge_id)
        if not challenge:
            return error_response("Challenge not found", 404)
        return success_response({'challenge': challenge})
    except Exception as e:
        return error_response(f"Failed to get challenge: {str(e)}", 500)


@app.route('/api/challenges/<int:challenge_id>/solve', methods=['POST'])
@jwt_optional
def solve_challenge(challenge_id):
    """
    Submit a solution to a challenge.

    Users submit their answer and receive feedback on whether
    it was correct. Points are awarded for correct answers.

    Args:
        challenge_id: The ID of the challenge to solve

    Request Body:
        solution: The user answer to check
        start_time: Optional timestamp when user started (for timing)

    Returns:
        Success status, message, and points earned
    """
    try:
        data = request.get_json()
        solution = data.get('solution', '').strip()
        start_time = data.get('start_time')

        if not solution:
            return error_response("Solution is required", 400)

        # Get user ID if authenticated (for tracking progress)
        user_id = get_current_user_id()

        # Check the solution
        success, message, points, already_solved = ChallengeManager.submit_solution(
            challenge_id, solution, user_id, start_time
        )

        return jsonify({
            'success': success,
            'message': message,
            'points': points,
            'correct': success,
            'already_solved': already_solved
        })
    except Exception as e:
        return error_response(f"Failed to submit solution: {str(e)}", 500)


# ------------------------------------------------------------------------------
# Leaderboard and Points Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get the challenge leaderboard showing top users by points.

    Query Parameters:
        limit: Number of users to return (default 10, max 50)

    Returns:
        List of top users with rank, username, points, and challenges solved
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        leaderboard = ChallengeManager.get_leaderboard(limit)
        
        return success_response({
            'leaderboard': leaderboard,
            'count': len(leaderboard)
        })
    except Exception as e:
        return error_response(f"Failed to get leaderboard: {str(e)}", 500)


@app.route('/api/points', methods=['GET'])
@jwt_required
def get_user_points():
    """
    Get current user points and challenge progress.

    Returns:
        User total points, challenges solved, rank info, and solved challenge IDs
    """
    try:
        user_id = get_current_user_id()
        
        # Get user points info
        points_info = ChallengeManager.get_user_points(user_id)
        
        # Get user rank
        rank_info = ChallengeManager.get_user_rank(user_id)
        
        # Get list of solved challenge IDs
        solved_challenges = ChallengeManager.get_user_solved_challenges(user_id)
        
        return success_response({
            'total_points': points_info['total_points'],
            'challenges_solved': points_info['challenges_solved'],
            'rank': rank_info['rank'],
            'total_participants': rank_info['total_participants'],
            'solved_challenge_ids': solved_challenges
        })
    except Exception as e:
        return error_response(f"Failed to get points: {str(e)}", 500)


# ------------------------------------------------------------------------------
# Steganography Detection Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/detect/image', methods=['POST'])
@rate_limit(limit=10, window=60)
def detect_image_stego():
    """
    Detect possible steganography in an image.

    Analyzes an image for signs of hidden data using various detection
    techniques. Returns a probability score and analysis details.

    Request Body:
        image: Base64 encoded image to analyze

    Returns:
        Analysis results with detection probability
    """
    try:
        data = request.get_json()
        image_b64 = data.get('image')

        if not image_b64:
            return error_response("Image data required", 400)

        # Decode and analyze the image
        image_data = decode_base64_image(image_b64)
        analysis = StegoDetector.analyze_image(image_data)

        return success_response({
            'analysis': analysis
        }, message="Image analyzed successfully")
    except Exception as e:
        return error_response(f"Detection failed: {str(e)}", 500)


@app.route('/api/detect/text', methods=['POST'])
@rate_limit(limit=10, window=60)
def detect_text_stego():
    """
    Detect possible steganography in text.

    Analyzes text for signs of hidden data like zero width characters.
    Returns detection results and locations of suspicious content.

    Request Body:
        text: The text to analyze

    Returns:
        Analysis results with detected steganography indicators
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return error_response("Text is required", 400)

        # Analyze the text
        analysis = StegoDetector.analyze_text(text)

        return success_response({
            'analysis': analysis
        }, message="Text analyzed successfully")
    except Exception as e:
        return error_response(f"Detection failed: {str(e)}", 500)


# ------------------------------------------------------------------------------
# Multi File Steganography Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/multi-encode', methods=['POST'])
@jwt_optional
@rate_limit(limit=5, window=60)
def multi_file_encode():
    """
    Encode a secret across multiple images.

    Splits the secret message into multiple parts and encodes each
    part into a separate image. ALL parts are needed to decode.
    This provides extra security through secret splitting.

    Request Body:
        secret_message: The message to hide
        num_parts: How many parts to split into (2 to 10)
        cover_images: Array of base64 encoded images (must have at least num_parts)

    Returns:
        Array of stego images containing the split secret
    """
    try:
        data = request.get_json()

        secret_message = data.get('secret_message')
        num_parts = data.get('num_parts', 3)
        cover_images = data.get('cover_images', [])

        if not secret_message:
            return error_response("Secret message required", 400)

        # Validate number of parts
        if num_parts < 2 or num_parts > 10:
            return error_response("Number of parts must be between 2 and 10", 400)

        # Check we have enough images
        if len(cover_images) < num_parts:
            return error_response(f"Need {num_parts} cover images", 400)

        # Split the secret into parts
        secret_parts = MultiFileStego.split_secret(secret_message, num_parts)

        # Encode each part into a separate image
        stego_images = []
        for i, (part, cover_b64) in enumerate(zip(secret_parts, cover_images[:num_parts])):
            cover_data = decode_base64_image(cover_b64)

            # Create temp files for this image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as cover_temp:
                cover_temp.write(cover_data)
                cover_temp_path = cover_temp.name

            stego_temp_path = tempfile.mktemp(suffix='.png')

            try:
                # Encode this part into the image
                image_stego.encode_lsb(cover_temp_path, part, stego_temp_path)
                stego_b64 = encode_image_to_base64(stego_temp_path)
                stego_images.append({
                    'part_number': i + 1,
                    'stego_image': stego_b64
                })
            finally:
                safe_delete_file(cover_temp_path)
                safe_delete_file(stego_temp_path)

        return success_response({
            'stego_images': stego_images,
            'total_parts': num_parts,
            'message': f'Secret split into {num_parts} parts. ALL parts needed to decode.'
        }, message="Multi-file encoding successful")
    except Exception as e:
        return error_response(f"Multi-file encoding failed: {str(e)}", 500)


@app.route('/api/multi-decode', methods=['POST'])
@jwt_optional
@rate_limit(limit=5, window=60)
def multi_file_decode():
    """
    Decode a secret from multiple images.

    Extracts parts from each stego image and combines them to
    reconstruct the original secret message.

    Request Body:
        stego_images: Array of objects with image field containing base64 data

    Returns:
        The reconstructed secret message
    """
    try:
        data = request.get_json()
        stego_images = data.get('stego_images', [])

        if len(stego_images) < 2:
            return error_response("Need at least 2 stego images", 400)

        # Decode each part from the images
        parts = []
        for img_data in stego_images:
            image_b64 = img_data.get('image')
            if not image_b64:
                continue

            image_data = decode_base64_image(image_b64)

            # Create temp file for processing
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_temp:
                stego_temp.write(image_data)
                stego_temp_path = stego_temp.name

            try:
                # Decode the part from this image
                decoded_part = image_stego.decode_lsb(stego_temp_path)
                parts.append(decoded_part)
            finally:
                safe_delete_file(stego_temp_path)

        # Combine all parts to reconstruct the secret
        secret_message = MultiFileStego.combine_secrets(parts)

        return success_response({
            'secret_message': secret_message,
            'parts_used': len(parts)
        }, message="Secret successfully reconstructed from multiple files")
    except Exception as e:
        return error_response(f"Multi-file decoding failed: {str(e)}", 500)


# ==============================================================================
# SECTION 15: ERROR HANDLERS
# ==============================================================================
# Global error handlers for common HTTP errors.
# These ensure consistent error responses across the application.
# ==============================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """
    Handle file too large error (413).

    This is triggered when a request exceeds MAX_CONTENT_LENGTH.
    """
    return error_response("File too large (max 16MB)", 413)


@app.errorhandler(404)
def not_found(error):
    """
    Handle not found error (404).

    This is triggered when a requested endpoint does not exist.
    """
    return error_response("Endpoint not found", 404)


@app.errorhandler(500)
def internal_error(error):
    """
    Handle internal server error (500).

    This is triggered when an unhandled exception occurs.
    """
    return error_response("Internal server error", 500)


# ==============================================================================
# SECTION 16: APPLICATION ENTRY POINT
# ==============================================================================
# The main entry point when running the application directly.
# This starts the Flask development server with debug mode enabled.
# ==============================================================================

if __name__ == '__main__':
    # Print startup banner
    print("=" * 70)
    print("  STEGANOGRAPHY API SERVER")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print("  GET  /ping              - Health check")
    print("  GET  /api/algorithms    - List available algorithms")
    print("  POST /api/encode        - Hide message in text/image")
    print("  POST /api/decode        - Extract hidden message")
    print("  POST /api/analyze       - Analyze image quality metrics")
    print("\n" + "=" * 70)
    print("Starting server on http://localhost:5000")
    print("=" * 70 + "\n")

    # Start the Flask development server
    # Debug mode is enabled for development (auto reload on code changes)
    # Host 0.0.0.0 allows access from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
