"""
AI Chatbot for Steganography using Hugging Face Inference API
Uses LLaMA 3.2 - requires free HF token
"""

import os
from huggingface_hub import InferenceClient

# Steganography context to guide the AI
SYSTEM_CONTEXT = """You are a helpful assistant specialized in steganography. Help users understand steganography techniques.

Key topics:
- Steganography: hiding secret messages in text or images
- ZWC (Zero-Width Characters): using invisible Unicode characters
- LSB (Least Significant Bit): hiding data in image pixels
- Encryption with AES-256
- Image quality metrics: PSNR, MSE, SSIM
- Best practices

Keep answers concise (2-3 sentences) and focused on steganography."""


class SteganographyChatbot:
    def __init__(self, api_token=None):
        """
        Initialize chatbot with Hugging Face API.

        Args:
            api_token: Hugging Face API token (required)
        """
        self.api_token = api_token or os.environ.get('HUGGINGFACE_TOKEN')
        
        if not self.api_token:
            raise ValueError("HUGGINGFACE_TOKEN environment variable is required. Get a free token at https://huggingface.co/settings/tokens")

        # Initialize client with token
        self.client = InferenceClient(token=self.api_token)

        # Use LLaMA 3.2 1B - fast and accurate
        self.model = "meta-llama/Llama-3.2-1B-Instruct"

    def chat(self, user_message, conversation_history=None):
        """
        Get AI response to user message.

        Args:
            user_message: User's question
            conversation_history: List of previous messages (optional)

        Returns:
            AI response string
        """
        try:
            # Build messages with system context
            messages = [
                {"role": "system", "content": SYSTEM_CONTEXT}
            ]

            # Add conversation history if provided (last 3 exchanges)
            if conversation_history:
                messages.extend(conversation_history[-6:])

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get AI response
            response = self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=250,  # Keep responses concise
                temperature=0.7,
                top_p=0.9,
            )

            # Extract and return response text
            bot_reply = response.choices[0].message.content
            return bot_reply.strip()

        except Exception as e:
            print(f"AI API Error: {e}")
            # Use fallback response
            return self._fallback_response(user_message)

    def _fallback_response(self, user_message):
        """
        Provide fallback response if API fails.
        """
        msg_lower = user_message.lower()

        # Comprehensive keyword-based responses
        if any(word in msg_lower for word in ['what is', 'define', 'explain', 'tell me about']) and 'steganography' in msg_lower:
            return "Steganography is the practice of hiding secret messages within non-secret text or images. Unlike encryption which scrambles data, steganography conceals the existence of the message itself. This app supports text steganography using Zero-Width Characters (ZWC) and image steganography using Least Significant Bit (LSB) technique."

        elif 'zwc' in msg_lower or 'zero width' in msg_lower or 'zero-width' in msg_lower:
            return "ZWC (Zero-Width Characters) is a text steganography technique that uses invisible Unicode characters like Zero-Width Space (U+200B) and Zero-Width Joiner (U+200D) to encode secret messages. These characters are invisible to humans but can be decoded by software. You can adjust encoding bits (1-2) and insertion method (append, between_words, or distributed) for different security levels."

        elif 'lsb' in msg_lower or 'least significant' in msg_lower or 'image steg' in msg_lower:
            return "LSB (Least Significant Bit) is an image steganography technique that hides data by modifying the least significant bits of pixel color values. Since these are the least important bits, changes are imperceptible to the human eye. You can use 1-3 bits per pixel - lower values are more invisible, higher values provide more capacity. Always use PNG format as JPG compression destroys hidden data."

        elif any(word in msg_lower for word in ['password', 'encrypt', 'secure', 'aes']):
            return "Using a password encrypts your secret message with AES-256 encryption before hiding it. This provides two layers of security: steganography (hiding the message) and cryptography (encrypting it). Even if someone detects the hidden message, they cannot read it without the correct password. Always use strong passwords with mixed characters for maximum security."

        elif any(word in msg_lower for word in ['how to', 'how do', 'steps', 'use', 'hide message', 'encode']):
            return "To hide a message: 1) Choose algorithm - ZWC for text steganography or LSB for image steganography. 2) Provide cover medium - text for ZWC or upload image for LSB. 3) Enter your secret message. 4) Optional: Add a password for encryption. 5) Configure settings like bits per pixel or insertion method. 6) Click Encode. To extract: use the same algorithm, parameters, and password you used for encoding."

        elif 'decode' in msg_lower or 'extract' in msg_lower or 'reveal' in msg_lower:
            return "To decode/extract a hidden message: 1) Select the same algorithm used for encoding (ZWC or LSB). 2) Provide the stego medium (text with hidden message or stego image). 3) Enter the password if one was used. 4) Use the same parameters (encoding bits, bits per pixel, channel). 5) Click Decode. The secret message will be revealed. If decryption fails, check that you're using the correct password and parameters."

        elif 'best practice' in msg_lower or 'tips' in msg_lower or 'recommendation' in msg_lower:
            return "Best practices for secure steganography: 1) Always use encryption (add a password). 2) Use PNG images, never JPG. 3) Use 1-2 bits per pixel for invisibility. 4) Use distributed or between_words insertion for text. 5) Don't reuse cover media. 6) Don't fill entire capacity. 7) Verify quality with Analyze feature (PSNR > 40 dB is good). 8) Keep original files secure. 9) Use strong passwords. 10) Test decode before sharing."

        elif 'psnr' in msg_lower or 'mse' in msg_lower or 'ssim' in msg_lower or 'quality' in msg_lower or 'metric' in msg_lower:
            return "Quality metrics measure steganography invisibility: PSNR (Peak Signal-to-Noise Ratio) - higher is better, >40 dB means imperceptible changes. MSE (Mean Squared Error) - lower is better, near 0 means no visible difference. SSIM (Structural Similarity Index) - 0 to 1 scale, >0.95 means excellent quality. Use the Analyze feature to check if your stego image looks identical to the original."

        elif 'capacity' in msg_lower or 'how much' in msg_lower or 'size limit' in msg_lower:
            return "Image capacity depends on dimensions and bits per pixel. Formula: capacity = width × height × 3 (RGB) × bits_per_pixel / 8. Example: a 1920×1080 image with 2 bits per pixel can hide about 1.5 MB. For text steganography, capacity depends on cover text length and encoding bits. The app shows capacity estimates when you select an image or enter text."

        elif 'detect' in msg_lower or 'steganalysis' in msg_lower or 'caught' in msg_lower:
            return "Steganography can be detected by statistical analysis tools (steganalysis). To minimize detection: 1) Use encryption always. 2) Use low bits per pixel (1-2). 3) Don't fill entire capacity - use only 50-70%. 4) Use high-quality cover images with natural noise. 5) Use distributed insertion for text. 6) Avoid patterns. 7) Don't reuse cover media. Perfect steganography is theoretically undetectable if done correctly."

        elif 'python' in msg_lower and 'anywhere' in msg_lower:
            return "This app is fully compatible with PythonAnywhere! It uses SQLite (built-in), standard Python libraries, and has no special requirements. Just upload your files, install requirements with 'pip install --user -r requirements.txt', configure your WSGI file, and add your HUGGINGFACE_TOKEN environment variable. Then reload your web app."

        elif 'error' in msg_lower or 'problem' in msg_lower or 'not work' in msg_lower or 'fail' in msg_lower:
            return "Common issues: 1) Message too long - use larger cover image or compress message. 2) Wrong password - passwords are case-sensitive, must match exactly. 3) JPG corruption - use PNG format only. 4) Parameter mismatch - use same bits, channel, and method for decode. 5) Image too small - check capacity before encoding. 6) File size limit - max 16 MB per file. Check error messages for specific guidance."

        elif any(word in msg_lower for word in ['hello', 'hi', 'hey', 'greet']):
            return "Hello! I'm your AI steganography assistant powered by LLaMA 3.2. I can help you understand and use steganography techniques. Ask me about ZWC, LSB, encryption, best practices, or how to use this app!"

        elif any(word in msg_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! Feel free to ask if you have more questions about steganography, hiding messages, or using this app."

        elif any(word in msg_lower for word in ['help', 'what can you', 'capabilities']):
            return "I can help you with: Understanding steganography concepts (ZWC, LSB), Learning how to hide and extract messages, Choosing the right settings (bits per pixel, encoding method), Security and encryption advice, Quality metrics (PSNR, MSE, SSIM), Best practices for secure steganography, Troubleshooting issues, PythonAnywhere deployment. Just ask your question!"

        else:
            return "I'm an AI assistant specialized in steganography. I can explain how to hide messages in text (ZWC) or images (LSB), discuss encryption and security, help with quality metrics, and provide best practices. What would you like to know about steganography?"


# Global chatbot instance
_chatbot_instance = None

def get_chatbot():
    """Get or create chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = SteganographyChatbot()
    return _chatbot_instance
