# Steganography Pro - Deployment Checklist

## ✅ Files Ready for PythonAnywhere Deployment

### Core Files
- [x] app.py - Main Flask application
- [x] text_stego.py - Text steganography module
- [x] image_stego.py - Image steganography module  
- [x] security.py - Encryption module
- [x] metrics.py - Quality metrics module
- [x] crypto.py - Cryptography utilities
- [x] requirements.txt - Python dependencies
- [x] wsgi.py - WSGI configuration for PythonAnywhere
- [x] setup_pythonanywhere.sh - Installation script

### Frontend Files
- [x] static/index.html - Main web interface (with auto API detection)

### Documentation
- [x] DEPLOYMENT_GUIDE.md - Step-by-step deployment instructions
- [x] README.md - Project documentation

---

## 🚀 Quick Deployment Steps

### 1. Create PythonAnywhere Account
- Go to https://www.pythonanywhere.com
- Sign up for FREE Beginner account
- Choose a username (becomes your URL)

### 2. Upload Files
Upload these files to PythonAnywhere:
```
/home/yourusername/
├── app.py
├── text_stego.py
├── image_stego.py
├── security.py
├── metrics.py
├── crypto.py
├── requirements.txt
└── static/
    └── index.html
```

### 3. Install Dependencies
In Bash console:
```bash
pip3.10 install --user flask flask-cors cryptography pillow numpy scikit-image
```

### 4. Create Web App
- Web tab → Add new web app
- Choose Flask + Python 3.10
- Path: `/home/yourusername/app.py`

### 5. Configure WSGI
Edit WSGI file with content from `wsgi.py`
(Replace `yourusername` with your actual username)

### 6. Set Static Files
- URL: `/static/`
- Path: `/home/yourusername/static`

### 7. Reload & Launch
- Click green "Reload" button
- Visit: `yourusername.pythonanywhere.com`

---

## 🎯 What's Been Prepared

✅ **API endpoint automatically adjusts** - Works on localhost AND PythonAnywhere
✅ **All dependencies listed** in requirements.txt
✅ **WSGI configuration ready** - Just change username
✅ **Complete deployment guide** - Step-by-step with screenshots
✅ **Static files configured** - Frontend will load properly
✅ **CORS enabled** - API accessible from frontend

---

## 📝 Important Configuration Changes Made

### 1. index.html - Smart API Detection
Changed from:
```javascript
const API_BASE = 'http://localhost:5000/api';
```

To:
```javascript
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api' 
    : `${window.location.protocol}//${window.location.host}/api`;
```

This automatically uses the correct URL whether you're testing locally or deployed.

---

## 🌐 Your Live URL

After deployment: `https://yourusername.pythonanywhere.com`

Replace `yourusername` with your actual PythonAnywhere username.

---

## 💡 Tips

- **Testing locally**: Just run `python app.py` - works as before
- **After deployment**: Any file changes require clicking "Reload" in Web tab
- **Viewing errors**: Web tab → Error log
- **Free forever**: No credit card, no expiration, 24/7 uptime

---

## 🆘 Need Help?

1. Read `DEPLOYMENT_GUIDE.md` for detailed instructions
2. Check PythonAnywhere error logs
3. Visit: https://help.pythonanywhere.com

---

## ✨ You're All Set!

Everything is ready for deployment. Just follow the steps in `DEPLOYMENT_GUIDE.md` and your app will be live in 10-15 minutes!
