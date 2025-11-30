"""
==============================================================================
ADVANCED FEATURES MODULE FOR STEGANOGRAPHY APPLICATION
==============================================================================

This module provides advanced steganography features beyond basic
encoding and decoding. It includes educational challenges, detection
tools, and special features for enhanced security.

Main Features:
    - Challenge Generator: Learn steganography through puzzles
    - Stego Detector: Analyze files for hidden data
    - Multi-File Stego: Split secrets across multiple files

This module uses its own database tables separate from the main
user database to keep features organized.
==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

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

# Import our existing steganography modules
import image_stego
import text_stego
import security


# ==============================================================================
# DATABASE PATH CONFIGURATION
# ==============================================================================

# Database is stored in the instance folder to match the main database location
DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'steganography.db')


# ==============================================================================
# DATABASE SETUP FOR ADVANCED FEATURES
# ==============================================================================

def init_features_database():
    """
    Initialize database tables for advanced features.
    
    This creates tables for challenges, self destructing messages,
    and multi-file operations. Safe to call multiple times.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # -------------------------------------------------------------------------
    # Challenges Table
    # Stores steganography challenges for learning
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Challenge Solutions Table
    # Records who solved which challenges and when
    # -------------------------------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenge_solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER,
            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_taken INTEGER,
            points_awarded INTEGER DEFAULT 0,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Add points_awarded column if it does not exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE challenge_solutions ADD COLUMN points_awarded INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    # -------------------------------------------------------------------------
    # Multi File Operations Table
    # Tracks secrets split across multiple files
    # -------------------------------------------------------------------------
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


# ==============================================================================
# CHALLENGE MANAGER CLASS
# ==============================================================================

class ChallengeManager:
    """
    Manages steganography learning challenges.
    
    Challenges help users learn about steganography concepts through
    interactive puzzles. They range from easy knowledge questions to
    harder problems requiring calculations.
    """

    # --------------------------------------------------------------------------
    # Challenge Creation Methods
    # --------------------------------------------------------------------------

    @staticmethod
    def create_challenge(title: str, description: str, difficulty: str,
                        secret_message: str, algorithm: str,
                        password: str = None, hints: List[str] = None) -> int:
        """
        Create a new steganography challenge.
        
        This generates actual stego data that users must decode.
        
        Args:
            title: Challenge title shown to users
            description: Full description of the challenge
            difficulty: 'easy', 'medium', or 'hard'
            secret_message: The hidden message (also the solution)
            algorithm: 'zwc' for text or 'lsb' for image
            password: Optional password for encrypted challenges
            hints: Optional list of hint strings
            
        Returns:
            The ID of the created challenge
        """
        import tempfile

        # Generate stego data based on the algorithm chosen
        if algorithm == 'zwc':
            # Create text with hidden message
            cover_text = "The quick brown fox jumps over the lazy dog. " * 10
            if password:
                encrypted = security.encrypt_message(secret_message, password)
                stego_data = text_stego.encode_message(cover_text, encrypted)
            else:
                stego_data = text_stego.encode_message(cover_text, secret_message)

        elif algorithm == 'lsb':
            # Create image with hidden message
            img = Image.new('RGB', (800, 600), color=(100, 150, 200))
            temp_path = tempfile.mktemp(suffix='.png')
            img.save(temp_path)

            stego_temp = tempfile.mktemp(suffix='.png')
            if password:
                encrypted = security.encrypt_message(secret_message, password)
                image_stego.encode_lsb(temp_path, encrypted, stego_temp)
            else:
                image_stego.encode_lsb(temp_path, secret_message, stego_temp)

            # Convert stego image to base64 for storage
            import base64
            with open(stego_temp, 'rb') as f:
                stego_data = base64.b64encode(f.read()).decode('ascii')

            # Clean up temp files
            os.unlink(temp_path)
            os.unlink(stego_temp)

        # Calculate points based on difficulty
        points_map = {'easy': 50, 'medium': 100, 'hard': 200}
        points = points_map.get(difficulty, 100)

        # Save challenge to database
        conn = sqlite3.connect(DATABASE_PATH)
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
    def create_puzzle_challenge(title: str, description: str, difficulty: str,
                               secret_message: str, algorithm: str,
                               password: str = None, hints: List[str] = None) -> int:
        """
        Create a simple text puzzle challenge (no stego generation).
        
        These are knowledge based questions where the answer is just
        typed in directly, not decoded from stego data.
        
        Args:
            title: Challenge title
            description: Question text
            difficulty: 'easy', 'medium', or 'hard'
            secret_message: The correct answer
            algorithm: Set to 'puzzle' for these
            password: Not used for puzzles
            hints: Optional list of hints
            
        Returns:
            The ID of the created challenge
        """
        points_map = {'easy': 50, 'medium': 100, 'hard': 200}
        points = points_map.get(difficulty, 100)

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # For puzzles, stego_data is just the description itself
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

    # --------------------------------------------------------------------------
    # Challenge Retrieval Methods
    # --------------------------------------------------------------------------

    @staticmethod
    def get_challenges(difficulty: str = None) -> List[Dict]:
        """
        Get list of all challenges.
        
        Args:
            difficulty: Optional filter ('easy', 'medium', 'hard')
            
        Returns:
            List of challenge info dictionaries (without solutions)
        """
        conn = sqlite3.connect(DATABASE_PATH)
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
        """
        Get specific challenge details.
        
        Returns full challenge info for displaying to user,
        but does not include the actual solution.
        
        Args:
            challenge_id: ID of challenge to get
            
        Returns:
            Challenge dictionary or None if not found
        """
        conn = sqlite3.connect(DATABASE_PATH)
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

    # --------------------------------------------------------------------------
    # Solution Submission
    # --------------------------------------------------------------------------

    @staticmethod
    def submit_solution(challenge_id: int, submitted_answer: str, user_id: int = None, start_time: float = None) -> Tuple[bool, str, int]:
        """
        Check if a submitted answer is correct.
        
        If correct, updates the challenge solved count and records
        the solution for the user. Points are awarded only once per
        challenge per user to prevent farming.
        
        Args:
            challenge_id: ID of the challenge
            submitted_answer: User's answer to check
            user_id: Optional user ID to record solution
            start_time: Optional start time to calculate duration
            
        Returns:
            Tuple of (is_correct, message, points_earned, already_solved)
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT solution, points FROM challenges WHERE id = ?', (challenge_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Challenge not found", 0, False

        correct_answer = row[0]
        points = row[1]

        # Check if the answer matches (ignoring whitespace)
        if submitted_answer.strip().lower() == correct_answer.strip().lower():
            # Correct answer - update solved count
            cursor.execute('UPDATE challenges SET solved_count = solved_count + 1 WHERE id = ?', (challenge_id,))

            # Check if this user already solved this challenge (to prevent point farming)
            points_to_award = 0
            already_solved = False
            
            if user_id:
                cursor.execute('''
                    SELECT id, points_awarded FROM challenge_solutions 
                    WHERE challenge_id = ? AND user_id = ?
                ''', (challenge_id, user_id))
                existing = cursor.fetchone()
                
                if existing and existing[1] > 0:
                    # User already earned points for this challenge
                    already_solved = True
                    points_to_award = 0
                else:
                    # First time solving - award points
                    points_to_award = points
                    
                    # Update user total points in users table
                    cursor.execute('''
                        UPDATE users SET total_points = COALESCE(total_points, 0) + ? 
                        WHERE id = ?
                    ''', (points_to_award, user_id))

            # Record the solution
            time_taken = int(time.time() - start_time) if start_time else 0
            cursor.execute('''
                INSERT INTO challenge_solutions (challenge_id, user_id, time_taken, points_awarded)
                VALUES (?, ?, ?, ?)
            ''', (challenge_id, user_id, time_taken, points_to_award))

            conn.commit()
            conn.close()

            if already_solved:
                return True, "Correct! (You already earned points for this challenge)", 0, True
            else:
                return True, f"Correct! You earned {points_to_award} points!", points_to_award, False
        else:
            conn.close()
            return False, "Incorrect solution. Try again!", 0, False

    # --------------------------------------------------------------------------
    # User Points and Leaderboard
    # --------------------------------------------------------------------------

    @staticmethod
    def get_user_points(user_id: int) -> Dict[str, Any]:
        """
        Get points information for a specific user.
        
        Args:
            user_id: The user ID to get points for
            
        Returns:
            Dictionary with total points and solved challenges count
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get total points from users table
        cursor.execute('SELECT total_points FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        total_points = row[0] if row and row[0] else 0
        
        # Get count of unique challenges solved
        cursor.execute('''
            SELECT COUNT(DISTINCT challenge_id) FROM challenge_solutions 
            WHERE user_id = ? AND points_awarded > 0
        ''', (user_id,))
        solved_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_points': total_points,
            'challenges_solved': solved_count
        }

    @staticmethod
    def get_user_solved_challenges(user_id: int) -> List[int]:
        """
        Get list of challenge IDs that a user has solved for points.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of challenge IDs
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT challenge_id FROM challenge_solutions 
            WHERE user_id = ? AND points_awarded > 0
        ''', (user_id,))
        
        solved_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return solved_ids

    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top users by points for the leaderboard.
        
        Args:
            limit: Maximum number of users to return (default 10)
            
        Returns:
            List of user dictionaries with rank, username, and points
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get top users by total points
        cursor.execute('''
            SELECT u.id, u.username, COALESCE(u.total_points, 0) as points,
                   (SELECT COUNT(DISTINCT cs.challenge_id) 
                    FROM challenge_solutions cs 
                    WHERE cs.user_id = u.id AND cs.points_awarded > 0) as challenges_solved
            FROM users u
            WHERE u.is_active = 1 AND COALESCE(u.total_points, 0) > 0
            ORDER BY points DESC, challenges_solved DESC, u.created_at ASC
            LIMIT ?
        ''', (limit,))
        
        leaderboard = []
        for rank, row in enumerate(cursor.fetchall(), 1):
            leaderboard.append({
                'rank': rank,
                'user_id': row[0],
                'username': row[1],
                'total_points': row[2],
                'challenges_solved': row[3]
            })
        
        conn.close()
        return leaderboard

    @staticmethod
    def get_user_rank(user_id: int) -> Dict[str, Any]:
        """
        Get the rank of a specific user on the leaderboard.
        
        Args:
            user_id: The user ID to get rank for
            
        Returns:
            Dictionary with user rank and total participants
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user's points
        cursor.execute('SELECT COALESCE(total_points, 0) FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        user_points = row[0] if row else 0
        
        # Count users with more points
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE is_active = 1 AND COALESCE(total_points, 0) > ?
        ''', (user_points,))
        users_above = cursor.fetchone()[0]
        
        # Count total participating users (with any points)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE is_active = 1 AND COALESCE(total_points, 0) > 0
        ''')
        total_participants = cursor.fetchone()[0]
        
        conn.close()
        
        # User rank is users_above + 1 (if they have points)
        if user_points > 0:
            rank = users_above + 1
        else:
            rank = None  # Not ranked yet
        
        return {
            'rank': rank,
            'total_participants': total_participants,
            'user_points': user_points
        }

    # --------------------------------------------------------------------------
    # Default Challenge Initialization
    # --------------------------------------------------------------------------

    @staticmethod
    def init_default_challenges():
        """
        Create the default set of learning challenges.
        
        These are simple text puzzles that test steganography knowledge.
        They do not require actual stego decoding, just answering
        questions about steganography concepts.
        """
        challenges = [
            # ==================================================================
            # EASY CHALLENGES (50 points each)
            # ==================================================================
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
            
            # ==================================================================
            # MEDIUM CHALLENGES (100 points each)
            # ==================================================================
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
            
            # ==================================================================
            # HARD CHALLENGES (200 points each)
            # ==================================================================
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

        # Create each challenge if it does not already exist
        for challenge in challenges:
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM challenges WHERE title = ?', (challenge['title'],))
                existing = cursor.fetchone()
                conn.close()
                
                if not existing:
                    ChallengeManager.create_puzzle_challenge(**challenge)
            except Exception as e:
                print(f"Error creating challenge {challenge.get('title', 'unknown')}: {e}")

    @staticmethod
    def init_fake_leaderboard_users():
        """
        Create fake users to populate the leaderboard.
        
        These are bot accounts with varying point totals to make the
        leaderboard look active and give users something to compete against.
        Includes users with low points so new users can climb the ranks easily.
        """
        import hashlib
        import os
        
        fake_users = [
            # Top tier users (harder to beat)
            {'username': 'CryptoMaster', 'points': 850},
            {'username': 'StegaNinja', 'points': 720},
            {'username': 'HiddenSeeker', 'points': 650},
            # Mid tier users
            {'username': 'BitWhisperer', 'points': 400},
            {'username': 'ShadowEncoder', 'points': 300},
            {'username': 'PixelHunter', 'points': 250},
            # Lower tier users (easy to beat with a few challenges)
            {'username': 'CodeBreaker99', 'points': 150},
            {'username': 'InvisibleInk', 'points': 100},
            {'username': 'ZeroWidthPro', 'points': 75},
            {'username': 'LSBExplorer', 'points': 50},
            # Beginner tier (very easy to surpass)
            {'username': 'NewbieCoder', 'points': 30},
            {'username': 'JustStarted', 'points': 20},
            {'username': 'FirstTimer', 'points': 10},
        ]
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        for user in fake_users:
            try:
                # Check if fake user already exists
                cursor.execute('SELECT id FROM users WHERE username = ?', (user['username'],))
                existing = cursor.fetchone()
                
                if not existing:
                    # Generate a random salt and hash for the fake user
                    # These accounts cannot actually be logged into
                    salt = os.urandom(32).hex()
                    fake_password = os.urandom(32).hex()
                    password_hash = hashlib.pbkdf2_hmac(
                        'sha256', 
                        fake_password.encode(), 
                        salt.encode(), 
                        100000
                    ).hex()
                    
                    # Create the fake user with points
                    cursor.execute('''
                        INSERT INTO users (username, email, password_hash, salt, is_active, total_points)
                        VALUES (?, ?, ?, ?, 1, ?)
                    ''', (
                        user['username'],
                        f"{user['username'].lower()}@example.com",
                        password_hash,
                        salt,
                        user['points']
                    ))
                    
            except Exception as e:
                print(f"Error creating fake user {user['username']}: {e}")
        
        conn.commit()
        conn.close()


# ==============================================================================
# STEGANOGRAPHY DETECTOR CLASS
# ==============================================================================

class StegoDetector:
    """
    Detects steganography in images and text.
    
    This class provides analysis tools to check if files might contain
    hidden data. It uses statistical analysis and pattern detection
    to estimate the likelihood of steganography being present.
    
    Detection is not perfect and can have false positives/negatives.
    Results should be interpreted as indicators, not certainties.
    """

    # --------------------------------------------------------------------------
    # Image Analysis
    # --------------------------------------------------------------------------

    @staticmethod
    def analyze_image(image_data: bytes) -> Dict[str, Any]:
        """
        Analyze an image for signs of LSB steganography.
        
        Uses multiple detection techniques including LSB randomness
        analysis, chi-square testing, and entropy measurement.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with analysis results including:
            - has_stego_probability: 0-95 probability estimate
            - indicators: List of suspicious findings
            - lsb_analysis: LSB specific metrics
            - statistical_analysis: Statistical test results
            - verdict: 'clean', 'uncertain', 'suspicious', or 'likely_stego'
        """
        # Open image and convert to array
        img = Image.open(io.BytesIO(image_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)

        # Initialize results structure
        results = {
            'has_stego_probability': 0.0,
            'indicators': [],
            'lsb_analysis': {},
            'statistical_analysis': {},
            'verdict': 'clean'
        }

        # Run LSB analysis
        lsb_score = StegoDetector._analyze_lsb_randomness(img_array)
        results['lsb_analysis'] = lsb_score

        # Run statistical tests
        stats = StegoDetector._statistical_tests(img_array)
        results['statistical_analysis'] = stats

        # Calculate overall probability based on multiple indicators
        probability = 0.0

        # Check LSB distribution uniformity
        # Steganography typically makes LSB distribution more uniform (close to 50%)
        ones_ratio = lsb_score['ones_ratio']
        if 0.48 <= ones_ratio <= 0.52:
            probability += 25
            results['indicators'].append('LSB distribution is suspiciously uniform (typical of stego)')
        
        # High randomness combined with uniform distribution is suspicious
        if lsb_score['randomness_score'] > 0.9 and 0.45 <= ones_ratio <= 0.55:
            probability += 20
            results['indicators'].append('LSB shows characteristics of hidden data')

        # Chi-square test results
        if stats['chi_square'] < 0.1:
            probability += 15
            results['indicators'].append('Statistical anomaly in pixel value pairs')
        elif stats['chi_square'] > 0.7:
            probability += 20
            results['indicators'].append('Chi-square test suggests possible hidden data')

        # Entropy analysis - stego images often have higher entropy
        if stats['entropy'] > 7.8:
            probability += 15
            results['indicators'].append('Unusually high entropy in pixel distribution')

        # Bit plane pattern anomalies
        if lsb_score['bit_plane_anomaly']:
            probability += 20
            results['indicators'].append('Anomalies detected in LSB bit plane patterns')
        
        # Sequential pattern analysis
        if lsb_score.get('sequential_anomaly', False):
            probability += 15
            results['indicators'].append('Sequential patterns suggest embedded data')

        # Cap probability at 95% (we can never be 100% certain)
        results['has_stego_probability'] = min(probability, 95)

        # Determine verdict based on probability
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
        """
        Analyze the randomness of least significant bits.
        
        Natural images have non-random LSB patterns due to smooth
        color transitions. Steganography introduces randomness.
        
        Args:
            img_array: Numpy array of image pixels
            
        Returns:
            Dictionary with LSB analysis metrics
        """
        # Extract LSB from appropriate channel
        if len(img_array.shape) == 2:
            # Grayscale image
            lsb = img_array & 1
        else:
            # RGB image - analyze blue channel (most common for stego)
            lsb_r = img_array[:, :, 0] & 1
            lsb_g = img_array[:, :, 1] & 1
            lsb_b = img_array[:, :, 2] & 1
            lsb = lsb_b

        # Calculate ratio of 1s to total bits
        ones = np.sum(lsb)
        total = lsb.size
        ratio = ones / total

        # Calculate randomness score (0.5 ratio = perfect randomness)
        randomness_score = 1.0 - abs(ratio - 0.5) * 2

        # Check for unusual patterns in bit transitions
        flat = lsb.flatten()
        transitions = np.sum(np.abs(np.diff(flat)))
        expected_transitions = (total - 1) * 0.5
        pattern_score = abs(transitions - expected_transitions) / expected_transitions if expected_transitions > 0 else 0
        
        # Analyze run lengths (consecutive same bits)
        # Natural images have longer runs, stego has shorter runs
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
        # Stego images tend to have shorter runs (more random)
        sequential_anomaly = avg_run_length < 1.8

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
        """
        Perform statistical tests for steganalysis.
        
        Args:
            img_array: Numpy array of image pixels
            
        Returns:
            Dictionary with statistical test results
        """
        # Get pixel values from blue channel (or grayscale)
        if len(img_array.shape) == 3:
            channel = img_array[:, :, 2].flatten()
        else:
            channel = img_array.flatten()

        # Calculate entropy (measure of randomness)
        hist, _ = np.histogram(channel, bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]  # Remove zeros to avoid log(0)
        entropy = -np.sum(hist * np.log2(hist))

        # Chi-square like test for pixel value distribution
        expected = len(channel) / 256
        chi_square = np.sum((hist * len(channel) - expected) ** 2 / expected) / expected
        chi_normalized = min(chi_square / 100, 1.0)

        return {
            'entropy': float(entropy),
            'chi_square': float(chi_normalized),
            'unique_values': int(np.unique(channel).size)
        }

    # --------------------------------------------------------------------------
    # Text Analysis
    # --------------------------------------------------------------------------

    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        Analyze text for signs of ZWC steganography.
        
        Looks for zero-width Unicode characters that might be hiding
        data. These characters are invisible but detectable.
        
        Args:
            text: Text string to analyze
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            'has_stego_probability': 0.0,
            'indicators': [],
            'zero_width_chars': 0,
            'verdict': 'clean'
        }

        # Check for common zero-width characters
        zwc_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        zwc_count = sum(text.count(char) for char in zwc_chars)

        results['zero_width_chars'] = zwc_count

        # Any ZWC characters present is a strong indicator
        if zwc_count > 0:
            probability = min(zwc_count * 10, 95)
            results['has_stego_probability'] = probability
            results['indicators'].append(f'Found {zwc_count} zero-width characters')
            results['verdict'] = 'likely_stego'

        return results


# ==============================================================================
# MULTI-FILE STEGANOGRAPHY CLASS
# ==============================================================================

class MultiFileStego:
    """
    Split secrets across multiple files.
    
    Uses XOR-based secret sharing to split a message into parts
    that can only be combined when ALL parts are present. This
    provides extra security because finding one part reveals nothing.
    """

    @staticmethod
    def split_secret(secret: str, num_parts: int) -> List[str]:
        """
        Split a secret into multiple parts using XOR.
        
        All parts are required to reconstruct the original.
        Each individual part reveals nothing about the secret.
        
        Args:
            secret: The secret message to split
            num_parts: Number of parts to create (2-10)
            
        Returns:
            List of base64 encoded part strings
        """
        secret_bytes = secret.encode('utf-8')

        # Generate random parts for all but the last one
        parts = []
        for i in range(num_parts - 1):
            parts.append(secrets.token_bytes(len(secret_bytes)))

        # Calculate final part using XOR of all previous parts with secret
        final_part = bytearray(secret_bytes)
        for part in parts:
            for i in range(len(final_part)):
                final_part[i] ^= part[i]
        parts.append(bytes(final_part))

        # Convert all parts to base64 for safe storage/transmission
        import base64
        return [base64.b64encode(part).decode('ascii') for part in parts]

    @staticmethod
    def combine_secrets(parts: List[str]) -> str:
        """
        Combine secret parts back into original message.
        
        XORs all parts together to reconstruct the secret.
        All original parts must be provided in any order.
        
        Args:
            parts: List of base64 encoded part strings
            
        Returns:
            The original secret message
        """
        import base64

        # Decode all parts from base64
        decoded_parts = [base64.b64decode(part) for part in parts]

        # XOR all parts together
        result = bytearray(decoded_parts[0])
        for part in decoded_parts[1:]:
            for i in range(len(result)):
                result[i] ^= part[i]

        return result.decode('utf-8')


# ==============================================================================
# MODULE INITIALIZATION
# ==============================================================================

# Initialize the features database when module is imported
init_features_database()


# ==============================================================================
# END OF FILE
# ==============================================================================
