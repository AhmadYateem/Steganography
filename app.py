"""
Flask Web API for Steganography

This API provides endpoints for hiding and extracting messages using:
- Text steganography (zero-width characters)
- Image steganography (LSB)
- Encryption for secure communication
- User authentication (JWT)
- Operation history tracking

Endpoints:
    GET  /ping                - Health check
    POST /api/encode          - Hide a message in cover text/image
    POST /api/decode          - Extract hidden message
    GET  /api/algorithms      - List available algorithms
    POST /api/analyze         - Analyze image quality metrics
    
    # Authentication Endpoints
    POST /api/auth/signup     - Create new account
    POST /api/auth/login      - Login and get tokens
    POST /api/auth/refresh    - Refresh access token
    POST /api/auth/logout     - Logout and invalidate session
    GET  /api/auth/me         - Get current user info
    PUT  /api/auth/password   - Change password
    DELETE /api/auth/account  - Delete account
    
    # History Endpoints
    GET  /api/history         - Get operation history
    DELETE /api/history/:id   - Delete history item
    DELETE /api/history       - Clear all history
    GET  /api/history/stats   - Get user statistics
    
    # System Info
    GET  /api/limits          - Get system limits
"""

from flask import Flask, request, jsonify, send_file, send_from_directory, g
from flask_cors import CORS
import base64
import io
import os
import tempfile
from typing import Dict, Any
from PIL import Image

# Import our steganography modules
import text_stego
import image_stego
import security
import metrics

# Import authentication and database modules
from auth import (
    JWTManager, jwt_required, jwt_optional, get_current_user_id,
    create_auth_response, refresh_access_token, rate_limit, TokenBlacklist
)
from database import (
    UserManager, SessionManager, HistoryManager, init_database
)

# Initialize database
init_database()

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Security configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', os.urandom(32).hex())

# Enable CORS for all routes with credentials support
CORS(app, supports_credentials=True, origins=['*'])

# ============================================================================
# SYSTEM LIMITS CONFIGURATION
# ============================================================================

SYSTEM_LIMITS = {
    'max_file_size_mb': 16,
    'max_file_size_bytes': 16 * 1024 * 1024,
    'max_text_message_length': 100000,  # 100KB text
    'max_secret_message_length': 50000,  # 50KB secret
    'max_image_dimension': 4096,  # 4096x4096 pixels max
    'min_image_dimension': 10,   # 10x10 pixels min
    'supported_image_formats': ['png', 'jpg', 'jpeg', 'bmp', 'gif'],
    'max_history_items': 100,
    'rate_limits': {
        'encode': {'limit': 30, 'window': 60},  # 30 per minute
        'decode': {'limit': 30, 'window': 60},
        'auth': {'limit': 10, 'window': 60}     # 10 per minute for auth
    }
}


# ============================================================================
# SECTION 1: Utility Functions
# ============================================================================

def error_response(message: str, status_code: int = 400, code: str = None) -> tuple:
    """Create standardized error response."""
    response = {'error': message, 'success': False}
    if code:
        response['code'] = code
    return jsonify(response), status_code


def success_response(data: Dict[str, Any], message: str = None) -> tuple:
    """Create standardized success response."""
    response = {'success': True, **data}
    if message:
        response['message'] = message
    return jsonify(response), 200


def decode_base64_image(base64_string: str) -> bytes:
    """Decode base64-encoded image data."""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 image data: {e}")


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('ascii')


def validate_image_dimensions(image_data: bytes) -> tuple[bool, str, dict]:
    """Validate image dimensions and return info."""
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size
        
        if width > SYSTEM_LIMITS['max_image_dimension'] or height > SYSTEM_LIMITS['max_image_dimension']:
            return False, f"Image too large. Maximum dimension is {SYSTEM_LIMITS['max_image_dimension']}x{SYSTEM_LIMITS['max_image_dimension']} pixels", {}
        
        if width < SYSTEM_LIMITS['min_image_dimension'] or height < SYSTEM_LIMITS['min_image_dimension']:
            return False, f"Image too small. Minimum dimension is {SYSTEM_LIMITS['min_image_dimension']}x{SYSTEM_LIMITS['min_image_dimension']} pixels", {}
        
        # Calculate capacity
        capacity_bits = width * height * 3  # RGB channels
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
    """Get client IP address, considering proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


def safe_delete_file(filepath: str, max_retries: int = 5, delay: float = 0.1) -> bool:
    """
    Safely delete a file with retries for Windows file locking issues.
    
    Args:
        filepath: Path to file to delete
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        True if file was deleted or doesn't exist, False if deletion failed
    """
    import time
    import gc
    
    if not os.path.exists(filepath):
        return True
    
    for attempt in range(max_retries):
        try:
            # Force garbage collection to release file handles
            gc.collect()
            os.unlink(filepath)
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(delay)
            continue
        except Exception:
            return False
    
    return False


# ============================================================================
# SECTION 2: Frontend & Test Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the frontend application."""
    return send_from_directory('static', 'index.html')


@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check endpoint.

    Returns:
        JSON: {"status": "ok", "message": "Steganography API is running"}

    Example:
        GET /ping
        Response: {"status": "ok", "message": "Steganography API is running"}
    """
    return jsonify({
        'status': 'ok',
        'message': 'Steganography API is running',
        'version': '2.0.0',
        'features': ['text_stego', 'image_stego', 'encryption', 'jwt_auth', 'history']
    })


# ============================================================================
# SECTION 2.5: System Limits Endpoint
# ============================================================================

@app.route('/api/limits', methods=['GET'])
def get_limits():
    """
    Get system limits and capabilities.
    
    Returns:
        JSON: System limits configuration
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


# ============================================================================
# SECTION 2.6: Authentication Endpoints
# ============================================================================

@app.route('/api/auth/signup', methods=['POST'])
@rate_limit(limit=10, window=60)
def signup():
    """
    Create a new user account.
    
    Request JSON:
        {
            "username": "string (3-30 chars, alphanumeric + underscore)",
            "email": "valid email address",
            "password": "string (8+ chars, must include upper, lower, digit, special)"
        }
    
    Returns:
        JSON: User info and authentication tokens
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Create user
        success, message, user_id = UserManager.create_user(username, email, password)
        
        if not success:
            return error_response(message, 400, "SIGNUP_FAILED")
        
        # Create session
        device_info = request.headers.get('User-Agent', 'Unknown')
        refresh_token = SessionManager.create_session(user_id, device_info, get_client_ip())
        
        # Generate tokens
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
    
    Request JSON:
        {
            "username_or_email": "username or email",
            "password": "user password"
        }
    
    Returns:
        JSON: Authentication tokens and user info
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return error_response("Username/email and password are required", 400, "MISSING_FIELDS")
        
        # Authenticate
        success, message, user_data = UserManager.authenticate_user(username_or_email, password)
        
        if not success:
            return error_response(message, 401, "AUTH_FAILED")
        
        # Create session
        device_info = request.headers.get('User-Agent', 'Unknown')
        refresh_token = SessionManager.create_session(
            user_data['id'], 
            device_info, 
            get_client_ip()
        )
        
        # Generate tokens
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
    Refresh access token using refresh token.
    
    Request JSON:
        {
            "refresh_token": "refresh token string"
        }
    
    Returns:
        JSON: New access token
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400, "INVALID_REQUEST")
        
        refresh_token_str = data.get('refresh_token', '')
        
        if not refresh_token_str:
            return error_response("Refresh token is required", 400, "MISSING_TOKEN")
        
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
    Logout user and invalidate session.
    
    Request JSON (optional):
        {
            "refresh_token": "refresh token to invalidate",
            "all_sessions": false  // Set true to logout everywhere
        }
    
    Returns:
        JSON: Success message
    """
    try:
        data = request.get_json() or {}
        user_id = get_current_user_id()
        
        if data.get('all_sessions'):
            # Logout from all devices
            count = SessionManager.invalidate_all_user_sessions(user_id)
            return success_response({'sessions_invalidated': count}, f"Logged out from {count} sessions")
        
        # Logout from current session
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
    Get current authenticated user's information.
    
    Returns:
        JSON: User profile and statistics
    """
    try:
        user_id = get_current_user_id()
        user = UserManager.get_user_by_id(user_id)
        
        if not user:
            return error_response("User not found", 404, "USER_NOT_FOUND")
        
        # Get user stats
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
    Change user password.
    
    Request JSON:
        {
            "current_password": "current password",
            "new_password": "new password (must meet requirements)"
        }
    
    Returns:
        JSON: Success message
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
        
        # Optionally invalidate all other sessions
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
    
    Request JSON:
        {
            "password": "current password for confirmation"
        }
    
    Returns:
        JSON: Success message
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
    Get all active sessions for current user.
    
    Returns:
        JSON: List of active sessions
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


# ============================================================================
# SECTION 2.7: History Endpoints
# ============================================================================

@app.route('/api/history', methods=['GET'])
@jwt_required
def get_history():
    """
    Get operation history for current user.
    
    Query Parameters:
        limit: Number of items (default 50, max 100)
        offset: Pagination offset (default 0)
    
    Returns:
        JSON: List of history items
    """
    try:
        user_id = get_current_user_id()
        
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
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
    
    Returns:
        JSON: Success message
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
    Clear all history for current user.
    
    Returns:
        JSON: Number of items deleted
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
    Get user statistics.
    
    Returns:
        JSON: User statistics
    """
    try:
        user_id = get_current_user_id()
        stats = HistoryManager.get_user_stats(user_id)
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f"Failed to get stats: {str(e)}", 500, "SERVER_ERROR")


# ============================================================================
# SECTION 3: GET /api/algorithms (D2)
# ============================================================================

@app.route('/api/algorithms', methods=['GET'])
def get_algorithms():
    """
    List all available steganography algorithms.

    Returns:
        JSON: List of available algorithms with details

    Example:
        GET /api/algorithms
        Response: {
            "algorithms": {
                "text": [...],
                "image": [...]
            }
        }
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


# ============================================================================
# SECTION 4: POST /api/encode (D2)
# ============================================================================

@app.route('/api/encode', methods=['POST'])
@jwt_optional
def encode_message():
    """
    Hide a message in cover text or image.

    Request JSON (for text):
        {
            "algorithm": "zwc",
            "cover_text": "Public message here",
            "secret_message": "Hidden message",
            "password": "optional_password",
            "encoding_bits": 2,  // optional (1 or 2)
            "insertion_method": "between_words"  // optional
        }

    Request JSON (for image):
        {
            "algorithm": "lsb",
            "cover_image": "base64_encoded_image_data",
            "secret_message": "Hidden message",
            "password": "optional_password",
            "bits_per_pixel": 2,  // optional (1, 2, or 3)
            "channel": 2  // optional (0=red, 1=green, 2=blue)
        }

    Returns:
        JSON: Encoded result with stego text/image

    Example:
        POST /api/encode
        {
            "algorithm": "zwc",
            "cover_text": "Hello world",
            "secret_message": "Secret!"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No JSON data provided", 400, "INVALID_REQUEST")

        algorithm = data.get('algorithm', '').lower()
        secret_message = data.get('secret_message')
        password = data.get('password')

        if not secret_message:
            return error_response("'secret_message' is required", 400, "MISSING_FIELD")
        
        # Validate message length
        if len(secret_message) > SYSTEM_LIMITS['max_secret_message_length']:
            return error_response(
                f"Secret message too long. Maximum is {SYSTEM_LIMITS['max_secret_message_length']:,} characters",
                400, "MESSAGE_TOO_LONG"
            )

        # Get current user ID if authenticated
        user_id = get_current_user_id()

        # TEXT STEGANOGRAPHY (ZWC)
        if algorithm == 'zwc':
            cover_text = data.get('cover_text')
            if not cover_text:
                return error_response("'cover_text' is required for text steganography", 400, "MISSING_FIELD")
            
            # Validate cover text length
            if len(cover_text) > SYSTEM_LIMITS['max_text_message_length']:
                return error_response(
                    f"Cover text too long. Maximum is {SYSTEM_LIMITS['max_text_message_length']:,} characters",
                    400, "TEXT_TOO_LONG"
                )

            encoding_bits = data.get('encoding_bits', 2)
            insertion_method = data.get('insertion_method', 'between_words')

            # Validate parameters
            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2", 400, "INVALID_PARAM")

            if insertion_method not in ['append', 'between_words', 'distributed']:
                return error_response("Invalid insertion_method", 400, "INVALID_PARAM")

            # Encrypt if password provided
            message_to_hide = secret_message
            if password:
                message_to_hide = security.encrypt_message(secret_message, password)

            # Encode message
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

        # IMAGE STEGANOGRAPHY (LSB)
        elif algorithm == 'lsb':
            cover_image_b64 = data.get('cover_image')
            if not cover_image_b64:
                return error_response("'cover_image' (base64) is required for image steganography", 400, "MISSING_FIELD")

            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default: blue channel

            # Validate parameters
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3", 400, "INVALID_PARAM")

            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)", 400, "INVALID_PARAM")

            # Decode base64 image
            cover_image_data = decode_base64_image(cover_image_b64)
            
            # Validate image dimensions
            is_valid, msg, img_info = validate_image_dimensions(cover_image_data)
            if not is_valid:
                return error_response(msg, 400, "INVALID_IMAGE")

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as cover_temp:
                cover_temp.write(cover_image_data)
                cover_temp_path = cover_temp.name

            stego_temp_path = tempfile.mktemp(suffix='.png')

            try:
                # Encrypt if password provided
                message_to_hide = secret_message
                if password:
                    message_to_hide = security.encrypt_message(secret_message, password)

                # Encode message in image
                result = image_stego.encode_lsb(
                    image_path=cover_temp_path,
                    message=message_to_hide,
                    output_path=stego_temp_path,
                    bits_per_pixel=bits_per_pixel,
                    channel=channel
                )

                # Encode stego image to base64
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
                # Cleanup temporary files (with Windows file locking workaround)
                safe_delete_file(cover_temp_path)
                safe_delete_file(stego_temp_path)

        else:
            return error_response(f"Unknown algorithm: '{algorithm}'. Use 'zwc' or 'lsb'")

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Encoding failed: {str(e)}", 500)


# ============================================================================
# SECTION 5: POST /api/decode (D2)
# ============================================================================

@app.route('/api/decode', methods=['POST'])
@jwt_optional
def decode_message():
    """
    Extract hidden message from stego text or image.

    Request JSON (for text):
        {
            "algorithm": "zwc",
            "stego_text": "Text with hidden message",
            "password": "optional_password",
            "encoding_bits": 2  // optional (1 or 2)
        }

    Request JSON (for image):
        {
            "algorithm": "lsb",
            "stego_image": "base64_encoded_stego_image",
            "password": "optional_password",
            "bits_per_pixel": 2,  // optional (1, 2, or 3)
            "channel": 2  // optional (0=red, 1=green, 2=blue)
        }

    Returns:
        JSON: Decoded secret message

    Example:
        POST /api/decode
        {
            "algorithm": "zwc",
            "stego_text": "Hello​‌‍ world"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No JSON data provided", 400, "INVALID_REQUEST")

        algorithm = data.get('algorithm', '').lower()
        password = data.get('password')
        
        # Get current user ID if authenticated
        user_id = get_current_user_id()

        # TEXT STEGANOGRAPHY (ZWC)
        if algorithm == 'zwc':
            stego_text = data.get('stego_text')
            if not stego_text:
                return error_response("'stego_text' is required", 400, "MISSING_FIELD")

            encoding_bits = data.get('encoding_bits', 2)

            # Validate parameters
            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2", 400, "INVALID_PARAM")

            # Decode message
            decoded_message = text_stego.decode_message(
                stego_text=stego_text,
                encoding_bits=encoding_bits
            )

            # Decrypt if password provided
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

        # IMAGE STEGANOGRAPHY (LSB)
        elif algorithm == 'lsb':
            stego_image_b64 = data.get('stego_image')
            if not stego_image_b64:
                return error_response("'stego_image' (base64) is required", 400, "MISSING_FIELD")

            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default: blue channel

            # Validate parameters
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3", 400, "INVALID_PARAM")

            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)", 400, "INVALID_PARAM")

            # Decode base64 image
            stego_image_data = decode_base64_image(stego_image_b64)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_temp:
                stego_temp.write(stego_image_data)
                stego_temp_path = stego_temp.name

            try:
                # Decode message from image
                decoded_message = image_stego.decode_lsb(
                    stego_image_path=stego_temp_path,
                    bits_per_pixel=bits_per_pixel,
                    channel=channel
                )

                # Decrypt if password provided
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
                # Cleanup temporary file (with Windows file locking workaround)
                safe_delete_file(stego_temp_path)

        else:
            return error_response(f"Unknown algorithm: '{algorithm}'. Use 'zwc' or 'lsb'", 400, "INVALID_ALGORITHM")

    except ValueError as e:
        return error_response(str(e), 400, "VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Decoding failed: {str(e)}", 500, "SERVER_ERROR")


# ============================================================================
# SECTION 6: POST /api/analyze (D2)
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze image quality metrics (MSE, PSNR, SSIM).

    Request JSON:
        {
            "original_image": "base64_encoded_original",
            "stego_image": "base64_encoded_stego"
        }

    Returns:
        JSON: Quality metrics and assessment

    Example:
        POST /api/analyze
        {
            "original_image": "data:image/png;base64,...",
            "stego_image": "data:image/png;base64,..."
        }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No JSON data provided")

        original_b64 = data.get('original_image')
        stego_b64 = data.get('stego_image')

        if not original_b64 or not stego_b64:
            return error_response("Both 'original_image' and 'stego_image' are required")

        # Decode base64 images
        original_data = decode_base64_image(original_b64)
        stego_data = decode_base64_image(stego_b64)

        # Save to temporary files
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as orig_temp:
            orig_temp.write(original_data)
            original_path = orig_temp.name

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as stego_temp:
            stego_temp.write(stego_data)
            stego_path = stego_temp.name

        try:
            # Calculate metrics
            metrics_summary = metrics.calculate_metrics_summary(original_path, stego_path)

            return success_response({
                'metrics': metrics_summary
            }, message="Image quality analysis completed")

        finally:
            # Cleanup temporary files (with Windows file locking workaround)
            safe_delete_file(original_path)
            safe_delete_file(stego_path)

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Analysis failed: {str(e)}", 500)


# ============================================================================
# SECTION 7: Error Handlers
# ============================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return error_response("File too large (max 16MB)", 413)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return error_response("Endpoint not found", 404)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return error_response("Internal server error", 500)


# ============================================================================
# SECTION 8: Main Entry Point
# ============================================================================

if __name__ == '__main__':
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

    # Run Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
