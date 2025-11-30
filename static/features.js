/**
 * SteganographyPro - Advanced Features Module
 * Handles: Challenges, Multi-File Stego, Scanner/Detector
 */

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize dropzones only once
    initAllDropzones();
});

function initAllDropzones() {
    // Scanner dropzone
    const scannerDropzone = document.getElementById('scanner-dropzone');
    if (scannerDropzone) {
        setupDropzone(scannerDropzone, handleScannerDrop);
    }
    
    // Multi-file decode dropzone
    const mfDropzone = document.getElementById('mf-dropzone');
    if (mfDropzone) {
        setupDropzone(mfDropzone, (e) => {
            handleMultiFileUpload({ target: { files: e.dataTransfer.files } });
        });
    }
    
    // Multi-file encode custom images dropzone
    const mfCustomSection = document.getElementById('mf-custom-upload-section');
    if (mfCustomSection) {
        const dropzone = mfCustomSection.querySelector('.upload-zone');
        if (dropzone) {
            setupDropzone(dropzone, (e) => {
                handleMfEncodeUpload({ target: { files: e.dataTransfer.files } });
            });
        }
    }
    
    // Image encode/decode dropzones (both pages)
    document.querySelectorAll('#page-image-encode .upload-zone, #page-image-decode .upload-zone').forEach(dropzone => {
        setupDropzone(dropzone, (e) => {
            const input = dropzone.querySelector('input[type="file"]');
            if (input && e.dataTransfer.files[0]) {
                const dt = new DataTransfer();
                dt.items.add(e.dataTransfer.files[0]);
                input.files = dt.files;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    });
}

function setupDropzone(dropzone, onDropHandler) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, { passive: false });
    });
    
    dropzone.addEventListener('dragenter', () => dropzone.classList.add('dragover'));
    dropzone.addEventListener('dragover', () => dropzone.classList.add('dragover'));
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
        dropzone.classList.remove('dragover');
        onDropHandler(e);
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function escapeHtml(s) {
    if (!s) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };
    return s.replace(/[&<>"'`]/g, ch => map[ch]);
}

function showToastFeatures(msg, type = 'info') {
    // Use the global showToast from index.html if available
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    } else {
        console.log(`[${type}] ${msg}`);
    }
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// ============================================
// MULTI-FILE MODE TOGGLE
// ============================================
function setMultiFileMode(mode) {
    const encodeSection = document.getElementById('mf-encode-section');
    const decodeSection = document.getElementById('mf-decode-section');
    const encodeModeBtn = document.getElementById('mf-mode-encode');
    const decodeModeBtn = document.getElementById('mf-mode-decode');
    
    if (mode === 'encode') {
        encodeSection.style.display = 'block';
        decodeSection.style.display = 'none';
        encodeModeBtn?.classList.add('active');
        decodeModeBtn?.classList.remove('active');
    } else {
        encodeSection.style.display = 'none';
        decodeSection.style.display = 'block';
        encodeModeBtn?.classList.remove('active');
        decodeModeBtn?.classList.add('active');
    }
    
    // Clear results
    document.getElementById('mf-results').innerHTML = '';
}

function setMfParts(num) {
    document.getElementById('mf-parts').value = num;
    document.querySelectorAll('.part-btn').forEach(btn => {
        btn.classList.toggle('active', parseInt(btn.textContent) === num);
    });
    
    // Clear custom images if count exceeds new parts limit
    if (mfCustomImages.length > num) {
        mfCustomImages = mfCustomImages.slice(0, num);
        refreshMfCustomPreview();
        showToast(`Custom images trimmed to ${num}`, 'info');
    }
    
    // Update hint text
    const hint = document.querySelector('#mf-custom-upload-section .upload-hint');
    if (hint) {
        hint.textContent = `Upload exactly ${num} images for the ${num} parts`;
    }
}

// ============================================
// MULTI-FILE IMAGE SOURCE TOGGLE
// ============================================
let mfImageSource = 'generated';
let mfCustomImages = [];

function setMfImageSource(source) {
    mfImageSource = source;
    
    const generatedBtn = document.getElementById('mf-source-generated');
    const customBtn = document.getElementById('mf-source-custom');
    const customSection = document.getElementById('mf-custom-upload-section');
    
    if (source === 'generated') {
        generatedBtn?.classList.add('active');
        customBtn?.classList.remove('active');
        customSection.style.display = 'none';
    } else {
        generatedBtn?.classList.remove('active');
        customBtn?.classList.add('active');
        customSection.style.display = 'block';
    }
}

function handleMfEncodeUpload(e) {
    const files = e.target?.files || e.dataTransfer?.files;
    if (!files) return;
    
    const parts = parseInt(document.getElementById('mf-parts')?.value) || 3;
    const preview = document.getElementById('mf-encode-preview');
    
    // Limit to the number of parts selected
    const remainingSlots = parts - mfCustomImages.length;
    if (remainingSlots <= 0) {
        showToast(`Maximum ${parts} images allowed (based on parts selected)`, 'warning');
        return;
    }
    
    const filesToProcess = Array.from(files).slice(0, remainingSlots);
    
    filesToProcess.forEach(file => {
        if (!file.type.startsWith('image/')) return;
        
        const reader = new FileReader();
        reader.onload = (ev) => {
            const b64 = ev.target.result.split(',')[1];
            mfCustomImages.push(b64);
            refreshMfCustomPreview();
        };
        reader.readAsDataURL(file);
    });
    
    if (files.length > remainingSlots) {
        showToast(`Only ${remainingSlots} more image(s) allowed`, 'warning');
    }
}

function copyMfDecodedMessage() {
    const msgEl = document.getElementById('mf-decoded-message');
    if (msgEl) {
        const text = msgEl.textContent || msgEl.innerText || '';
        if (!text.trim()) {
            showToast('❌ Nothing to copy', 'error');
            return;
        }
        
        // Try modern clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('📋 Copied to clipboard!', 'success');
            }).catch(() => {
                // Fallback for clipboard API failure
                fallbackCopyText(text);
            });
        } else {
            // Fallback for older browsers
            fallbackCopyText(text);
        }
    } else {
        showToast('❌ No message to copy', 'error');
    }
}

// Fallback copy function for older browsers or permission issues
function fallbackCopyText(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    textarea.style.top = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast('📋 Copied to clipboard!', 'success');
        } else {
            showToast('❌ Copy failed', 'error');
        }
    } catch (err) {
        showToast('❌ Copy not supported', 'error');
    }
    
    document.body.removeChild(textarea);
}

function removeMfCustomImage(index) {
    mfCustomImages.splice(index, 1);
    refreshMfCustomPreview();
}

function refreshMfCustomPreview() {
    const preview = document.getElementById('mf-encode-preview');
    preview.innerHTML = mfCustomImages.map((b64, i) => `
        <div class="mf-preview-item">
            <img src="data:image/png;base64,${b64}" alt="Cover ${i + 1}" />
            <span>Cover ${i + 1}</span>
            <button class="mf-remove-btn" onclick="removeMfCustomImage(${i})">×</button>
        </div>
    `).join('');
}

// ============================================
// CHALLENGES SYSTEM
// ============================================
let currentFilter = '';
let challengesCache = [];

async function loadChallenges(difficulty = '') {
    currentFilter = difficulty;
    const container = document.getElementById('challenges-grid');
    if (!container) return;
    
    // Load leaderboard and user points when challenges page loads
    refreshPointsDisplay();
    
    // Update filter button states
    document.querySelectorAll('.btn-filter').forEach(btn => {
        const btnDiff = btn.textContent.toLowerCase().replace('all', '');
        btn.classList.toggle('active', btnDiff === difficulty || (btnDiff === '' && difficulty === ''));
    });
    
    container.innerHTML = `
        <div class="challenge-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 16px; color: var(--text-muted);">Loading challenges...</p>
        </div>
    `;
    
    try {
        const url = difficulty ? `/api/challenges?difficulty=${difficulty}` : '/api/challenges';
        const res = await fetch(url);
        const data = await res.json();
        challengesCache = data.challenges || [];
        
        if (!challengesCache.length) {
            container.innerHTML = `
                <div class="challenge-card" style="grid-column: 1/-1; text-align: center; padding: 60px;">
                    <div style="font-size: 3rem; margin-bottom: 16px;">🎯</div>
                    <h3 style="margin: 0 0 8px 0;">No Challenges Yet</h3>
                    <p style="color: var(--text-muted); margin: 0;">Check back later for new steganography puzzles!</p>
                </div>
            `;
            return;
        }
        
        renderChallengesList(challengesCache);
    } catch (err) {
        container.innerHTML = `
            <div class="challenge-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">⚠️</div>
                <p style="color: var(--text-muted);">Failed to load challenges. Please try again.</p>
                <button class="btn-primary" onclick="loadChallenges('${difficulty}')" style="margin-top: 12px;">Retry</button>
            </div>
        `;
    }
}

function renderChallengesList(challenges) {
    const container = document.getElementById('challenges-grid');
    const diffConfig = {
        easy: { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', icon: '🌱' },
        medium: { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', icon: '🔥' },
        hard: { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', icon: '💀' }
    };
    
    container.innerHTML = challenges.map(c => {
        const conf = diffConfig[c.difficulty] || diffConfig.medium;
        const isPuzzle = c.algorithm === 'puzzle';
        const typeIcon = isPuzzle ? '🧩' : (c.algorithm === 'zwc' ? '📝' : '🖼️');
        const typeLabel = isPuzzle ? 'Quiz' : (c.algorithm === 'zwc' ? 'Text' : 'Image');
        
        // Truncate description for card view
        const shortDesc = (c.description || 'Test your steganography knowledge!').substring(0, 80) + (c.description && c.description.length > 80 ? '...' : '');
        
        return `
            <div class="challenge-card" onclick="openChallenge(${c.id})">
                <div class="challenge-header">
                    <span class="challenge-badge" style="background: ${conf.bg}; color: ${conf.color};">
                        ${conf.icon} ${c.difficulty.toUpperCase()}
                    </span>
                    <span class="challenge-badge" style="background: rgba(124, 58, 237, 0.1); color: #7c3aed;">
                        ${typeIcon} ${typeLabel}
                    </span>
                    <span class="challenge-points">🏆 ${c.points} pts</span>
                </div>
                <h3 class="challenge-title">${escapeHtml(c.title)}</h3>
                <p class="challenge-desc">${escapeHtml(shortDesc)}</p>
                <div class="challenge-footer">
                    <span class="challenge-solves">✓ ${c.solved_count || 0} solves</span>
                    <span class="challenge-action">Try it →</span>
                </div>
            </div>
        `;
    }).join('');
}

function filterChallenges(difficulty) {
    loadChallenges(difficulty);
}
async function openChallenge(id) {
    const container = document.getElementById('challenges-grid');
    container.innerHTML = `
        <div class="challenge-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 16px; color: var(--text-muted);">Loading challenge...</p>
        </div>
    `;
    
    try {
        const res = await fetch(`/api/challenges/${id}`);
        const data = await res.json();
        const c = data.challenge;
        
        const diffConfig = {
            easy: { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', icon: '🌱' },
            medium: { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', icon: '🔥' },
            hard: { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', icon: '💀' }
        };
        const conf = diffConfig[c.difficulty] || diffConfig.medium;
        
        // Determine if it's a puzzle or stego challenge
        const isPuzzle = c.algorithm === 'puzzle';
        const placeholderText = isPuzzle ? 'Enter your answer...' : 'Enter the hidden message you found...';
        
        container.innerHTML = `
            <div class="challenge-detail" style="grid-column: 1/-1;">
                <button class="btn-back" onclick="loadChallenges('${currentFilter}')">← Back to Challenges</button>
                
                <div class="challenge-detail-header">
                    <div>
                        <h2 style="margin: 0 0 12px 0; font-size: 1.75rem;">${escapeHtml(c.title)}</h2>
                        <span class="challenge-badge" style="background: ${conf.bg}; color: ${conf.color};">
                            ${conf.icon} ${c.difficulty.toUpperCase()}
                        </span>
                        <span class="challenge-badge" style="background: rgba(124, 58, 237, 0.1); color: #7c3aed; margin-left: 8px;">
                            ${isPuzzle ? '🧩 Knowledge Quiz' : (c.algorithm === 'zwc' ? '📝 Text Stego' : '🖼️ Image Stego')}
                        </span>
                    </div>
                    <div class="challenge-points-large">🏆 ${c.points} pts</div>
                </div>
                
                <div style="background: var(--bg-tertiary); padding: 24px; border-radius: 12px; margin: 20px 0; border-left: 4px solid var(--primary-color);">
                    <h3 style="margin: 0 0 12px 0; color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">📝 Challenge Question</h3>
                    <p style="color: var(--text-primary); font-size: 1.2rem; line-height: 1.8; margin: 0; white-space: pre-wrap;">
                        ${escapeHtml(c.description || '')}
                    </p>
                </div>
                
                ${c.hints && c.hints.length ? `
                <div class="hints-section">
                    <details>
                        <summary>💡 Need a hint? (${c.hints.length} available)</summary>
                        <ul class="hints-list">
                            ${c.hints.map((h, i) => `<li><strong>Hint ${i + 1}:</strong> ${escapeHtml(h)}</li>`).join('')}
                        </ul>
                    </details>
                </div>
                ` : ''}
                
                <div class="solution-section">
                    <label class="input-label">Your Answer</label>
                    <div class="solution-input-group">
                        <input type="text" id="challenge-solution-${c.id}" class="input-field" 
                               placeholder="${placeholderText}" 
                               onkeydown="if(event.key==='Enter')submitChallenge(${c.id})" />
                        <button class="btn-primary" onclick="submitChallenge(${c.id})">
                            Submit Answer
                        </button>
                    </div>
                </div>
                
                <div id="challenge-result-${c.id}" class="challenge-result"></div>
            </div>
        `;
        
        // Focus the input
        document.getElementById(`challenge-solution-${c.id}`)?.focus();
    } catch (err) {
        container.innerHTML = `
            <div class="challenge-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">⚠️</div>
                <p style="color: var(--text-muted);">Failed to load challenge.</p>
                <button class="btn-primary" onclick="loadChallenges('${currentFilter}')" style="margin-top: 12px;">Back to List</button>
            </div>
        `;
    }
}

async function submitChallenge(id) {
    const input = document.getElementById(`challenge-solution-${id}`);
    const result = document.getElementById(`challenge-result-${id}`);
    const solution = input.value.trim();
    
    if (!solution) {
        result.innerHTML = `<div class="result-error">Please enter your solution.</div>`;
        input.focus();
        return;
    }
    
    result.innerHTML = `<div class="result-loading">Checking your answer...</div>`;
    
    // Get auth token from localStorage (stored as JSON object)
    let token = null;
    try {
        const authData = localStorage.getItem('auth');
        if (authData) {
            const parsed = JSON.parse(authData);
            token = parsed.accessToken;
        }
    } catch (e) {
        console.error('Error parsing auth data:', e);
    }
    
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const res = await fetch(`/api/challenges/${id}/solve`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ solution, start_time: Date.now() / 1000 })
        });
        const data = await res.json();
        
        if (data.correct) {
            // Build the success message based on whether points were awarded
            let pointsMessage = '';
            if (data.already_solved) {
                pointsMessage = `<p>You already solved this challenge before.</p>`;
            } else if (token && data.points > 0) {
                pointsMessage = `<p>You earned <strong>${data.points} points</strong>!</p>`;
            } else if (!token) {
                pointsMessage = `<p style="font-size: 0.9rem; color: var(--text-muted);">Log in to save your points!</p>`;
            } else {
                pointsMessage = `<p>${data.message}</p>`;
            }
            
            result.innerHTML = `
                <div class="result-success">
                    <div class="result-icon">🎉</div>
                    <div class="result-content">
                        <strong>Correct!</strong>
                        ${pointsMessage}
                    </div>
                </div>
            `;
            showToast('Challenge completed! 🎉', 'success');
            
            // Refresh leaderboard and user points after solving
            refreshPointsDisplay();
        } else {
            result.innerHTML = `
                <div class="result-error">
                    <div class="result-icon">❌</div>
                    <div class="result-content">
                        <strong>Not quite right</strong>
                        <p>${data.message || 'Try again!'}</p>
                    </div>
                </div>
            `;
            input.focus();
            input.select();
        }
    } catch (err) {
        result.innerHTML = `<div class="result-error">Submission failed. Please try again.</div>`;
    }
}

// ============================================
// LEADERBOARD AND POINTS SYSTEM
// ============================================

// Get the current user's username from localStorage
function getCurrentUsername() {
    try {
        const authData = localStorage.getItem('auth');
        if (authData) {
            const parsed = JSON.parse(authData);
            return parsed.username || null;
        }
    } catch (e) {
        console.error('Error getting username:', e);
    }
    return null;
}

// Load the leaderboard from the server
// Shows top users ranked by total points earned from challenges
async function loadLeaderboard() {
    const container = document.getElementById('leaderboard-container');
    if (!container) return;
    
    container.innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div class="loading-spinner"></div>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Loading...</p>
        </div>
    `;
    
    // Get current user's username for highlighting
    const currentUsername = getCurrentUsername();
    
    try {
        const res = await fetch('/api/leaderboard?limit=10');
        const data = await res.json();
        
        if (!data.leaderboard || data.leaderboard.length === 0) {
            container.innerHTML = `
                <div class="leaderboard-empty">
                    <div class="leaderboard-empty-icon">🏆</div>
                    <p>No one on the leaderboard yet.</p>
                    <p style="font-size: 0.85rem;">Complete challenges to be the first!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = data.leaderboard.map((user, index) => {
            const rank = index + 1;
            const topClass = rank <= 3 ? `top-${rank}` : '';
            const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
            // Highlight if this is the current logged-in user
            const isCurrentUser = currentUsername && user.username.toLowerCase() === currentUsername.toLowerCase();
            const currentUserClass = isCurrentUser ? 'current-user' : '';
            
            return `
                <div class="leaderboard-entry ${topClass} ${currentUserClass}">
                    <div class="leaderboard-rank">${medal || rank}</div>
                    <div class="leaderboard-user">
                        <div class="leaderboard-username">${escapeHtml(user.username)}</div>
                    </div>
                    <div class="leaderboard-points">${user.total_points}</div>
                </div>
            `;
        }).join('');
        
    } catch (err) {
        console.error('Error loading leaderboard:', err);
        container.innerHTML = `
            <div class="leaderboard-empty">
                <p style="color: var(--text-muted);">Could not load leaderboard.</p>
                <button class="btn-small" onclick="loadLeaderboard()">Retry</button>
            </div>
        `;
    }
}

// Load the current user's points and show the points banner
// Only shows when the user is logged in
async function loadUserPoints() {
    const banner = document.getElementById('user-points-banner');
    if (!banner) return;
    
    // Get auth token from localStorage (stored as JSON object)
    let token = null;
    try {
        const authData = localStorage.getItem('auth');
        if (authData) {
            const parsed = JSON.parse(authData);
            token = parsed.accessToken;
        }
    } catch (e) {
        console.error('Error parsing auth data:', e);
    }
    
    if (!token) {
        banner.style.display = 'none';
        return;
    }
    
    try {
        const res = await fetch('/api/points', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!res.ok) {
            banner.style.display = 'none';
            return;
        }
        
        const data = await res.json();
        
        // Update the points display
        document.getElementById('user-total-points').textContent = data.total_points || 0;
        document.getElementById('user-challenges-solved').textContent = data.challenges_solved || 0;
        document.getElementById('user-rank').textContent = data.rank ? `#${data.rank}` : '#-';
        
        banner.style.display = 'block';
        
    } catch (err) {
        console.error('Error loading user points:', err);
        banner.style.display = 'none';
    }
}

// Refresh both leaderboard and user points
// Called after solving a challenge or when challenges page loads
function refreshPointsDisplay() {
    loadLeaderboard();
    loadUserPoints();
}

// ============================================
// MULTI-FILE STEGANOGRAPHY
// ============================================
let multiFileImages = [];

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleMultiFileDrop(e) {
    const files = e.dataTransfer.files;
    handleMultiFileUpload({ target: { files } });
}

function handleMultiFileUpload(e) {
    const files = e.target?.files || e.dataTransfer?.files;
    if (!files) return;
    
    const preview = document.getElementById('mf-preview');
    
    Array.from(files).forEach(file => {
        if (!file.type.startsWith('image/')) return;
        
        const reader = new FileReader();
        reader.onload = (ev) => {
            const b64 = ev.target.result.split(',')[1];
            multiFileImages.push(b64);
            
            preview.innerHTML += `
                <div class="mf-preview-item">
                    <img src="${ev.target.result}" alt="Part ${multiFileImages.length}" />
                    <span>Part ${multiFileImages.length}</span>
                    <button class="mf-remove-btn" onclick="removeMultiFile(${multiFileImages.length - 1})">×</button>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    });
}

function removeMultiFile(index) {
    multiFileImages.splice(index, 1);
    refreshMultiFilePreview();
}

function refreshMultiFilePreview() {
    const preview = document.getElementById('mf-preview');
    preview.innerHTML = multiFileImages.map((b64, i) => `
        <div class="mf-preview-item">
            <img src="data:image/png;base64,${b64}" alt="Part ${i + 1}" />
            <span>Part ${i + 1}</span>
            <button class="mf-remove-btn" onclick="removeMultiFile(${i})">×</button>
        </div>
    `).join('');
}

function clearMultiFiles() {
    multiFileImages = [];
    document.getElementById('mf-preview').innerHTML = '';
    document.getElementById('mf-results').innerHTML = '';
}

async function multiFileEncode() {
    const secret = document.getElementById('mf-secret').value.trim();
    const parts = parseInt(document.getElementById('mf-parts').value) || 3;
    const results = document.getElementById('mf-results');
    
    if (!secret) {
        results.innerHTML = `<div class="result-error">Please enter a secret message to hide.</div>`;
        return;
    }
    
    if (parts < 2 || parts > 10) {
        results.innerHTML = `<div class="result-error">Number of parts must be between 2 and 10.</div>`;
        return;
    }
    
    // Check if using custom images and validate count
    if (mfImageSource === 'custom') {
        if (mfCustomImages.length < parts) {
            results.innerHTML = `<div class="result-error">Please upload at least ${parts} cover images (you have ${mfCustomImages.length}).</div>`;
            return;
        }
    }
    
    results.innerHTML = `
        <div class="result-loading">
            <div class="loading-spinner"></div>
            <span>Generating ${parts} steganographic parts...</span>
        </div>
    `;
    
    try {
        // Get cover images based on source selection
        let coverImages = [];
        
        if (mfImageSource === 'custom') {
            // Use user-uploaded images
            coverImages = mfCustomImages.slice(0, parts);
        } else {
            // Generate cover images with gradients
            const colors = [
                [100, 150, 200], [150, 100, 180], [80, 170, 150],
                [200, 120, 100], [130, 180, 90], [180, 140, 170],
                [90, 160, 180], [170, 90, 140], [140, 170, 100], [160, 130, 190]
            ];
            
            for (let i = 0; i < parts; i++) {
                coverImages.push(await generateCoverImage(400, 300, colors[i % colors.length]));
            }
        }
        
        const res = await fetch('/api/multi-encode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ secret_message: secret, num_parts: parts, cover_images: coverImages })
        });
        
        const data = await res.json();
        
        if (!data.success) {
            results.innerHTML = `<div class="result-error">${data.error || 'Encoding failed'}</div>`;
            return;
        }
        
        const images = data.stego_images || [];
        results.innerHTML = `
            <div class="result-success" style="margin-bottom: 16px;">
                <strong>✓ Secret split into ${images.length} parts!</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.9rem; opacity: 0.9;">All parts are required to recover the message.</p>
            </div>
            <div class="mf-results-grid">
                ${images.map((img, i) => `
                    <div class="mf-result-item">
                        <img src="data:image/png;base64,${img.stego_image || img}" alt="Part ${i + 1}" />
                        <div class="mf-result-info">
                            <span>Part ${i + 1} of ${images.length}</span>
                            <button class="btn-download" onclick="downloadBase64('stego_part_${i + 1}.png', '${img.stego_image || img}')">
                                ⬇ Download
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <button class="btn-primary" onclick="downloadAllParts()" style="margin-top: 16px; width: 100%;">
                ⬇ Download All Parts
            </button>
        `;
        
        // Store for batch download
        window.lastEncodedParts = images;
    } catch (err) {
        results.innerHTML = `<div class="result-error">Error: ${err.message}</div>`;
    }
}

async function multiFileDecode() {
    const results = document.getElementById('mf-results');
    
    if (multiFileImages.length < 2) {
        results.innerHTML = `<div class="result-error">Please upload at least 2 image parts to decode.</div>`;
        return;
    }
    
    results.innerHTML = `
        <div class="result-loading">
            <div class="loading-spinner"></div>
            <span>Reconstructing secret from ${multiFileImages.length} parts...</span>
        </div>
    `;
    
    try {
        // Convert bare base64 strings to objects with 'image' key
        const stegoImageObjects = multiFileImages.map(img => ({ image: img }));
        
        const res = await fetch('/api/multi-decode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stego_images: stegoImageObjects })
        });
        
        const data = await res.json();
        
        if (data.success && data.secret_message) {
            const secretMsg = data.secret_message;
            results.innerHTML = `
                <div class="result-success">
                    <strong>✓ Secret Recovered!</strong>
                </div>
                <div class="decoded-message">
                    <label>Hidden Message:</label>
                    <div class="message-content" id="mf-decoded-message">${escapeHtml(secretMsg)}</div>
                    <button class="btn-copy-styled" onclick="copyMfDecodedMessage()">
                        📋 Copy to Clipboard
                    </button>
                </div>
            `;
        } else {
            results.innerHTML = `<div class="result-error">${data.error || 'Decoding failed. Make sure you have all parts.'}\n<small>Ensure you uploaded all the original parts created together.</small></div>`;
        }
    } catch (err) {
        results.innerHTML = `<div class="result-error">Error: ${err.message}</div>`;
    }
}

function generateCoverImage(w, h, rgb) {
    return new Promise(resolve => {
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        
        // Create gradient background
        const gradient = ctx.createLinearGradient(0, 0, w, h);
        gradient.addColorStop(0, `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`);
        gradient.addColorStop(1, `rgb(${rgb[0] + 30}, ${rgb[1] - 20}, ${rgb[2] + 10})`);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, w, h);
        
        // Add some noise for better hiding
        const imageData = ctx.getImageData(0, 0, w, h);
        for (let i = 0; i < imageData.data.length; i += 4) {
            const noise = Math.random() * 10 - 5;
            imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + noise));
            imageData.data[i + 1] = Math.max(0, Math.min(255, imageData.data[i + 1] + noise));
            imageData.data[i + 2] = Math.max(0, Math.min(255, imageData.data[i + 2] + noise));
        }
        ctx.putImageData(imageData, 0, 0);
        
        resolve(canvas.toDataURL('image/png').split(',')[1]);
    });
}

function downloadBase64(filename, b64) {
    const link = document.createElement('a');
    link.href = 'data:image/png;base64,' + b64;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
}

function downloadAllParts() {
    if (!window.lastEncodedParts) return;
    window.lastEncodedParts.forEach((img, i) => {
        setTimeout(() => {
            downloadBase64(`stego_part_${i + 1}.png`, img.stego_image || img);
        }, i * 200);
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    });
}

// ============================================
// SCANNER / DETECTOR
// ============================================
let scannerImageData = null;

function handleScannerDrop(e) {
    const files = e.dataTransfer.files;
    if (files[0]) {
        handleScannerUpload({ target: { files } });
    }
}

function switchScannerTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.scanner-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.scanner-tab[onclick*="${tab}"]`)?.classList.add('active');
    
    // Update sections
    document.getElementById('scanner-image-section')?.classList.toggle('active', tab === 'image');
    document.getElementById('scanner-text-section')?.classList.toggle('active', tab === 'text');
}

function handleScannerUpload(e) {
    const file = e.target?.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (ev) => {
        scannerImageData = ev.target.result.split(',')[1];
        
        const preview = document.getElementById('scanner-preview');
        preview.innerHTML = `
            <div class="scanner-preview-content">
                <img src="${ev.target.result}" alt="Uploaded image" />
                <div class="scanner-preview-info">
                    <strong>${escapeHtml(file.name)}</strong>
                    <span>${(file.size / 1024).toFixed(1)} KB</span>
                </div>
            </div>
        `;
        
        // Show the dropzone with preview state
        document.getElementById('scanner-dropzone').classList.add('has-file');
    };
    reader.readAsDataURL(file);
}

function handleScannerFile(input) {
    handleScannerUpload({ target: input });
}

async function scanImage() {
    const output = document.getElementById('scanner-output');
    
    if (!scannerImageData) {
        output.innerHTML = `<div class="result-error">Please upload an image to analyze.</div>`;
        return;
    }
    
    output.innerHTML = `
        <div class="result-loading">
            <div class="loading-spinner"></div>
            <span>Running statistical analysis...</span>
        </div>
    `;
    
    try {
        const res = await fetch('/api/detect/image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: scannerImageData })
        });
        
        const data = await res.json();
        const analysis = data.analysis || {};
        const prob = analysis.has_stego_probability || 0;
        const verdict = analysis.verdict || 'unknown';
        const indicators = analysis.indicators || [];
        
        // Determine color and icon based on probability
        let statusColor, statusIcon, statusText;
        if (prob < 25) {
            statusColor = '#10b981';
            statusIcon = '✓';
            statusText = 'Likely Clean';
        } else if (prob < 50) {
            statusColor = '#f59e0b';
            statusIcon = '?';
            statusText = 'Uncertain';
        } else if (prob < 75) {
            statusColor = '#f97316';
            statusIcon = '⚠';
            statusText = 'Suspicious';
        } else {
            statusColor = '#ef4444';
            statusIcon = '!';
            statusText = 'Likely Contains Hidden Data';
        }
        
        output.innerHTML = `
            <div class="scanner-result">
                <div class="scanner-result-header">
                    <div class="scanner-probability" style="--prob-color: ${statusColor}">
                        <svg class="probability-ring" viewBox="0 0 36 36">
                            <path class="probability-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <path class="probability-fill" stroke="${statusColor}" stroke-dasharray="${prob}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                        <div class="probability-text">
                            <span class="probability-value">${prob.toFixed(0)}%</span>
                            <span class="probability-label">Probability</span>
                        </div>
                    </div>
                    <div class="scanner-verdict">
                        <span class="verdict-icon" style="background: ${statusColor}">${statusIcon}</span>
                        <div class="verdict-text">
                            <strong>${statusText}</strong>
                            <span>${verdict.replace(/_/g, ' ')}</span>
                        </div>
                    </div>
                </div>
                
                ${indicators.length ? `
                <div class="scanner-indicators">
                    <h4>Detection Indicators</h4>
                    <ul>
                        ${indicators.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <details class="scanner-details">
                    <summary>View Full Analysis Data</summary>
                    <pre>${JSON.stringify(analysis, null, 2)}</pre>
                </details>
            </div>
        `;
    } catch (err) {
        output.innerHTML = `<div class="result-error">Analysis failed: ${err.message}</div>`;
    }
}

async function scanText() {
    const textInput = document.getElementById('scanner-text');
    const output = document.getElementById('scanner-text-output');
    const text = textInput?.value || '';
    
    if (!text.trim()) {
        output.innerHTML = `<div class="result-error">Please enter text to analyze.</div>`;
        return;
    }
    
    output.innerHTML = `
        <div class="result-loading">
            <div class="loading-spinner"></div>
            <span>Scanning for hidden characters...</span>
        </div>
    `;
    
    try {
        const res = await fetch('/api/detect/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        const data = await res.json();
        const analysis = data.analysis || {};
        const zwc = analysis.zero_width_chars || 0;
        const verdict = analysis.verdict || 'clean';
        
        const isClean = zwc === 0;
        const statusColor = isClean ? '#10b981' : '#ef4444';
        
        output.innerHTML = `
            <div class="scanner-result">
                <div class="scanner-result-header">
                    <div class="text-scan-stat">
                        <span class="stat-value" style="color: ${statusColor}">${zwc}</span>
                        <span class="stat-label">Zero-Width Characters</span>
                    </div>
                    <div class="scanner-verdict">
                        <span class="verdict-icon" style="background: ${statusColor}">${isClean ? '✓' : '!'}</span>
                        <div class="verdict-text">
                            <strong>${isClean ? 'Text is Clean' : 'Hidden Data Detected!'}</strong>
                            <span>${verdict.replace(/_/g, ' ')}</span>
                        </div>
                    </div>
                </div>
                
                ${!isClean ? `
                <div class="scanner-warning">
                    <strong>⚠️ This text contains invisible characters</strong>
                    <p>There may be a hidden message encoded using zero-width character steganography.</p>
                </div>
                ` : ''}
            </div>
        `;
    } catch (err) {
        output.innerHTML = `<div class="result-error">Analysis failed: ${err.message}</div>`;
    }
}

function clearScannerImage() {
    scannerImageData = null;
    document.getElementById('scanner-preview').innerHTML = '';
    document.getElementById('scanner-output').innerHTML = '';
    document.getElementById('scanner-dropzone')?.classList.remove('has-file');
}

// ============================================
// ADDITIONAL STYLES (injected dynamically)
// ============================================
const featureStyles = document.createElement('style');
featureStyles.textContent = `
    /* Loading spinner */
    .loading-spinner {
        width: 24px;
        height: 24px;
        border: 3px solid var(--border-color);
        border-top-color: var(--purple-600);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: inline-block;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Result states */
    .result-loading {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
        background: var(--bg-tertiary);
        border-radius: 8px;
        color: var(--text-secondary);
    }
    
    .result-success {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #059669;
        padding: 16px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .result-error {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #dc2626;
        padding: 16px;
        border-radius: 8px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
        animation: fadeInError 0.3s ease;
    }
    
    .result-error small {
        display: block;
        margin-top: 8px;
        opacity: 0.8;
        font-size: 0.85rem;
    }
    
    @keyframes fadeInError {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Styled Copy Button */
    .btn-copy-styled {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: linear-gradient(135deg, #7c3aed, #6366f1);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s;
        margin-top: 12px;
    }
    
    .btn-copy-styled:hover {
        background: linear-gradient(135deg, #6d28d9, #4f46e5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
    }
    
    .btn-copy-styled:active {
        transform: translateY(0);
    }
    
    .result-icon {
        font-size: 1.5rem;
    }
    
    .result-content p {
        margin: 4px 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Challenge cards */
    .challenge-card {
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: 16px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .challenge-card:hover {
        border-color: var(--purple-400);
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }
    
    .challenge-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .challenge-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .challenge-points {
        font-weight: 800;
        color: var(--purple-600);
        font-size: 1.1rem;
    }
    
    .challenge-title {
        margin: 0 0 8px 0;
        font-size: 1.15rem;
    }
    
    .challenge-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0 0 16px 0;
        line-height: 1.5;
    }
    
    .challenge-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid var(--border-color);
    }
    
    .challenge-solves {
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .challenge-action {
        color: var(--purple-600);
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Challenge detail view */
    .challenge-detail {
        background: var(--card-bg);
        border: 2px solid var(--purple-300);
        border-radius: 16px;
        padding: 24px;
    }
    
    .btn-back {
        background: transparent;
        border: none;
        color: var(--purple-600);
        cursor: pointer;
        font-size: 0.95rem;
        padding: 0;
        margin-bottom: 20px;
        font-weight: 600;
    }
    
    .btn-back:hover {
        text-decoration: underline;
    }
    
    .challenge-detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .challenge-points-large {
        font-size: 2rem;
        font-weight: 900;
        color: var(--purple-600);
    }
    
    .hints-section {
        background: var(--bg-tertiary);
        border-radius: 12px;
        margin: 20px 0;
    }
    
    .hints-section summary {
        padding: 16px;
        cursor: pointer;
        font-weight: 600;
    }
    
    .hints-list {
        padding: 0 16px 16px 36px;
        margin: 0;
    }
    
    .hints-list li {
        margin-bottom: 8px;
        color: var(--text-secondary);
    }
    
    .solution-section {
        margin-top: 24px;
    }
    
    .solution-input-group {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .solution-input-group .input-field {
        flex: 1;
        min-width: 300px;
        padding: 14px 18px;
        font-size: 1rem;
        border-radius: 10px;
    }
    
    .solution-input-group .btn-primary {
        padding: 14px 28px;
        white-space: nowrap;
    }
    
    .challenge-result {
        margin-top: 16px;
    }
    
    /* Multi-file preview */
    .mf-preview-item {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 12px;
        background: var(--bg-tertiary);
        border-radius: 8px;
        position: relative;
    }
    
    .mf-preview-item img {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: 4px;
    }
    
    .mf-remove-btn {
        position: absolute;
        top: 4px;
        right: 4px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(239, 68, 68, 0.9);
        color: white;
        border: none;
        cursor: pointer;
        font-size: 14px;
        line-height: 1;
    }
    
    .mf-results-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 16px;
    }
    
    .mf-result-item {
        background: var(--bg-tertiary);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .mf-result-item img {
        width: 100%;
        height: 100px;
        object-fit: cover;
    }
    
    .mf-result-info {
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .btn-download {
        background: var(--purple-600);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: background 0.2s;
    }
    
    .btn-download:hover {
        background: var(--purple-700);
    }
    
    .decoded-message {
        background: var(--bg-tertiary);
        border-radius: 12px;
        padding: 16px;
        margin-top: 16px;
    }
    
    .decoded-message label {
        display: block;
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--text-secondary);
    }
    
    .message-content {
        background: var(--card-bg);
        padding: 16px;
        border-radius: 8px;
        font-family: monospace;
        word-break: break-all;
        margin-bottom: 12px;
    }
    
    .btn-copy {
        background: var(--purple-100);
        color: var(--purple-700);
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .btn-copy:hover {
        background: var(--purple-200);
    }
    
    /* Scanner result */
    .scanner-result-header {
        display: flex;
        align-items: center;
        gap: 24px;
        padding: 20px;
        background: var(--bg-tertiary);
        border-radius: 12px;
        margin-bottom: 16px;
    }
    
    .scanner-probability {
        position: relative;
        width: 100px;
        height: 100px;
    }
    
    .probability-ring {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }
    
    .probability-bg {
        fill: none;
        stroke: var(--border-color);
        stroke-width: 3;
    }
    
    .probability-fill {
        fill: none;
        stroke-width: 3;
        stroke-linecap: round;
        transition: stroke-dasharray 0.5s ease;
    }
    
    .probability-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    
    .probability-value {
        display: block;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--prob-color, var(--text-primary));
    }
    
    .probability-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
    }
    
    .scanner-verdict {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .verdict-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .verdict-text strong {
        display: block;
        font-size: 1.1rem;
    }
    
    .verdict-text span {
        color: var(--text-muted);
        font-size: 0.9rem;
        text-transform: capitalize;
    }
    
    .text-scan-stat {
        text-align: center;
        padding: 16px 24px;
        background: var(--card-bg);
        border-radius: 12px;
    }
    
    .stat-value {
        display: block;
        font-size: 2.5rem;
        font-weight: 900;
    }
    
    .stat-label {
        display: block;
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    .scanner-indicators {
        margin-top: 16px;
        padding: 16px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    
    .scanner-indicators h4 {
        margin: 0 0 12px 0;
        font-size: 0.95rem;
    }
    
    .scanner-indicators ul {
        margin: 0;
        padding-left: 20px;
    }
    
    .scanner-indicators li {
        margin-bottom: 6px;
        color: var(--text-secondary);
    }
    
    .scanner-warning {
        margin-top: 16px;
        padding: 16px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 8px;
        color: #dc2626;
    }
    
    .scanner-warning p {
        margin: 8px 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .scanner-details {
        margin-top: 16px;
    }
    
    .scanner-details summary {
        cursor: pointer;
        color: var(--purple-600);
        font-weight: 600;
    }
    
    .scanner-details pre {
        background: var(--bg-tertiary);
        padding: 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        overflow-x: auto;
        margin-top: 8px;
    }
    
    .scanner-preview-content {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    
    .scanner-preview-content img {
        max-width: 120px;
        max-height: 80px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .scanner-preview-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .scanner-preview-info span {
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    /* Mode toggle buttons */
    .mode-toggle {
        display: flex;
        gap: 0;
        margin-bottom: 24px;
        background: var(--bg-tertiary);
        border-radius: 12px;
        padding: 4px;
    }
    
    .mode-btn {
        flex: 1;
        padding: 12px 24px;
        border: none;
        background: transparent;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .mode-btn:hover {
        color: var(--text-primary);
    }
    
    .mode-btn.active {
        background: var(--purple-600);
        color: white;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);
    }
    
    .mode-icon {
        font-size: 1.2rem;
    }
    
    /* Parts selector */
    .parts-selector {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .part-btn {
        width: 48px;
        height: 48px;
        border: 2px solid var(--border-color);
        background: var(--card-bg);
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .part-btn:hover {
        border-color: var(--purple-400);
    }
    
    .part-btn.active {
        background: var(--purple-600);
        color: white;
        border-color: var(--purple-600);
    }
    
    /* Scanner tabs */
    .scanner-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 24px;
        background: var(--bg-tertiary);
        border-radius: 12px;
        padding: 4px;
    }
    
    .scanner-tab {
        flex: 1;
        padding: 12px 20px;
        border: none;
        background: transparent;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .scanner-tab:hover {
        color: var(--text-primary);
    }
    
    .scanner-tab.active {
        background: var(--purple-600);
        color: white;
    }
    
    .scanner-section {
        display: none;
    }
    
    .scanner-section.active {
        display: block;
    }
    
    /* Upload zone */
    .upload-zone {
        border: 2px dashed var(--border-color);
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 16px;
    }
    
    .upload-zone:hover {
        border-color: var(--purple-400);
        background: rgba(124, 58, 237, 0.05);
    }
    
    .upload-zone.dragover {
        border-color: var(--purple-600);
        background: rgba(124, 58, 237, 0.1);
    }
    
    .upload-zone.has-file {
        border-style: solid;
        border-color: var(--purple-400);
        padding: 16px;
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }
    
    .upload-text {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    
    .upload-hint {
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    /* Challenge filters */
    .challenge-filters {
        display: flex;
        gap: 8px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    
    .btn-filter {
        padding: 8px 20px;
        border: 2px solid var(--border-color);
        background: var(--card-bg);
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
        border-radius: 24px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-filter:hover {
        border-color: var(--purple-400);
        color: var(--text-primary);
    }
    
    .btn-filter.active {
        background: var(--purple-600);
        color: white;
        border-color: var(--purple-600);
    }
    
    /* Challenges grid */
    .challenges-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
    }
    
    /* Multi-file preview grid */
    .mf-preview-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 16px;
    }
`;
document.head.appendChild(featureStyles);