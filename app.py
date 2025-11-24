"""
Flask Web API for Steganography

This API provides endpoints for hiding and extracting messages using:
- Text steganography (zero-width characters)
- Image steganography (LSB)
- Encryption for secure communication

Endpoints:
    GET  /ping                - Health check
    POST /api/encode          - Hide a message in cover text/image
    POST /api/decode          - Extract hidden message
    GET  /api/algorithms      - List available algorithms
    POST /api/analyze         - Analyze image quality metrics
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import base64
import io
import os
import tempfile
from typing import Dict, Any

# Import our steganography modules
import text_stego
import image_stego
import security
import metrics

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app)


# ============================================================================
# SECTION 1: Utility Functions
# ============================================================================

def error_response(message: str, status_code: int = 400) -> tuple:
    """Create standardized error response."""
    return jsonify({'error': message, 'success': False}), status_code


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
        'version': '1.0.0'
    })


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
            return error_response("No JSON data provided")

        algorithm = data.get('algorithm', '').lower()
        secret_message = data.get('secret_message')
        password = data.get('password')

        if not secret_message:
            return error_response("'secret_message' is required")

        # TEXT STEGANOGRAPHY (ZWC)
        if algorithm == 'zwc':
            cover_text = data.get('cover_text')
            if not cover_text:
                return error_response("'cover_text' is required for text steganography")

            encoding_bits = data.get('encoding_bits', 2)
            insertion_method = data.get('insertion_method', 'between_words')

            # Validate parameters
            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2")

            if insertion_method not in ['append', 'between_words', 'distributed']:
                return error_response("Invalid insertion_method")

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

            return success_response({
                'stego_text': stego_text,
                'algorithm': 'zwc',
                'encrypted': bool(password),
                'encoding_bits': encoding_bits,
                'insertion_method': insertion_method,
                'cover_length': len(cover_text),
                'stego_length': len(stego_text),
                'message_length': len(secret_message)
            }, message="Message encoded successfully in text")

        # IMAGE STEGANOGRAPHY (LSB)
        elif algorithm == 'lsb':
            cover_image_b64 = data.get('cover_image')
            if not cover_image_b64:
                return error_response("'cover_image' (base64) is required for image steganography")

            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default: blue channel

            # Validate parameters
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3")

            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)")

            # Decrypt base64 image
            cover_image_data = decode_base64_image(cover_image_b64)

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

                return success_response({
                    'stego_image': stego_image_b64,
                    'algorithm': 'lsb',
                    'encrypted': bool(password),
                    'bits_per_pixel': bits_per_pixel,
                    'channel': channel,
                    'channel_name': ['red', 'green', 'blue'][channel],
                    'pixels_modified': result['pixels_modified'],
                    'capacity_used_percent': result['capacity_used_percent'],
                    'message_length': len(secret_message)
                }, message="Message encoded successfully in image")

            finally:
                # Cleanup temporary files
                if os.path.exists(cover_temp_path):
                    os.unlink(cover_temp_path)
                if os.path.exists(stego_temp_path):
                    os.unlink(stego_temp_path)

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
            return error_response("No JSON data provided")

        algorithm = data.get('algorithm', '').lower()
        password = data.get('password')

        # TEXT STEGANOGRAPHY (ZWC)
        if algorithm == 'zwc':
            stego_text = data.get('stego_text')
            if not stego_text:
                return error_response("'stego_text' is required")

            encoding_bits = data.get('encoding_bits', 2)

            # Validate parameters
            if encoding_bits not in [1, 2]:
                return error_response("'encoding_bits' must be 1 or 2")

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
                    return error_response(f"Decryption failed (wrong password?): {e}", 401)

            return success_response({
                'secret_message': decoded_message,
                'algorithm': 'zwc',
                'decrypted': bool(password),
                'encoding_bits': encoding_bits,
                'message_length': len(decoded_message)
            }, message="Message decoded successfully from text")

        # IMAGE STEGANOGRAPHY (LSB)
        elif algorithm == 'lsb':
            stego_image_b64 = data.get('stego_image')
            if not stego_image_b64:
                return error_response("'stego_image' (base64) is required")

            bits_per_pixel = data.get('bits_per_pixel', 2)
            channel = data.get('channel', 2)  # Default: blue channel

            # Validate parameters
            if bits_per_pixel not in [1, 2, 3]:
                return error_response("'bits_per_pixel' must be 1, 2, or 3")

            if channel not in [0, 1, 2]:
                return error_response("'channel' must be 0 (red), 1 (green), or 2 (blue)")

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
                        return error_response(f"Decryption failed (wrong password?): {e}", 401)

                return success_response({
                    'secret_message': decoded_message,
                    'algorithm': 'lsb',
                    'decrypted': bool(password),
                    'bits_per_pixel': bits_per_pixel,
                    'channel': channel,
                    'channel_name': ['red', 'green', 'blue'][channel],
                    'message_length': len(decoded_message)
                }, message="Message decoded successfully from image")

            finally:
                # Cleanup temporary file
                if os.path.exists(stego_temp_path):
                    os.unlink(stego_temp_path)

        else:
            return error_response(f"Unknown algorithm: '{algorithm}'. Use 'zwc' or 'lsb'")

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Decoding failed: {str(e)}", 500)


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
            # Cleanup temporary files
            if os.path.exists(original_path):
                os.unlink(original_path)
            if os.path.exists(stego_path):
                os.unlink(stego_path)

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
