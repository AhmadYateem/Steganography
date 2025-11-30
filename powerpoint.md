```latex
% Steganography Suite PowerPoint Deck (Beamer)
\documentclass[aspectratio=169]{beamer}
\usetheme{metropolis}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{enumitem}
\hypersetup{colorlinks=true, urlcolor=cyan}

\title{Inside the Steganography Suite}
\subtitle{Every framework, library, algorithm, and operational detail}
\author{Deployed via PythonAnywhere}
\date{November 26, 2025}

\begin{document}

\frame{\titlepage}

%=========================
\section{Project Map}
%=========================
\begin{frame}{Repository Tour}
\begin{itemize}[leftmargin=*]
    \item Monorepo root: \texttt{Steganography/}
    \item Backend: \texttt{app.py} (Flask 3.x REST API) + \texttt{auth.py}, \texttt{database.py}
    \item Core engines: \texttt{text\_stego.py}, \texttt{image\_stego.py}, \texttt{secure\_stego.py}, \texttt{crypto.py}, \texttt{metrics.py}
    \item Frontend: \texttt{static/index.html}, \texttt{static/features.js}, \texttt{static/chatbot.js}, \texttt{static/chatbot.css}
    \item AI layer: \texttt{chatbot\_ai.py} (LLaMA 3.2 via Hugging Face InferenceClient)
    \item Docs: \texttt{README.md}, \texttt{PROJECT\_REPORT.md}, \texttt{API\_GUIDE.md}, \texttt{IMAGE\_GUIDE.md}, \texttt{METRICS\_GUIDE.md}, \texttt{FRONTEND\_GUIDE.md}, \texttt{DEPLOYMENT\_GUIDE.md}, chatbot setup guides
    \item Launch scripts: \texttt{start.py}, \texttt{start.sh}, \texttt{start.bat}; production entry \texttt{wsgi.py}
\end{itemize}
\end{frame}

%=========================
\section{Frameworks \& Libraries}
%=========================
\begin{frame}{Backend Stack}
\begin{itemize}[leftmargin=*]
    \item \textbf{Flask 3.x}: routing, JSON APIs, static file serving
    \item \textbf{Flask-CORS 4.x}: same-origin relaxation with credential support
    \item \textbf{PyJWT 2.8}: signing/validating JWT access \& refresh tokens
    \item \textbf{cryptography/Fernet}: AES-128-CBC + HMAC-SHA256 authenticated encryption
    \item \textbf{SQLite3}: file DB under \texttt{instance/steganography.db}; Python standard lib driver
    \item \textbf{Pillow}: PNG/BMP/TIFF I/O for LSB routines and metrics
    \item \textbf{NumPy}: pixel math, MSE/PSNR calculations
    \item \textbf{scikit-image}: SSIM (	exttt{structural\_similarity})
    \item \textbf{huggingface\_hub}: InferenceClient for meta-llama/Llama-3.2-1B-Instruct
\end{itemize}
\end{frame}

\begin{frame}{Frontend Stack}
\begin{itemize}[leftmargin=*]
    \item Pure HTML5/CSS3/ES6 (no framework) for maximum PythonAnywhere compatibility
    \item Cyber/dark theme with theme toggle \texttt{toggleTheme()} (stored in \texttt{localStorage})
    \item Drag-and-drop upload zones, animated drop indicators, toast notifications
    \item Modules: \texttt{features.js} (multi-file, scanner, burn, challenges), \texttt{chatbot.js} (floating chat widget), \texttt{chatbot.css}
    \item Responsive grid handles text vs image encode/decode dashboards, metrics panels, history timeline, challenge cards
\end{itemize}
\end{frame}

%=========================
\section{System Limits \& Policies}
%=========================
\begin{frame}{Global Limits (\texttt{SYSTEM\_LIMITS})}
\begin{itemize}[leftmargin=*]
    \item Max upload size: 16 MB (Flask \texttt{MAX\_CONTENT\_LENGTH})
    \item Image dimensions: 10--4096 px each side; validated via Pillow before processing
    \item Text caps: cover text 100{,}000 chars; secret payload 50{,}000 chars (tracked via live counters)
    \item History per user: 100 entries (automatic rolling deletion)
    \item Rate limiting decorator \texttt{@rate\_limit}: encode/decode 30 req/min, auth 10/min, detector 10/min, multi-file 5/min
\end{itemize}
\end{frame}

%=========================
\section{Encoding Algorithms}
%=========================
\begin{frame}{Text Steganography (ZWC)}
\begin{itemize}[leftmargin=*]
    \item \texttt{text\_stego.py}
    \item Convert secret text $\rightarrow$ UTF-8 bytes $\rightarrow$ binary string
    \item Map bits to zero-width Unicode: 1-bit (ZWNJ, ZWJ) or 2-bit (ZW Space, ZWNJ, ZWJ, ZW NBSP)
    \item Insertion strategies:
    \begin{itemize}
        \item \texttt{append}: tack onto end of cover text
        \item \texttt{between\_words}: distribute between spaces
        \item \texttt{distributed}: periodic injection for stealth
    \end{itemize}
    \item Decoder scans characters, strips invisible glyphs, rebuilds binary, converts back to text
\end{itemize}
\end{frame}

\begin{frame}{Image Steganography (LSB)}
\begin{itemize}[leftmargin=*]
    \item \texttt{image\_stego.py}
    \item Header: first 32 bits store payload length (up to 4 GB theoretical)
    \item Payload embedded in selected channel (default Blue) with 1, 2, or 3 bits per pixel
    \item PNG/BMP/TIFF recommended; JPEG rejected (lossy destroys LSB)
    \item Capacity formula: $\frac{width \times height \times 3 \times bits\_per\_pixel}{8}$ bytes
    \item Decoding reads header, extracts exact number of bits, reconstructs plaintext
\end{itemize}
\end{frame}

\begin{frame}{Secure Pipeline (Defense-in-Depth)}
\begin{itemize}[leftmargin=*]
    \item \texttt{secure\_stego.py}
    \item Encode pipeline:
    \begin{enumerate}
        \item Derive key via SHA-256 (Fernet requirement); encrypt secret with AES-128-CBC + HMAC
        \item Base64 ciphertext
        \item Feed ciphertext into ZWC encoder (default 2-bit, \texttt{between\_words})
    \end{enumerate}
    \item Decode pipeline:
    \begin{enumerate}
        \item Extract ZWC payload
        \item Base64 decode
        \item Decrypt via Fernet; raise errors if password/encoding mismatch
    \end{enumerate}
    \item Benefits: even if stego detected, ciphertext stays opaque without password
\end{itemize}
\end{frame}

\begin{frame}{Bonus Algorithms}
\begin{itemize}[leftmargin=*]
    \item \textbf{Multi-file shares} (\texttt{MultiFileStego}): XOR secret into N parts; each part base64-encoded and embedded into its own LSB image. All parts needed to reconstruct.
    \item \textbf{Burn-after-reading} (\texttt{BurnAfterReading}): stores ZWC stego text with \#views + expiry; retrieval increments view count, burns record on limit or expiry.
    \item \textbf{Stego Detector} (\texttt{StegoDetector}):
    \begin{itemize}
        \item Image: LSB randomness, chi-square anomalies, entropy, run-length checks
        \item Text: counts zero-width characters
    \end{itemize}
\end{itemize}
\end{frame}

%=========================
\section{Encode/Decode Walkthrough}
%=========================
\begin{frame}{Text Encode Flow}
\begin{enumerate}[leftmargin=*]
    \item Frontend collects cover text, secret, password flag, encoding bits, insertion method
    \item Optional password triggers secure pipeline (encrypt-before-hide)
    \item POST \texttt{/api/encode} with JSON payload
    \item Backend validates limits, rate limit, optionally logs 401 if token missing for history
    \item \texttt{text\_stego.encode\_message()} runs; response includes stego text, metadata (lengths, encoding bits)
    \item History entry saved if JWT present
\end{enumerate}
\end{frame}

\begin{frame}{Text Decode Flow}
\begin{enumerate}[leftmargin=*]
    \item User pastes stego text + password (if used) + encoding bits
    \item POST \texttt{/api/decode}
    \item Backend extracts ZWC characters and returns plaintext (or decrypts if secure pipeline)
    \item Errors: invalid encoding bits, wrong password (Fernet exception), corrupted ZWC
    \item History logging mirrors encode path
\end{enumerate}
\end{frame}

\begin{frame}{Image Encode Flow}
\begin{enumerate}[leftmargin=*]
    \item Frontend base64-encodes PNG, gathers secret/password/BPP/channel
    \item Backend decodes image, validates dimensions + format
    \item Optional encryption via \texttt{security.encrypt\_message}
    \item \texttt{image\_stego.encode\_lsb} writes to temp file, calculates metrics
    \item Response returns base64 stego image, metrics summary, download link
    \item \texttt{HistoryManager} stores entry with metadata (BPP, encrypted flag)
\end{enumerate}
\end{frame}

\begin{frame}{Image Decode Flow}
\begin{enumerate}[leftmargin=*]
    \item Upload stego PNG + BPP/channel + optional password
    \item Backend decodes to temp file, calls \texttt{image\_stego.decode\_lsb}
    \item If encrypted, passes ciphertext to \texttt{security.decrypt\_message}
    \item Returns plaintext + metadata (bits extracted, capacity usage)
    \item History entry saved with decode metadata
\end{enumerate}
\end{frame}

%=========================
\section{Security and Password Storage}
%=========================
\begin{frame}{Authentication Overview}
\begin{itemize}[leftmargin=*]
    \item JWT access tokens (15 min) + refresh tokens (30 days)
    \item Access tokens signed with HS256; secret loaded from \texttt{JWT\_SECRET\_KEY}
    \item Refresh tokens stored in \texttt{sessions} table with device info/IP/expiry; invalidated on logout or expiry
    \item \texttt{TokenBlacklist} holds JTI of revoked tokens (single-worker friendly)
\end{itemize}
\end{frame}

\begin{frame}{Password Handling}
\begin{itemize}[leftmargin=*]
    \item \texttt{database.UserManager} enforces length 8--128, uppercase, lowercase, digit, special char
    \item \texttt{hashlib.pbkdf2\_hmac('sha256', password, salt, 100000)}
    \item Per-user 64-hex salt from \texttt{secrets.token\_hex(32)} stored alongside hash
    \item Salt + hash persisted in users table; plaintext never stored
    \item Login flow:
    \begin{enumerate}
        \item Fetch salt/hash, recompute PBKDF2
        \item Compare via \texttt{secrets.compare\_digest}
        \item Track failed attempts; lock account for 15 min after 5 failures
    \end{enumerate}
\end{itemize}
\end{frame}

%=========================
\section{Database Schema}
%=========================
\begin{frame}{SQLite Tables}
\begin{tabular}{ll}
\toprule
Table & Purpose \\
\midrule
\texttt{users} & Credentials, salts, profile data, settings JSON \\
\texttt{sessions} & Refresh tokens, device/IP, expiry, validity flag \\
\texttt{operation\_history} & Encode/decode logs with metadata, encryption flag \\
\texttt{challenges} & Title, difficulty, algorithm, hints, stego payload, solution \\
\texttt{challenge\_solutions} & Per-user solve stats/time \\
\texttt{burn\_messages} & Self-destruct payloads + expiry \& view counts \\
\texttt{multi\_file\_ops} & Metadata on split secrets (audit) \\
\texttt{password\_reset\_tokens} & Password recovery tokens (optional) \\
\bottomrule
\end{tabular}
\end{frame}

%=========================
\section{History, Metrics, and Detection}
%=========================
\begin{frame}{History Engine}
\begin{itemize}[leftmargin=*]
    \item \texttt{HistoryManager.add\_operation}: stores operation type, algorithm, previews (truncated), encryption flag, metadata JSON (BPP, metrics, capacity)
    \item Frontend history panel shows icons (encode/decode), badges (text/image/encrypted), timestamps, buttons for clearing entries
    \item Stats endpoint aggregates counts by type/algorithm/encrypted operations
\end{itemize}
\end{frame}

\begin{frame}{Quality Metrics}
\begin{itemize}[leftmargin=*]
    \item \texttt{metrics.calculate\_metrics\_summary} returns MSE/PSNR/SSIM + qualitative assessment (Excellent/Very Good/Good/Poor)
    \item Recommendations array (e.g., "use fewer bits per pixel" or "quality acceptable")
    \item \texttt{/api/analyze} endpoint powers front-end dashboard with gauges and textual explanations
\end{itemize}
\end{frame}

\begin{frame}{Detection Lab}
\begin{itemize}[leftmargin=*]
    \item \texttt{/api/detect/image}: accepts base64 PNG, runs \texttt{StegoDetector.analyze\_image}
    \item Indicators: uniform LSB ratios, entropy spikes, chi-square anomalies, run-length irregularities
    \item \texttt{/api/detect/text}: counts zero-width chars; verdict clean/likely stego
    \item UI: probability donut, verdict badges, indicator list, expandable JSON block
\end{itemize}
\end{frame}

%=========================
\section{Frontend Experience}
%=========================
\begin{frame}{Dark-Mode UI Highlights}
\begin{itemize}[leftmargin=*]
    \item Cyber gradient hero, Apple-inspired typography, theme toggle button (top-right)
    \item Separate text vs image workflows, step-by-step callouts, drag-drop uploaders
    \item Inline char counters, password strength cues, toast notifications \texttt{showToast}
    \item Steganography history timeline + FAQ ensures "literally mention history"
    \item Challenge hub with difficulty badges, animated cards, solver modals
\end{itemize}
\end{frame}

%=========================
\section{AI Chatbot}
%=========================
\begin{frame}{LLaMA Chat Integration}
\begin{itemize}[leftmargin=*]
    \item Backend: \texttt{chatbot\_ai.py}
    \begin{enumerate}
        \item Load \texttt{HUGGINGFACE\_TOKEN} (env var or Windows \texttt{setx})
        \item Instantiate InferenceClient with \texttt{meta-llama/Llama-3.2-1B-Instruct}
        \item Provide system prompt focused on ZWC, LSB, AES, metrics, best practices
        \item Maintain short conversation history (last 3 exchanges)
    \end{enumerate}
    \item Fallback: deterministic responses triggered by keywords (ZWC, LSB, capacity, errors, PythonAnywhere) when API unreachable or token missing
    \item Frontend: floating purple button, chat drawer, typing indicator, conversation log, error banners when fallback active
\end{itemize}
\end{frame}

%=========================
\section{Deployment \& Ops}
%=========================
\begin{frame}{PythonAnywhere Deployment}
\begin{enumerate}[leftmargin=*]
    \item Push repo to GitHub or upload zip via Files tab
    \item Bash console: \texttt{git clone} or unzip; install deps \texttt{pip3.10 install --user -r requirements.txt}
    \item Create web app (Flask, Python 3.10); set working directory + WSGI file to import \texttt{app}
    \item Configure static mapping: URL \texttt{/static/} \rightarrow project \texttt{/static}
    \item Add env vars: \texttt{JWT\_SECRET\_KEY}, \texttt{HUGGINGFACE\_TOKEN}
    \item Reload site; monitor \texttt{error.log} and \texttt{server.log}
\end{enumerate}
\end{frame}

\begin{frame}{Testing \& Diagnostics}
\begin{itemize}[leftmargin=*]
    \item \texttt{test\_api.py}: import smoke tests, text stego round-trip, encryption round-trip, route listing
    \item \texttt{test\_auth.py}: signup/login/history flows with JWT tokens
    \item \texttt{test\_api\_detector.py}, \texttt{test\_detector.py}: scanner endpoints
    \item \texttt{test\_new\_features.py}: multi-file + burn APIs
    \item Demo scripts: \texttt{demo.py}, \texttt{demo\_image.py}, \texttt{demo\_secure.py}
\end{itemize}
\end{frame}

%=========================
\section{Key Takeaways}
%=========================
\begin{frame}{Summary}
\begin{itemize}[leftmargin=*]
    \item Dual-carrier steganography with encryption-first design
    \item Robust security posture: PBKDF2 password storage, JWT auth, rate limiting, history logging
    \item Extensive toolbelt: multi-file secret sharing, burn links, stego detector, metrics dashboard, challenge gamification
    \item Hugging Face LLaMA assistant + detailed documentation streamline onboarding
    \item Production-ready on PythonAnywhere with 16 MB uploads, 50k-char payloads, and polished dark-mode UX
\end{itemize}
\end{frame}

\end{document}
```
