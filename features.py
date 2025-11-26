"""
Advanced Steganography Features
- Challenge Generator
- Multi-File Steganography
- Steganography Scanner/Detector
- Self-Destructing Messages
"""

import os
import json
import sqlite3
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import numpy as np
from PIL import Image
import io

# Import existing modules
import image_stego
import text_stego
import security


# ============================================================================
# DATABASE SETUP FOR NEW FEATURES
# ============================================================================

def init_features_database():
    """Initialize database tables for new features."""
    conn = sqlite3.connect('steganography.db')
    cursor = conn.cursor()

    # Challenges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            stego_data TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            password TEXT,
            solution TEXT NOT NULL,
            hints TEXT,
            points INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            solved_count INTEGER DEFAULT 0
        )
    ''')

    # Challenge attempts/solutions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenge_solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER,
            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_taken INTEGER,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Self-destructing messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS burn_messages (
            id TEXT PRIMARY KEY,
            stego_data TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            password TEXT,
            parameters TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            max_views INTEGER DEFAULT 1,
            view_count INTEGER DEFAULT 0,
            burned BOOLEAN DEFAULT 0
        )
    ''')

    # Multi-file operations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS multi_file_ops (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            file_count INTEGER NOT NULL,
            secret_message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# ============================================================================
# CHALLENGE GENERATOR
# ============================================================================

class ChallengeManager:
    """Manage steganography challenges."""

    @staticmethod
    def create_challenge(title: str, description: str, difficulty: str,
                        secret_message: str, algorithm: str,
                        password: str = None, hints: List[str] = None) -> int:
        """Create a new challenge."""
        import tempfile

        # Generate stego data based on algorithm
        if algorithm == 'zwc':
            cover_text = "The quick brown fox jumps over the lazy dog. " * 10
            if password:
                encrypted = security.encrypt_message(secret_message, password)
                stego_data = text_stego.encode_message(cover_text, encrypted)
            else:
                stego_data = text_stego.encode_message(cover_text, secret_message)

        elif algorithm == 'lsb':
            # Create a simple test image
            img = Image.new('RGB', (800, 600), color=(100, 150, 200))
            temp_path = tempfile.mktemp(suffix='.png')
            img.save(temp_path)

            stego_temp = tempfile.mktemp(suffix='.png')
            if password:
                encrypted = security.encrypt_message(secret_message, password)
                image_stego.encode_lsb(temp_path, encrypted, stego_temp)
            else:
                image_stego.encode_lsb(temp_path, secret_message, stego_temp)

            # Read stego image as base64
            import base64
            with open(stego_temp, 'rb') as f:
                stego_data = base64.b64encode(f.read()).decode('ascii')

            os.unlink(temp_path)
            os.unlink(stego_temp)

        # Calculate points based on difficulty
        points_map = {'easy': 50, 'medium': 100, 'hard': 200}
        points = points_map.get(difficulty, 100)

        # Store in database
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO challenges (title, description, difficulty, stego_data,
                                  algorithm, password, solution, hints, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, difficulty, stego_data, algorithm,
              password, secret_message, json.dumps(hints or []), points))

        challenge_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return challenge_id

    @staticmethod
    def get_challenges(difficulty: str = None) -> List[Dict]:
        """Get all challenges."""
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        if difficulty:
            cursor.execute('''
                SELECT id, title, description, difficulty, algorithm, points,
                       solved_count, created_at
                FROM challenges
                WHERE difficulty = ?
                ORDER BY points DESC, created_at DESC
            ''', (difficulty,))
        else:
            cursor.execute('''
                SELECT id, title, description, difficulty, algorithm, points,
                       solved_count, created_at
                FROM challenges
                ORDER BY points DESC, created_at DESC
            ''')

        challenges = []
        for row in cursor.fetchall():
            challenges.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'difficulty': row[3],
                'algorithm': row[4],
                'points': row[5],
                'solved_count': row[6],
                'created_at': row[7]
            })

        conn.close()
        return challenges

    @staticmethod
    def get_challenge(challenge_id: int) -> Dict:
        """Get specific challenge details."""
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, description, difficulty, stego_data, algorithm,
                   password, solution, hints, points, solved_count
            FROM challenges
            WHERE id = ?
        ''', (challenge_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'difficulty': row[3],
            'stego_data': row[4],
            'algorithm': row[5],
            'has_password': bool(row[6]),
            'hints': json.loads(row[8]) if row[8] else [],
            'points': row[9],
            'solved_count': row[10]
        }

    @staticmethod
    def submit_solution(challenge_id: int, submitted_answer: str, user_id: int = None, start_time: float = None) -> Tuple[bool, str, int]:
        """Submit and verify challenge solution."""
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('SELECT solution, points FROM challenges WHERE id = ?', (challenge_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Challenge not found", 0

        correct_answer = row[0]
        points = row[1]

        # Check if answer is correct
        if submitted_answer.strip() == correct_answer.strip():
            # Update solved count
            cursor.execute('UPDATE challenges SET solved_count = solved_count + 1 WHERE id = ?', (challenge_id,))

            # Record solution
            time_taken = int(time.time() - start_time) if start_time else 0
            cursor.execute('''
                INSERT INTO challenge_solutions (challenge_id, user_id, time_taken)
                VALUES (?, ?, ?)
            ''', (challenge_id, user_id, time_taken))

            conn.commit()
            conn.close()

            return True, "Correct! Challenge solved!", points
        else:
            conn.close()
            return False, "Incorrect solution. Try again!", 0

    @staticmethod
    def init_default_challenges():
        """Create steganography knowledge challenges - simple text-based puzzles."""
        challenges = [
            # ==================== EASY CHALLENGES ====================
            {
                'title': 'The Hidden Word',
                'description': 'Steganography comes from Greek words meaning "covered writing". What is the Greek word for "covered" or "hidden"? (Hint: It starts with "steg")',
                'difficulty': 'easy',
                'secret_message': 'steganos',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Greek language', 'Steg- prefix', 'Means covered/hidden']
            },
            {
                'title': 'Bit by Bit',
                'description': 'In LSB steganography, what does LSB stand for? (three words, all lowercase, separated by spaces)',
                'difficulty': 'easy',
                'secret_message': 'least significant bit',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['It describes which bit we modify', 'The smallest change in binary', 'L___ S_______ B__']
            },
            {
                'title': 'Invisible Characters',
                'description': 'ZWC steganography uses characters that are invisible. What does ZWC stand for? (three words, lowercase)',
                'difficulty': 'easy',
                'secret_message': 'zero width characters',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Unicode special characters', 'They have no visible width', 'Z___ W____ C________']
            },
            {
                'title': 'The Pioneer',
                'description': 'Who wrote the first book on steganography in 1499, titled "Steganographia"? (just the last name, lowercase)',
                'difficulty': 'easy',
                'secret_message': 'trithemius',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['A German abbot', 'Johannes _________', 'Wrote about hidden writing']
            },
            
            # ==================== MEDIUM CHALLENGES ====================
            {
                'title': 'The Math Formula',
                'description': 'In image steganography, capacity depends on dimensions. If an image is 100x100 pixels with RGB colors, and we use 1 bit per channel, how many BYTES can we hide? (just the number)',
                'difficulty': 'medium',
                'secret_message': '3750',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['100 x 100 = 10,000 pixels', '3 channels (RGB) per pixel', 'Divide total bits by 8 for bytes']
            },
            {
                'title': 'Quality Metrics',
                'description': 'What metric, measured in decibels (dB), indicates how much an image changed after steganography? Higher is better. (abbreviation, uppercase)',
                'difficulty': 'medium',
                'secret_message': 'PSNR',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Peak Signal to Noise Ratio', 'Measured in dB', 'Four letters']
            },
            {
                'title': 'Ancient Secrets',
                'description': 'In ancient Greece, a famous historian recorded that a message was hidden on a shaved head, then covered by hair. Who was this historian? (lowercase)',
                'difficulty': 'medium',
                'secret_message': 'herodotus',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Father of History', 'Greek historian', 'Wrote about Persian Wars']
            },
            {
                'title': 'The Invisible Ink',
                'description': 'During WWII, what common household liquid was used as invisible ink by spies? (one word, lowercase)',
                'difficulty': 'medium',
                'secret_message': 'lemon',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['A citrus fruit', 'Also used for cooking', 'Yellow when visible']
            },
            
            # ==================== HARD CHALLENGES ====================
            {
                'title': 'The Cipher Equation',
                'description': 'A 1024x768 PNG image uses 2-bit LSB encoding in the blue channel only. What is the maximum message size in BYTES? (just the number)',
                'difficulty': 'hard',
                'secret_message': '196608',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['1024 x 768 pixels', '2 bits per pixel, 1 channel', 'Divide bits by 8']
            },
            {
                'title': 'Detection Challenge',
                'description': 'What statistical attack uses a chi-square test to detect LSB steganography by analyzing pixel value pairs? (two words, lowercase)',
                'difficulty': 'hard',
                'secret_message': 'chi square',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Greek letter chi', 'Statistical test', 'Compares expected vs observed']
            },
            {
                'title': 'The Standard',
                'description': 'What image format is BEST for steganography because it uses lossless compression? (uppercase, 3 letters)',
                'difficulty': 'hard',
                'secret_message': 'PNG',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Portable Network Graphics', 'Lossless format', 'NOT JPEG']
            },
            {
                'title': 'Crypto Master',
                'description': 'What encryption mode does Fernet (used in this app) use for AES? (abbreviation-number format, like CBC-128)',
                'difficulty': 'hard',
                'secret_message': 'CBC-128',
                'algorithm': 'puzzle',
                'password': None,
                'hints': ['Cipher Block Chaining', 'AES with 128 bits', 'C__-___']
            }
        ]

        for challenge in challenges:
            try:
                # Check if challenge with this title already exists
                conn = sqlite3.connect('steganography.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM challenges WHERE title = ?', (challenge['title'],))
                existing = cursor.fetchone()
                conn.close()
                
                if not existing:
                    ChallengeManager.create_puzzle_challenge(**challenge)
            except Exception as e:
                print(f"Error creating challenge {challenge.get('title', 'unknown')}: {e}")

    @staticmethod
    def create_puzzle_challenge(title: str, description: str, difficulty: str,
                               secret_message: str, algorithm: str,
                               password: str = None, hints: List[str] = None) -> int:
        """Create a simple puzzle challenge (no stego generation)."""
        
        # Calculate points based on difficulty
        points_map = {'easy': 50, 'medium': 100, 'hard': 200}
        points = points_map.get(difficulty, 100)

        # Store in database - stego_data is just the description for puzzles
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO challenges (title, description, difficulty, stego_data,
                                  algorithm, password, solution, hints, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, difficulty, description, algorithm,
              password, secret_message, json.dumps(hints or []), points))

        challenge_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return challenge_id


# ============================================================================
# STEGANOGRAPHY SCANNER/DETECTOR
# ============================================================================

class StegoDetector:
    """Detect steganography in images and text."""

    @staticmethod
    def analyze_image(image_data: bytes) -> Dict[str, Any]:
        """Analyze image for steganography indicators."""
        img = Image.open(io.BytesIO(image_data))
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)

        results = {
            'has_stego_probability': 0.0,
            'indicators': [],
            'lsb_analysis': {},
            'statistical_analysis': {},
            'verdict': 'clean'
        }

        # LSB Analysis
        lsb_score = StegoDetector._analyze_lsb_randomness(img_array)
        results['lsb_analysis'] = lsb_score

        # Statistical tests
        stats = StegoDetector._statistical_tests(img_array)
        results['statistical_analysis'] = stats

        # Calculate overall probability with improved detection
        probability = 0.0

        # Check if LSB distribution is suspiciously uniform (close to 50% ones)
        # Steganography typically makes LSB distribution more uniform
        ones_ratio = lsb_score['ones_ratio']
        if 0.48 <= ones_ratio <= 0.52:
            probability += 25
            results['indicators'].append('LSB distribution is suspiciously uniform (typical of stego)')
        
        # High randomness in LSB is suspicious when combined with uniform distribution
        if lsb_score['randomness_score'] > 0.9 and 0.45 <= ones_ratio <= 0.55:
            probability += 20
            results['indicators'].append('LSB shows characteristics of hidden data')

        # Chi-square anomaly detection - look for unusual uniformity in pairs
        if stats['chi_square'] < 0.1:
            # Very low chi-square can indicate manipulation
            probability += 15
            results['indicators'].append('Statistical anomaly in pixel value pairs')
        elif stats['chi_square'] > 0.7:
            probability += 20
            results['indicators'].append('Chi-square test suggests possible hidden data')

        # Entropy analysis - stego images often have slightly higher entropy
        if stats['entropy'] > 7.8:
            probability += 15
            results['indicators'].append('Unusually high entropy in pixel distribution')

        # Bit plane anomaly - patterns in LSB transitions
        if lsb_score['bit_plane_anomaly']:
            probability += 20
            results['indicators'].append('Anomalies detected in LSB bit plane patterns')
        
        # Sequential analysis - check for embedded data patterns
        if lsb_score.get('sequential_anomaly', False):
            probability += 15
            results['indicators'].append('Sequential patterns suggest embedded data')

        results['has_stego_probability'] = min(probability, 95)

        # Verdict with better calibration
        if probability < 20:
            results['verdict'] = 'clean'
        elif probability < 45:
            results['verdict'] = 'uncertain'
        elif probability < 65:
            results['verdict'] = 'suspicious'
        else:
            results['verdict'] = 'likely_stego'

        return results

    @staticmethod
    def _analyze_lsb_randomness(img_array: np.ndarray) -> Dict:
        """Analyze LSB randomness."""
        if len(img_array.shape) == 2:
            # Grayscale
            lsb = img_array & 1
        else:
            # RGB - analyze all channels
            lsb_r = img_array[:, :, 0] & 1
            lsb_g = img_array[:, :, 1] & 1
            lsb_b = img_array[:, :, 2] & 1
            lsb = lsb_b  # Primary analysis on blue channel (most common)

        # Calculate randomness
        ones = np.sum(lsb)
        total = lsb.size
        ratio = ones / total

        # Perfect randomness = 0.5
        randomness_score = 1.0 - abs(ratio - 0.5) * 2

        # Check for patterns
        flat = lsb.flatten()
        transitions = np.sum(np.abs(np.diff(flat)))
        expected_transitions = (total - 1) * 0.5
        pattern_score = abs(transitions - expected_transitions) / expected_transitions if expected_transitions > 0 else 0
        
        # Check for sequential anomalies (embedded data often has structure)
        # Look at runs of consecutive same bits
        runs = []
        current_run = 1
        for i in range(1, len(flat)):
            if flat[i] == flat[i-1]:
                current_run += 1
            else:
                runs.append(current_run)
                current_run = 1
        runs.append(current_run)
        
        avg_run_length = np.mean(runs) if runs else 1
        # Natural images typically have longer runs than stego images
        sequential_anomaly = avg_run_length < 1.8  # Stego tends to have shorter runs

        return {
            'randomness_score': float(randomness_score),
            'ones_ratio': float(ratio),
            'bit_plane_anomaly': bool(pattern_score > 0.2),
            'pattern_score': float(pattern_score),
            'avg_run_length': float(avg_run_length),
            'sequential_anomaly': bool(sequential_anomaly)
        }

    @staticmethod
    def _statistical_tests(img_array: np.ndarray) -> Dict:
        """Perform statistical tests."""
        if len(img_array.shape) == 3:
            # Use blue channel
            channel = img_array[:, :, 2].flatten()
        else:
            channel = img_array.flatten()

        # Calculate entropy
        hist, _ = np.histogram(channel, bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))

        # Chi-square test
        expected = len(channel) / 256
        chi_square = np.sum((hist * len(channel) - expected) ** 2 / expected) / expected
        chi_normalized = min(chi_square / 100, 1.0)

        return {
            'entropy': float(entropy),
            'chi_square': float(chi_normalized),
            'unique_values': int(np.unique(channel).size)
        }

    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """Analyze text for steganography."""
        results = {
            'has_stego_probability': 0.0,
            'indicators': [],
            'zero_width_chars': 0,
            'verdict': 'clean'
        }

        # Check for zero-width characters
        zwc_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        zwc_count = sum(text.count(char) for char in zwc_chars)

        results['zero_width_chars'] = zwc_count

        if zwc_count > 0:
            probability = min(zwc_count * 10, 95)
            results['has_stego_probability'] = probability
            results['indicators'].append(f'Found {zwc_count} zero-width characters')
            results['verdict'] = 'likely_stego'

        return results


# ============================================================================
# SELF-DESTRUCTING MESSAGES
# ============================================================================

class BurnAfterReading:
    """Manage self-destructing steganography messages."""

    @staticmethod
    def create_burn_message(stego_data: str, algorithm: str, password: str = None,
                           parameters: Dict = None, max_views: int = 1,
                           expire_hours: int = 24) -> str:
        """Create a self-destructing message."""
        burn_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expire_hours)

        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO burn_messages
            (id, stego_data, algorithm, password, parameters, expires_at, max_views)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (burn_id, stego_data, algorithm, password,
              json.dumps(parameters or {}), expires_at, max_views))

        conn.commit()
        conn.close()

        return burn_id

    @staticmethod
    def get_burn_message(burn_id: str) -> Tuple[bool, str, Dict]:
        """Get and potentially burn a message."""
        conn = sqlite3.connect('steganography.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT stego_data, algorithm, password, parameters, expires_at,
                   max_views, view_count, burned
            FROM burn_messages
            WHERE id = ?
        ''', (burn_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Message not found or already burned", {}

        stego_data, algorithm, password, params_json, expires_at, max_views, view_count, burned = row

        # Check if already burned
        if burned:
            conn.close()
            return False, "This message has been burned (self-destructed)", {}

        # Check if expired
        if datetime.fromisoformat(expires_at) < datetime.now():
            cursor.execute('UPDATE burn_messages SET burned = 1 WHERE id = ?', (burn_id,))
            conn.commit()
            conn.close()
            return False, "This message has expired and been burned", {}

        # Increment view count
        new_view_count = view_count + 1
        cursor.execute('UPDATE burn_messages SET view_count = ? WHERE id = ?',
                      (new_view_count, burn_id))

        # Check if should burn
        if new_view_count >= max_views:
            cursor.execute('UPDATE burn_messages SET burned = 1 WHERE id = ?', (burn_id,))

        conn.commit()
        conn.close()

        return True, stego_data, {
            'algorithm': algorithm,
            'password': password,
            'parameters': json.loads(params_json) if params_json else {},
            'views_remaining': max_views - new_view_count,
            'will_burn': new_view_count >= max_views
        }


# ============================================================================
# MULTI-FILE STEGANOGRAPHY
# ============================================================================

class MultiFileStego:
    """Split secret across multiple files."""

    @staticmethod
    def split_secret(secret: str, num_parts: int) -> List[str]:
        """Split secret into multiple parts using XOR."""
        # Pad secret to make it divisible
        secret_bytes = secret.encode('utf-8')

        # Generate random parts
        parts = []
        for i in range(num_parts - 1):
            parts.append(secrets.token_bytes(len(secret_bytes)))

        # Calculate final part using XOR
        final_part = bytearray(secret_bytes)
        for part in parts:
            for i in range(len(final_part)):
                final_part[i] ^= part[i]
        parts.append(bytes(final_part))

        # Convert to base64
        import base64
        return [base64.b64encode(part).decode('ascii') for part in parts]

    @staticmethod
    def combine_secrets(parts: List[str]) -> str:
        """Combine secret parts."""
        import base64

        # Decode from base64
        decoded_parts = [base64.b64decode(part) for part in parts]

        # XOR all parts together
        result = bytearray(decoded_parts[0])
        for part in decoded_parts[1:]:
            for i in range(len(result)):
                result[i] ^= part[i]

        return result.decode('utf-8')


# Initialize database
init_features_database()
