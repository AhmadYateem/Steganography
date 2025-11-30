# AI Chatbot Setup Guide

## Overview
Your steganography app now includes an **AI-powered chatbot** using Hugging Face's free Inference API. The chatbot can answer questions about steganography dynamically using a small language model (Phi-3 Mini).

## Features
- ✅ **Real AI responses** - Uses Microsoft Phi-3 Mini model
- ✅ **100% Free** - Hugging Face free tier (no credit card required)
- ✅ **PythonAnywhere Compatible** - No GPU needed, works on free tier
- ✅ **Conversation Memory** - Remembers last 3 exchanges
- ✅ **Fallback Responses** - Works even if API is slow/down
- ✅ **Rate Limited** - 20 messages per minute to prevent abuse
- ✅ **Beautiful UI** - Typing indicators, smooth animations

## How It Works

1. **Frontend** (`static/chatbot.js`): User types question → sent to backend
2. **Backend** (`app.py`): `/api/chatbot` endpoint receives question
3. **AI Module** (`chatbot_ai.py`): Calls Hugging Face API with context
4. **Response**: AI generates answer → sent back to user

## Setup for Local Development

Already working! Just:
```bash
python app.py
```

Then open http://localhost:5000 and click the purple chat button in the bottom-right corner.

## IMPORTANT: Get Your Free AI Token First!

**Hugging Face now requires a free API token (takes 5 minutes):**

1. Go to https://huggingface.co/join and create free account
2. Get token at https://huggingface.co/settings/tokens
3. See detailed guide in [GET_FREE_AI_TOKEN.md](GET_FREE_AI_TOKEN.md)

**Without a token:** The chatbot works but uses smart fallback responses (not real AI).
**With a token:** Real LLaMA AI generates dynamic, contextual responses.

## Setup for PythonAnywhere

### Option 1: With Hugging Face Token (Real AI - Recommended)

1. **Upload your files** to PythonAnywhere
   - Upload all files including `chatbot_ai.py`, `chatbot.js`, `chatbot.css`

2. **Install dependencies** in PythonAnywhere Bash:
   ```bash
   pip install --user huggingface_hub
   ```

3. **Configure WSGI** (use your existing `wsgi.py`):
   ```python
   import sys
   path = '/home/YOUR_USERNAME/Steganography-main'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```

4. **Reload your web app** - Done! The chatbot will use Hugging Face's free tier without a token.

### Option 2: Without Token (Fallback Mode)

The chatbot will work with intelligent keyword-based responses:

1. **Upload your files** to PythonAnywhere
2. **Install dependencies**: `pip install --user huggingface_hub`
3. **Configure WSGI** and reload

The chatbot will provide accurate steganography answers but won't be "AI-powered". It's still very capable for common questions!

## Testing the Chatbot

1. Open your app in browser
2. Click the purple chat button (bottom-right)
3. Try these questions:
   - "What is steganography?"
   - "How do I hide a message in an image?"
   - "What's the difference between LSB and ZWC?"
   - "Should I use a password?"
   - "Best practices for secure steganography?"

## Troubleshooting

### Chatbot not appearing?
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Check browser console (F12) for errors
- Verify `chatbot.js` and `chatbot.css` are loaded (Network tab)

### "I'm having trouble connecting" message?
- This means Hugging Face API is slow or unavailable
- The chatbot automatically provides fallback responses
- Try again in a few moments
- Consider adding a Hugging Face token (Option 2 above)

### On PythonAnywhere: ImportError?
- Make sure you ran: `pip install --user huggingface_hub`
- Check that `chatbot_ai.py` is uploaded
- Reload your web app

### Rate limit errors?
- You're sending too many messages (20/minute limit)
- Wait a minute and try again
- This protects your app from abuse

## Customization

### Change AI Model
Edit `chatbot_ai.py` line 28:
```python
# Fast and free options:
self.model = "microsoft/Phi-3-mini-4k-instruct"  # Current (best balance)
# or
self.model = "meta-llama/Llama-3.2-1B-Instruct"  # Faster
# or
self.model = "google/flan-t5-base"  # Smaller
```

### Adjust Response Length
Edit `chatbot_ai.py` line 64:
```python
max_tokens=300,  # Increase for longer responses (uses more quota)
```

### Modify System Context
Edit `chatbot_ai.py` lines 9-20 to change how the AI behaves.

### Change Rate Limit
Edit `app.py` line 1217:
```python
@rate_limit(limit=20, window=60)  # 20 messages per minute
```

## Cost & Limits

### Hugging Face Free Tier:
- **Cost**: $0 (completely free!)
- **Rate limit**: ~1000 requests per day per IP
- **Model size**: Small models only (Phi-3 Mini, LLaMA 3.2 1B)
- **Response time**: 2-5 seconds
- **Token limit**: Up to 300 tokens per response

This is perfect for a personal project or small app. For production with many users, consider:
- Getting a Hugging Face Pro account ($9/month) for higher limits
- Using a paid API like OpenAI (not recommended for PythonAnywhere free tier)

## Files Added

1. **`chatbot_ai.py`** - Backend AI logic using Hugging Face
2. **`static/chatbot.js`** - Frontend chatbot interface (updated)
3. **`static/chatbot.css`** - Chatbot styling (updated with animations)
4. **`app.py`** - Added `/api/chatbot` endpoint
5. **`requirements.txt`** - Added `huggingface_hub>=0.20.0`

## Security Notes

- Rate limiting prevents abuse (20 messages/minute)
- Message length limited to 500 characters
- No sensitive data sent to Hugging Face
- Conversation history kept in memory only (not logged)
- Falls back gracefully if API fails

## Support

If you have issues:
1. Check PythonAnywhere error logs
2. Verify all files are uploaded
3. Ensure `huggingface_hub` is installed
4. Try the fallback responses first (they always work)
5. Consider adding a Hugging Face token

Enjoy your AI-powered steganography chatbot! 🤖✨
