# SteganographyPro - Complete Features Documentation

A comprehensive guide to every single feature, method, and capability in the SteganographyPro application.

---

## Table of Contents

1. [Steganography Methods](#1-steganography-methods)
2. [Encryption and Cryptography](#2-encryption-and-cryptography)
3. [Password Security](#3-password-security)
4. [Authentication System](#4-authentication-system)
5. [Rate Limiting and Protection](#5-rate-limiting-and-protection)
6. [Challenge and Gamification System](#6-challenge-and-gamification-system)
7. [Leaderboard and Points System](#7-leaderboard-and-points-system)
8. [Burn After Reading](#8-burn-after-reading)
9. [Detection and Scanner Features](#9-detection-and-scanner-features)
10. [AI Chatbot Assistant](#10-ai-chatbot-assistant)
11. [Image Quality Metrics](#11-image-quality-metrics)
12. [Multi-File Steganography](#12-multi-file-steganography)
13. [User Interface Features](#13-user-interface-features)
14. [Dark Mode and Theming](#14-dark-mode-and-theming)
15. [Database Structure](#15-database-structure)
16. [API Endpoints](#16-api-endpoints)
17. [System Configuration](#17-system-configuration)
18. [Unique and Creative Features](#18-unique-and-creative-features)

---

## 1. Steganography Methods

### 1.1 Text Steganography (Zero Width Characters)

The application uses invisible Unicode characters to hide secret messages inside normal text. These characters are completely invisible to the human eye but can be detected by the system.

**Zero Width Characters Used:**
| Character | Unicode | Binary Representation |
|-----------|---------|----------------------|
| Zero Width Non-Joiner | U+200C | Binary 0 |
| Zero Width Joiner | U+200D | Binary 1 |
| Zero Width Space | U+200B | Binary 00 |
| Zero Width No-Break Space | U+FEFF | Binary 11 |

**Encoding Modes:**
- **1-bit encoding:** Uses 2 ZWC characters to represent binary 0 and 1. Simple but uses more space.
- **2-bit encoding:** Uses 4 ZWC characters to represent 00, 01, 10, and 11. More compact and efficient.

**Insertion Methods:**
- **End of text:** All zero width characters are placed at the end of the cover text
- **Between words:** Characters are distributed in the spaces between words
- **Distributed:** Characters are spread evenly throughout the entire text

**Technical Process:**
1. Convert secret message to binary
2. Map binary to zero width characters based on encoding mode
3. Insert characters into cover text based on insertion method
4. Original text appears unchanged but contains hidden data

### 1.2 Image Steganography (LSB - Least Significant Bit)

The application hides data in images by modifying the least significant bits of pixel color values. This method is nearly invisible to the human eye.

**How It Works:**
- Each pixel has RGB color values (0-255)
- The least significant bits are modified to store secret data
- Human eyes cannot detect these tiny changes

**Bits Per Pixel Options:**
| Setting | Capacity | Visibility | Use Case |
|---------|----------|------------|----------|
| 1 bit | Low | Most invisible | Maximum security |
| 2 bits | Medium | Very low visibility | Balanced approach |
| 3 bits | High | Slightly visible | Maximum capacity |

**Color Channel Selection:**
- Red channel (channel 0)
- Green channel (channel 1)
- Blue channel (channel 2) - default choice

**Supported Image Formats:**
- PNG (recommended)
- BMP
- TIFF
- JPEG (automatically converted to PNG for output to preserve data)

**Capacity Calculation:**
```
Maximum bytes = (width x height x bits_per_pixel) / 8
```

**Header System:**
A 32-bit header is stored at the beginning containing the message length so the decoder knows how much data to extract.

---

## 2. Encryption and Cryptography

### 2.1 AES Encryption

All sensitive data can be encrypted before being hidden using industry-standard AES encryption.

**Algorithm Details:**
- **Type:** Fernet encryption (built on AES-128-CBC)
- **Authentication:** HMAC-SHA256 for integrity verification
- **IV (Initialization Vector):** Random IV generated for each encryption
- **Padding:** PKCS7 padding

**Key Derivation Process:**
1. User password is taken as input
2. SHA-256 hash is computed from the password
3. Hash is base64 encoded to create a Fernet-compatible key
4. This key is used for AES encryption

**Security Features:**
- Each encryption uses a unique random IV
- HMAC prevents tampering with encrypted data
- Timestamp included for optional token expiration

### 2.2 Dual Layer Security

The application supports combining steganography with encryption for maximum security:
1. First layer: Secret message is encrypted with AES
2. Second layer: Encrypted data is hidden using steganography

This means even if someone extracts the hidden data, they cannot read it without the password.

---

## 3. Password Security

### 3.1 Password Hashing

User passwords are never stored in plain text. They are securely hashed using industry-standard methods.

**Hashing Algorithm:**
- **Method:** PBKDF2-HMAC-SHA256
- **Iterations:** 100,000 rounds (slows down brute force attacks)
- **Salt:** 32-byte cryptographically secure random salt
- **Salt Storage:** Unique salt stored per user

**Why This Is Secure:**
- 100,000 iterations makes password cracking extremely slow
- Unique salt per user prevents rainbow table attacks
- SHA-256 provides strong cryptographic security

### 3.2 Password Requirements

When creating an account, passwords must meet these requirements:
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

### 3.3 Password Strength Checker

The application includes a 7-point scoring system to evaluate password strength:
1. Length score (longer is better)
2. Uppercase letters present
3. Lowercase letters present
4. Numbers present
5. Special characters present
6. No common patterns
7. Mixed character types

### 3.4 Random Password Generator

A built-in tool generates cryptographically secure random passwords that meet all requirements.

---

## 4. Authentication System

### 4.1 JWT (JSON Web Token) Authentication

The application uses JWT tokens for secure, stateless authentication.

**Token Types:**

| Token Type | Expiry Time | Purpose |
|------------|-------------|---------|
| Access Token | 15 minutes | Used for API access |
| Refresh Token | 30 days | Used to get new access tokens |

**Token Structure (Claims):**
- `sub`: Subject (user ID)
- `user_id`: User database ID
- `username`: User's display name
- `email`: User's email address
- `type`: Token type (access or refresh)
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp
- `jti`: Unique token identifier

**Algorithm:** HS256 (HMAC with SHA-256)

### 4.2 Token Blacklist

When users log out, their tokens are added to a blacklist to prevent reuse. This provides immediate token invalidation.

### 4.3 Account Lockout Protection

To prevent brute force attacks:
- After 5 failed login attempts, account is locked
- Lockout duration: 15 minutes
- Failed attempt counter resets after successful login

### 4.4 Session Management

The system tracks active sessions with:
- Device information
- IP address
- Creation time
- Expiration time
- Users can view all active sessions
- Users can log out from specific sessions or all sessions

---

## 5. Rate Limiting and Protection

### 5.1 Request Rate Limits

Different endpoints have different rate limits to prevent abuse:

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Encode/Decode | 30 requests | per minute |
| Authentication | 10 requests | per minute |
| Chatbot | 20 messages | per minute |
| Detection/Scanner | 10 scans | per minute |
| Multi-file operations | 5 requests | per minute |

### 5.2 How Rate Limiting Works

- Requests are tracked by IP address and endpoint
- In-memory storage for fast lookup
- Automatic cleanup of old entries
- Returns 429 (Too Many Requests) when limit exceeded

---

## 6. Challenge and Gamification System

### 6.1 Challenge Types

The application includes educational challenges to teach steganography:

| Type | Description | Example |
|------|-------------|---------|
| Puzzle | Knowledge questions | "What does LSB stand for?" |
| ZWC | Text steganography decode | Extract hidden message from text |
| LSB | Image steganography decode | Extract hidden message from image |

### 6.2 Difficulty Levels

| Level | Points | Description |
|-------|--------|-------------|
| Easy | 50 points | Basic concepts and definitions |
| Medium | 100 points | Calculations and historical knowledge |
| Hard | 200 points | Advanced topics and complex problems |

### 6.3 Default Challenges Include

- Etymology of the word "steganography"
- LSB (Least Significant Bit) abbreviation meaning
- ZWC (Zero Width Character) abbreviation meaning
- Historical figures in steganography (Trithemius, Herodotus)
- Capacity calculation problems
- Quality metrics understanding (PSNR)
- File format knowledge (PNG vs JPEG)
- Encryption mode knowledge (CBC-128)

### 6.4 Challenge Features

- **Hints system:** Multiple hints available per challenge
- **Solve tracking:** Count of how many users solved each challenge
- **Time tracking:** How long it took to solve
- **One-time points:** Points only awarded once per user per challenge

---

## 7. Leaderboard and Points System

### 7.1 Points System

- Points are earned by solving challenges
- Points are tied to user accounts
- Each challenge can only award points once per user (prevents farming)
- Points accumulate over time

### 7.2 Leaderboard Features

- Shows top 10 users by total points
- Displays username, rank, and total points
- Shows number of challenges solved
- Updates in real-time after solving challenges

### 7.3 User Stats Display

When logged in, users see:
- Total points earned
- Number of challenges solved
- Current rank on leaderboard

---

## 8. Burn After Reading

### 8.1 Self-Destructing Messages

Create messages that automatically delete after being viewed.

**Configuration Options:**
- **Max views:** 1 to 100 views before deletion
- **Expiry time:** 1 to 720 hours (30 days maximum)

**How It Works:**
1. Create a message with steganography
2. Set view limit and/or expiry time
3. Receive a unique URL
4. Share the URL
5. Message is deleted after view limit reached or time expires

### 8.2 Technical Details

- Unique 32-byte URL-safe token for each message
- Uses ZWC steganography by default
- Automatic cleanup of expired messages
- View count tracked in database

---

## 9. Detection and Scanner Features

### 9.1 Image Steganalysis

Analyze images to detect if they might contain hidden data.

**Detection Techniques:**

| Technique | What It Detects |
|-----------|-----------------|
| LSB Randomness Analysis | Distribution uniformity of least significant bits |
| Chi-Square Testing | Statistical anomalies in pixel values |
| Entropy Measurement | Presence of random encrypted data |
| Bit Plane Pattern Analysis | Embedding patterns in bit planes |
| Run Length Analysis | Sequential patterns in bit sequences |

**Metrics Calculated:**
- **Ratio of 1s:** Distribution of 1s in LSB (0.48-0.52 is suspicious)
- **Chi-Square Value:** 0-1 scale (higher means more suspicious)
- **Transition Frequency:** How often bits change
- **Run Length:** Average length of consecutive bit runs

**Verdict Levels:**
| Verdict | Probability | Meaning |
|---------|-------------|---------|
| Clean | 0-25% | Likely no hidden data |
| Uncertain | 25-50% | Cannot determine |
| Suspicious | 50-75% | May contain hidden data |
| Likely Stego | 75-95% | Probably contains hidden data |

### 9.2 Text Steganalysis

Scan text for zero width characters.

**Characters Detected:**
- U+200B (Zero Width Space)
- U+200C (Zero Width Non-Joiner)
- U+200D (Zero Width Joiner)
- U+FEFF (Zero Width No-Break Space)

**Output:** Count of each ZWC character type found

---

## 10. AI Chatbot Assistant

### 10.1 Overview

An AI-powered assistant that helps users learn about steganography.

**Technical Details:**
- **Model:** LLaMA 3.2 1B Instruct
- **Provider:** Hugging Face API
- **Context:** Keeps last 6 messages for context
- **Max tokens:** 250 per response
- **Temperature:** 0.7 (balanced creativity)
- **Top-p:** 0.9

### 10.2 Topics The Chatbot Can Help With

- Basic steganography concepts
- How zero width characters work
- How LSB encoding works
- Password and encryption guidance
- Step-by-step tutorials
- Best practices for hiding data
- Quality metrics explanation
- Detection and steganalysis
- Troubleshooting issues
- Deployment guidance

### 10.3 Fallback System

If the AI API is unavailable, keyword-based responses provide basic help:
- Recognizes common questions
- Provides pre-written helpful responses
- Ensures users always get some assistance

---

## 11. Image Quality Metrics

### 11.1 MSE (Mean Squared Error)

Measures the average squared difference between original and stego image.

**Formula:**
```
MSE = (1/n) x Sum of (original - stego)^2
```

**Interpretation:**
- Lower is better
- MSE < 1: Excellent quality
- MSE < 10: Very good quality

### 11.2 PSNR (Peak Signal-to-Noise Ratio)

Measures the ratio between maximum possible power and noise.

**Formula:**
```
PSNR = 10 x log10(MAX^2 / MSE)
```

**Interpretation (in decibels):**
| PSNR Value | Quality Level |
|------------|---------------|
| > 50 dB | Excellent |
| 40-50 dB | Very good |
| 30-40 dB | Good |
| < 30 dB | Poor |

### 11.3 SSIM (Structural Similarity Index)

Measures structural similarity between images.

**Range:** -1 to 1 (1 = identical images)

**Interpretation:**
| SSIM Value | Quality Level |
|------------|---------------|
| > 0.99 | Excellent |
| 0.95-0.99 | Very good |
| 0.90-0.95 | Good |
| < 0.90 | Noticeable difference |

---

## 12. Multi-File Steganography

### 12.1 Overview

Split a secret message across multiple images using XOR-based secret sharing.

**Key Features:**
- Split secrets into 2 to 10 parts
- ALL parts are required for reconstruction
- Each individual part reveals nothing about the secret
- Provides additional security layer

### 12.2 How It Works

1. Secret message is split using XOR operations
2. Each piece is hidden in a separate image
3. To decode, all images must be combined
4. XOR operations reverse the split

### 12.3 Custom Cover Images

- Upload your own images as covers
- Or use auto-generated gradient images
- Minimum number of images must match split count

---

## 13. User Interface Features

### 13.1 Navigation

- **Sticky navbar:** Always visible at top of page
- **Backdrop blur effect:** Modern frosted glass look
- **Pill-style buttons:** Rounded navigation items
- **Hover effects:** Visual feedback on all interactive elements
- **User menu dropdown:** Profile, settings, logout options

### 13.2 Workspace Cards

- Rounded corners with border radius
- Gradient headers for visual appeal
- Consistent padding and spacing
- Shadow effects for depth

### 13.3 Input Fields

- Large touch targets for mobile
- Clear focus states with color change
- Placeholder text for guidance
- Error states with red highlighting

### 13.4 Buttons

- **Primary buttons:** Purple gradient for main actions
- **Secondary buttons:** Outline style for less important actions
- **CTA buttons:** Large, animated buttons for key actions
- **Hover animations:** Scale and shadow changes

### 13.5 Upload Zones

- Drag and drop support
- Visual feedback when dragging
- File preview after upload
- File information display (name, size, type)
- Click to browse option

### 13.6 Feedback Elements

- **Toast notifications:** Pop-up messages for success/error
- **Progress bars:** Show encoding capacity
- **Loading spinners:** CSS-animated spinners
- **Probability rings:** Visual display for detection results

### 13.7 Modals

- Authentication modals (login, register)
- Confirmation dialogs
- Challenge detail views
- Smooth open/close animations

---

## 14. Dark Mode and Theming

### 14.1 Theme System

The application supports both light and dark modes with comprehensive CSS variable theming.

**Light Mode Colors:**
- Background: White and light gray
- Primary: Purple gradients
- Accent: Pink highlights
- Text: Dark gray and black

**Dark Mode Colors:**
- Background: Dark purple and near-black
- Primary: Lighter purple gradients
- Accent: Bright pink highlights
- Text: White and light gray

### 14.2 CSS Variables Used

```css
--bg-primary
--bg-secondary
--bg-tertiary
--text-primary
--text-secondary
--text-muted
--border-color
--card-bg
--primary-color
--accent-color
--shadow-sm
--shadow-md
--shadow-lg
```

### 14.3 Theme Toggle

- Toggle button in navbar
- Smooth transition between themes
- Theme preference saved to local storage
- Respects system preference on first visit

### 14.4 Animations

| Animation | Usage |
|-----------|-------|
| pageSlideIn | Page transitions |
| badgeFloat | Floating badge effect |
| iconFloat | Floating icon effect |
| pulse-glow | Glowing pulse effect |
| badge-pulse | Badge pulse animation |
| statusPulse | Status indicator pulse |
| iconBounce | Bouncing icon effect |
| arrow-bounce | Arrow bounce effect |
| rotate | Gradient rotation |

---

## 15. Database Structure

### 15.1 Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| email | TEXT | Unique email address |
| password_hash | TEXT | Hashed password |
| salt | TEXT | Password salt |
| created_at | TIMESTAMP | Account creation date |
| last_login | TIMESTAMP | Last login timestamp |
| is_active | BOOLEAN | Account active status |
| failed_login_attempts | INTEGER | Failed login counter |
| locked_until | TIMESTAMP | Account lockout expiry |
| profile_picture | TEXT | Profile picture data |
| settings | TEXT | User preferences (JSON) |
| total_points | INTEGER | Challenge points earned |

### 15.2 Sessions Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| refresh_token | TEXT | JWT refresh token |
| device_info | TEXT | Browser/device info |
| ip_address | TEXT | Client IP |
| created_at | TIMESTAMP | Session start |
| expires_at | TIMESTAMP | Session expiry |
| is_valid | BOOLEAN | Token validity |

### 15.3 Operation History Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| operation_type | TEXT | encode or decode |
| algorithm | TEXT | zwc, lsb, or multi |
| input_preview | TEXT | Preview of input |
| output_preview | TEXT | Preview of output |
| is_encrypted | BOOLEAN | Encryption used |
| metadata | TEXT | Additional info (JSON) |
| created_at | TIMESTAMP | Operation timestamp |

### 15.4 Challenges Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Challenge title |
| description | TEXT | Challenge question |
| difficulty | TEXT | easy, medium, or hard |
| stego_data | TEXT | Hidden data for stego challenges |
| algorithm | TEXT | puzzle, zwc, or lsb |
| password | TEXT | Decryption password if encrypted |
| solution | TEXT | Correct answer |
| hints | TEXT | JSON array of hints |
| points | INTEGER | Points awarded |
| created_at | TIMESTAMP | Creation date |
| solved_count | INTEGER | Number of solves |

### 15.5 Challenge Solutions Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| challenge_id | INTEGER | Foreign key to challenges |
| user_id | INTEGER | Foreign key to users |
| solved_at | TIMESTAMP | Solution timestamp |
| time_taken | INTEGER | Seconds to solve |
| points_awarded | INTEGER | Points given (0 if already solved) |

### 15.6 Burn Messages Table

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Unique token (32 bytes) |
| stego_data | TEXT | Hidden message data |
| algorithm | TEXT | Steganography method used |
| password | TEXT | Decryption password |
| parameters | TEXT | Additional parameters (JSON) |
| created_at | TIMESTAMP | Creation time |
| expires_at | TIMESTAMP | Expiration time |
| max_views | INTEGER | Maximum view count |
| view_count | INTEGER | Current view count |
| burned | BOOLEAN | Message destroyed flag |

### 15.7 Database Indexes

- `idx_users_email` - Fast email lookup
- `idx_users_username` - Fast username lookup
- `idx_sessions_token` - Fast token validation
- `idx_sessions_user` - Fast user session lookup
- `idx_history_user` - Fast history retrieval
- `idx_history_created` - Fast history sorting

---

## 16. API Endpoints

### 16.1 System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with version info |
| `/api/limits` | GET | System limits and recommendations |
| `/api/algorithms` | GET | Available algorithms info |

### 16.2 Authentication Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/register` | POST | No | Create new account |
| `/api/auth/login` | POST | No | Login with credentials |
| `/api/auth/refresh` | POST | Refresh Token | Get new access token |
| `/api/auth/logout` | POST | Yes | Logout (single or all sessions) |
| `/api/auth/me` | GET | Yes | Get user profile |
| `/api/auth/password` | PUT | Yes | Change password |
| `/api/auth/account` | DELETE | Yes | Delete account |
| `/api/auth/sessions` | GET | Yes | List active sessions |

### 16.3 Steganography Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/encode` | POST | Hide message using ZWC or LSB |
| `/api/decode` | POST | Extract hidden message |
| `/api/analyze` | POST | Get image quality metrics |

### 16.4 History Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/history` | GET | Yes | Get operation history |
| `/api/history/<id>` | DELETE | Yes | Delete history item |
| `/api/history/clear` | DELETE | Yes | Clear all history |
| `/api/history/stats` | GET | Yes | Usage statistics |

### 16.5 Challenge Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/challenges` | GET | List all challenges |
| `/api/challenges/<id>` | GET | Get challenge details |
| `/api/challenges/<id>/solve` | POST | Submit solution |
| `/api/leaderboard` | GET | Get top users |
| `/api/points` | GET | Get user points (auth required) |

### 16.6 Detection Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/detect/image` | POST | Analyze image for steganography |
| `/api/detect/text` | POST | Scan text for ZWC |

### 16.7 Burn Message Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/burn/create` | POST | Create burn message |
| `/api/burn/<token>` | GET | Retrieve burn message |

### 16.8 Multi-File Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/multi/encode` | POST | Split secret across images |
| `/api/multi/decode` | POST | Combine images to get secret |

### 16.9 Chatbot Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message to AI assistant |

---

## 17. System Configuration

### 17.1 System Limits

```
Maximum file size: 16 MB
Maximum text message length: 100,000 characters
Maximum secret message length: 50,000 characters
Maximum image dimension: 4096 pixels
Minimum image dimension: 10 pixels
Supported image formats: PNG, JPG, JPEG, BMP, GIF
Maximum history items: 100 per user
```

### 17.2 Environment Variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Secret key for JWT signing |
| `HUGGINGFACE_TOKEN` | API token for AI chatbot |

### 17.3 Dependencies

**Python Packages:**
- Flask - Web framework
- Flask-CORS - Cross-origin support
- Pillow - Image processing
- NumPy - Numerical operations
- cryptography - Encryption (Fernet/AES)
- PyJWT - JWT token handling
- huggingface_hub - AI chatbot API
- scikit-image - SSIM calculation (optional)

**Frontend Libraries:**
- Chart.js - Data visualization

### 17.4 Startup Options

| File | Platform | Description |
|------|----------|-------------|
| `start.py` | All | Python entry point |
| `start.bat` | Windows | Windows batch script |
| `start.sh` | Linux/Mac | Unix shell script |
| `wsgi.py` | Server | WSGI entry for production |

---

## 18. Unique and Creative Features

### 18.1 Dual-Layer Security
Combine steganography with AES encryption. Even if someone finds the hidden data, they cannot read it without the password.

### 18.2 Educational Challenge System
Learn steganography through gamified puzzles. Earn points and compete on the leaderboard while learning.

### 18.3 Real-Time Detection Scanner
Analyze any file to check if it might contain hidden data. Uses multiple statistical analysis techniques.

### 18.4 Self-Destructing Messages
Burn after reading feature with steganography. Messages automatically delete after viewing.

### 18.5 Multi-File Secret Sharing
XOR-based splitting across multiple images. All parts required to reconstruct. Maximum security for sensitive data.

### 18.6 AI-Powered Help
LLaMA chatbot specialized in steganography topics. Get help anytime while using the app.

### 18.7 Interactive Process Visualization
Animated explanations showing how steganography works step by step.

### 18.8 Comprehensive Quality Metrics
PSNR, MSE, and SSIM analysis to measure how invisible your hidden data is.

### 18.9 Detailed Operation History
Track all your encode and decode operations. Review past work and statistics.

### 18.10 Points and Leaderboard
Gamification for learning motivation. Compete with other users.

### 18.11 Custom Cover Images
Use your own images for multi-file encoding. Complete control over appearance.

### 18.12 Password Generator
Built-in secure password generation meeting all security requirements.

### 18.13 Live Capacity Calculator
See exactly how much data can be hidden before encoding. Plan your messages accordingly.

### 18.14 Mobile-Responsive Design
Full functionality on all devices. Touch-friendly interface.

### 18.15 Offline Fallback
Keyword-based chatbot responses when AI is unavailable. Always get help.

---

## Summary

SteganographyPro is a comprehensive steganography platform featuring:

- **2 steganography methods** (ZWC text and LSB image)
- **AES-128 encryption** with PBKDF2 password hashing
- **JWT authentication** with refresh tokens
- **Rate limiting** on all endpoints
- **Educational challenges** with points and leaderboard
- **Burn after reading** self-destructing messages
- **Multi-file secret sharing** with XOR splitting
- **AI chatbot** powered by LLaMA
- **Detection scanner** with statistical analysis
- **Quality metrics** (MSE, PSNR, SSIM)
- **Dark mode** and responsive design
- **16 database tables** with proper indexing
- **30+ API endpoints** for all features

---

*Documentation generated for SteganographyPro v1.0*
