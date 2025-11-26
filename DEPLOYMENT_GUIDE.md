# 🚀 PythonAnywhere Deployment Guide

## Step-by-Step Instructions to Deploy Your Steganography App for FREE Forever

### Prerequisites
- Your project files ready
- A free PythonAnywhere account

---

## 📋 Step 1: Sign Up for PythonAnywhere

1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing & signup"**
3. Choose **"Create a Beginner account"** (100% FREE - no credit card needed)
4. Fill in:
   - Username (this will be in your URL: `username.pythonanywhere.com`)
   - Email
   - Password
5. Verify your email

---

## 📁 Step 2: Connect GitHub (RECOMMENDED - Auto-updates!)

### Option A: Using GitHub (Best - Auto-sync on push!)

1. **First, push your code to GitHub:**
   - Create a new repository on GitHub
   - In your local project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/steganography-app.git
   git push -u origin main
   ```

2. **Clone in PythonAnywhere:**
   - Log in to PythonAnywhere
   - Go to **"Consoles"** tab
   - Start a **"Bash console"**
   - Run:
   ```bash
   git clone https://github.com/yourusername/steganography-app.git
   cd steganography-app
   ```

3. **To update later (automatically pull changes):**
   - After pushing to GitHub, open Bash console
   - Run:
   ```bash
   cd steganography-app
   git pull
   ```
   - Go to Web tab → Click **"Reload"**
   - Your changes are live!

### Option B: Using the Web Interface (Manual uploads)

1. Log in to PythonAnywhere
2. Go to **"Files"** tab (top menu)
3. Click **"Upload a file"**
4. Upload these files one by one:
   - `app.py`
   - `text_stego.py`
   - `image_stego.py`
   - `security.py`
   - `metrics.py`
   - `crypto.py`
   - `requirements.txt`
5. Create a folder called `static` (click "New directory")
6. Go into the `static` folder
7. Upload `index.html`

**Note:** With GitHub (Option A), you just `git push` locally and `git pull` on PythonAnywhere - much easier!

---

## 🐍 Step 3: Install Dependencies

1. Go to **"Consoles"** tab
2. Start a new **"Bash console"**
3. Run:
```bash
pip3.10 install --user flask flask-cors cryptography pillow numpy scikit-image
```
4. Wait for installation to complete (2-3 minutes)

---

## 🌐 Step 4: Create Web App

1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Click **"Next"** (accept the domain name `yourusername.pythonanywhere.com`)
4. Select **"Flask"**
5. Select **"Python 3.10"**
6. For "Path to Flask app", enter: `/home/yourusername/app.py`
   (Replace `yourusername` with your actual username)
7. Click **"Next"**

---

## ⚙️ Step 5: Configure WSGI File

1. Still in the **"Web"** tab
2. Find the section **"Code"**
3. Click on the **WSGI configuration file** link (something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
4. Delete all the content
5. Paste this:

```python
import sys
import os

# Add your project directory to the sys.path
# If using GitHub: change to /home/yourusername/steganography-app
# If manual upload: use /home/yourusername
project_home = '/home/yourusername/steganography-app'  # ← CHANGE THIS
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import Flask app
from app import app as application
```

6. **IMPORTANT:** 
   - Change `yourusername` to your actual PythonAnywhere username
   - If you used GitHub, keep `/steganography-app` (or your repo name)
   - If you uploaded manually, remove `/steganography-app`
7. Click **"Save"** (top right)

---

## 🔧 Step 6: Configure Static Files

1. Still in the **"Web"** tab
2. Scroll to **"Static files"** section
3. Click **"Enter URL"** and type: `/static/`
4. Click **"Enter path"** and type:
   - If using GitHub: `/home/yourusername/steganography-app/static`
   - If manual upload: `/home/yourusername/static`
   (Replace `yourusername` with your actual username)
5. Click the green checkmark ✓

---

## 🎯 Step 7: Set Working Directory

1. In the **"Web"** tab
2. Find **"Working directory"**
3. Set it to:
   - If using GitHub: `/home/yourusername/steganography-app`
   - If manual upload: `/home/yourusername`
   (Replace `yourusername` with your actual username)

---

## 🚀 Step 8: Reload and Launch

1. Scroll to the top of the **"Web"** tab
2. Click the big green **"Reload"** button
3. Wait 10-20 seconds
4. Click on your site URL: **`yourusername.pythonanywhere.com`**
5. **Your app is now LIVE! 🎉**

---

## 🔍 Troubleshooting

### Error: "Something went wrong"
1. Go to **"Web"** tab
2. Click **"Error log"** (near the bottom)
3. Check for error messages
4. Common fixes:
   - Make sure all files are uploaded
   - Check WSGI file has correct username
   - Verify all dependencies are installed

### Error: "Import Error"
1. Go to **"Consoles"** → **"Bash"**
2. Run: `pip3.10 install --user flask flask-cors cryptography pillow numpy scikit-image`
3. Reload the web app

### API Not Working
1. Check that your `app.py` doesn't have `if __name__ == '__main__':` causing issues
2. Make sure CORS is enabled in app.py (it already is)
3. In your HTML, change API_BASE to point to your PythonAnywhere domain

---

## 📝 Important Notes

- **Free tier limitations:**
  - App runs 24/7
  - 512 MB storage
  - Your domain: `yourusername.pythonanywhere.com`
  - No custom domain on free tier

- **To update your app:**
  - **With GitHub (recommended):**
    1. Make changes locally
    2. `git add .` → `git commit -m "message"` → `git push`
    3. In PythonAnywhere Bash: `cd steganography-app` → `git pull`
    4. Click "Reload" in Web tab
  - **Manual method:**
    1. Upload new files via "Files" tab
    2. Click "Reload" in Web tab

- **To view logs:**
  - "Web" tab → "Error log" or "Server log"

---

## 🎉 You're Done!

Your steganography app is now deployed and accessible worldwide at:
**`https://yourusername.pythonanywhere.com`**

Share this URL with anyone - your app will stay online forever on the free tier!

---

## 🔗 Useful Links

- PythonAnywhere Dashboard: https://www.pythonanywhere.com/dashboard
- PythonAnywhere Help: https://help.pythonanywhere.com
- Flask Documentation: https://flask.palletsprojects.com

---

**Need help?** Check the error logs or PythonAnywhere forums!
