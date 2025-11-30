# Get Free Hugging Face Token for AI Chatbot

## Why You Need This

Hugging Face requires a free API token to use their AI models (including LLaMA). **It's 100% free** - no credit card needed.

## Step-by-Step Guide (5 minutes)

### 1. Create Free Hugging Face Account

1. Go to: **https://huggingface.co/join**
2. Sign up with email (or GitHub/Google)
3. Verify your email
4. **Done!** - No payment info required

### 2. Create API Token

1. Go to: **https://huggingface.co/settings/tokens**
2. Click **"New token"**
3. Name it: `steganography-chatbot`
4. Type: Select **"Read"** (default)
5. Click **"Generate"**
6. **Copy the token** - starts with `hf_...`

### 3. Add Token to Your App

Choose ONE method:

#### Method A: Environment Variable (Recommended for Local)

**Windows:**
```bash
setx HUGGINGFACE_TOKEN "hf_your_token_here"
```

**Linux/Mac:**
```bash
export HUGGINGFACE_TOKEN="hf_your_token_here"
```

#### Method B: Direct in Code (Quick Test)

Edit `chatbot_ai.py` line 37, replace:
```python
self.api_token = api_token or os.environ.get('HUGGINGFACE_TOKEN')
```

With:
```python
self.api_token = api_token or os.environ.get('HUGGINGFACE_TOKEN') or "hf_your_token_here"
```

#### Method C: PythonAnywhere

1. Go to your PythonAnywhere Web tab
2. Scroll to **"Environment variables"** section
3. Add new variable:
   - Name: `HUGGINGFACE_TOKEN`
   - Value: `hf_your_token_here`
4. Click **"Reload"** button

### 4. Test It Works

Restart your app and ask the chatbot a question. You should see AI-generated responses now!

## What You Get (FREE Tier)

✅ **1,000 API calls per day**
✅ **Access to LLaMA 3.2 1B model**
✅ **Access to 400,000+ other models**
✅ **No credit card required**
✅ **No expiration**
✅ **Works on PythonAnywhere**

## Troubleshooting

### "Invalid token" error?
- Make sure you copied the full token (starts with `hf_`)
- Check for extra spaces
- Regenerate token if needed

### Still seeing fallback responses?
- Restart your Flask app after adding token
- Check environment variable is set: `echo %HUGGINGFACE_TOKEN%` (Windows) or `echo $HUGGINGFACE_TOKEN` (Linux/Mac)
- Verify token at: https://huggingface.co/settings/tokens

### Rate limit errors?
- Free tier: 1,000 calls/day per token
- That's plenty for personal use!
- Upgrade to Pro ($9/month) for unlimited calls if needed

## Without Token?

The chatbot will still work using **intelligent fallback responses** based on keywords. It won't be "AI-powered" but will still answer most steganography questions accurately.

If you want **real AI responses that can understand context and generate dynamic answers**, you need the token (5 min setup, totally free).

## Security Note

⚠️ **Never commit your token to GitHub!**
- Use environment variables
- Add `.env` to `.gitignore`
- On PythonAnywhere, use their environment variables feature

Your token gives read-only access to public models - it's safe, but keep it private like any API key.

---

**Need help?** Visit: https://huggingface.co/docs/hub/security-tokens
