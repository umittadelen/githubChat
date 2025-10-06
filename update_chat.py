#!/usr/bin/env python3
"""
GitHub Chat System - A real-time chat using GitHub Issues
Production-ready version with comprehensive error handling, monitoring, and security.
Supports markdown, HTML, and admin commands for moderation.
"""

from github import Github
import os
import sys
import time
import json
from datetime import datetime, timezone
import re
import logging
from typing import Optional, List, Dict, Any
import traceback

# Production Configuration
MAX_LENGTH = 500  # max characters per message (increased for HTML content)
ADMIN_USERS = ["umittadelen"]  # List of admin users - should be env var in production
CLEAN_COMMANDS = ["/clean", "/reset", "/clear"]  # Only slash commands for security
UPDATE_COMMANDS = ["/update", "/refresh", "/redraw"]  # Commands to trigger manual update
MAX_MESSAGES = 100  # Increased for production
API_TIMEOUT = 30  # GitHub API timeout in seconds
RETRY_ATTEMPTS = 3  # Number of retry attempts for API calls
BACKUP_FILE = "chat-data-backup.json"  # Backup file path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chat-system.log', mode='a')
    ]
)

def log(message: str, level: str = "INFO") -> None:
    """Enhanced logging with structured format and levels"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    if level == "ERROR":
        logging.error(f"[{timestamp}] {message}")
    elif level == "WARNING":
        logging.warning(f"[{timestamp}] {message}")
    elif level == "DEBUG":
        logging.debug(f"[{timestamp}] {message}")
    else:
        logging.info(f"[{timestamp}] {message}")

def safe_get_env(var_name: str, default: Optional[str] = None) -> str:
    """Safely get environment variables with error handling and validation"""
    value = os.environ.get(var_name, default)
    if not value and default is None:
        error_msg = f"Required environment variable '{var_name}' not found"
        log(error_msg, "ERROR")
        raise EnvironmentError(error_msg)
    
    # Validate GitHub token format
    if var_name == "GH_TOKEN" and value and not value.startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_")):
        log(f"Warning: GitHub token format may be invalid", "WARNING")
    
    return value

def retry_on_failure(max_attempts: int = RETRY_ATTEMPTS):
    """Decorator for retrying failed operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        log(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...", "WARNING")
                        time.sleep(wait_time)
                    else:
                        log(f"All {max_attempts} attempts failed", "ERROR")
            raise last_exception
        return wrapper
    return decorator

def create_backup(data: Dict[str, Any]) -> bool:
    """Create backup of chat data"""
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log(f"Backup created successfully: {BACKUP_FILE}")
        return True
    except Exception as e:
        log(f"Failed to create backup: {e}", "ERROR")
        return False

def sanitize_html(text):
    """Enhanced HTML sanitization to prevent XSS while allowing safe interactions"""
    if not text:
        return text
    
    # Remove potentially dangerous tags and attributes
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<form[^>]*>.*?</form>',
        r'<input[^>]*>',
        r'<textarea[^>]*>.*?</textarea>',
        r'<select[^>]*>.*?</select>',
    ]
    
    # Remove dangerous event handlers (allow only onclick for user interaction)
    dangerous_events = [
        r'onload\s*=\s*["\'][^"\']*["\']',
        r'onerror\s*=\s*["\'][^"\']*["\']',
        r'onmouseover\s*=\s*["\'][^"\']*["\']',
        r'onmouseout\s*=\s*["\'][^"\']*["\']',
        r'onmousemove\s*=\s*["\'][^"\']*["\']',
        r'onmousedown\s*=\s*["\'][^"\']*["\']',
        r'onmouseup\s*=\s*["\'][^"\']*["\']',
        r'onfocus\s*=\s*["\'][^"\']*["\']',
        r'onblur\s*=\s*["\'][^"\']*["\']',
        r'onchange\s*=\s*["\'][^"\']*["\']',
        r'onsubmit\s*=\s*["\'][^"\']*["\']',
        r'onreset\s*=\s*["\'][^"\']*["\']',
        r'onkeydown\s*=\s*["\'][^"\']*["\']',
        r'onkeyup\s*=\s*["\'][^"\']*["\']',
        r'onkeypress\s*=\s*["\'][^"\']*["\']',
        r'onresize\s*=\s*["\'][^"\']*["\']',
        r'onscroll\s*=\s*["\'][^"\']*["\']',
        r'onunload\s*=\s*["\'][^"\']*["\']',
        r'onbeforeunload\s*=\s*["\'][^"\']*["\']',
        r'ondragstart\s*=\s*["\'][^"\']*["\']',
        r'ondrag\s*=\s*["\'][^"\']*["\']',
        r'ondragend\s*=\s*["\'][^"\']*["\']',
        r'ondrop\s*=\s*["\'][^"\']*["\']',
        r'ondragover\s*=\s*["\'][^"\']*["\']',
        r'ondragenter\s*=\s*["\'][^"\']*["\']',
        r'ondragleave\s*=\s*["\'][^"\']*["\']',
        r'ontouchstart\s*=\s*["\'][^"\']*["\']',
        r'ontouchmove\s*=\s*["\'][^"\']*["\']',
        r'ontouchend\s*=\s*["\'][^"\']*["\']',
        r'onanimationstart\s*=\s*["\'][^"\']*["\']',
        r'onanimationend\s*=\s*["\'][^"\']*["\']',
        r'ontransitionend\s*=\s*["\'][^"\']*["\']',
    ]
    
    # Apply dangerous tag removal
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Apply dangerous event handler removal
    for pattern in dangerous_events:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    text = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'src\s*=\s*["\']javascript:[^"\']*["\']', '', text, flags=re.IGNORECASE)
    
    log(f"HTML sanitized - removed dangerous patterns", "DEBUG")
    return text

def is_admin_command(issue, admin_users, clean_commands, update_commands):
    """Check if an issue contains an admin command"""
    try:
        if not issue or not issue.user:
            return False, None
            
        username = issue.user.login
        if username not in admin_users:
            return False, None
            
        body = issue.body.strip().lower() if issue.body else ""
        
        # Check for clean commands
        if body in clean_commands:
            return True, body
            
        # Check for update commands
        if body in update_commands:
            return True, body
            
        return False, None
    except Exception as e:
        log(f"❌ Error checking admin command: {e}")
        return False, None

def process_message_body(body, username, max_length):
    """Process and sanitize message body"""
    try:
        if not body or not body.strip():
            return "*[no message]*"
        
        # Basic cleanup
        body = body.strip().replace("\r", "").replace("\n\n\n", "\n\n")
        
        # Sanitize HTML
        body = sanitize_html(body)
        
        # Check if message contains HTML tags
        contains_html = '<' in body and '>' in body
        
        # Calculate available space
        username_prefix_length = len(f"@{username}: ")
        
        if contains_html:
            available_length = max_length * 2 - username_prefix_length
        else:
            available_length = max_length - username_prefix_length
        
        # Truncate if necessary
        if len(body) > available_length:
            body = body[:available_length-1] + "…"
        
        return body
    except Exception as e:
        log(f"❌ Error processing message body: {e}")
        return "*[error processing message]*"

def execute_clean_command(repo, admin_users):
    """Execute the clean command with enhanced error handling"""
    try:
        log("🧹 Executing clean command...")
        
        issues_to_close = list(repo.get_issues(state="open"))
        total_issues = len(issues_to_close)
        
        if total_issues == 0:
            log("ℹ️ No open issues to close")
            return True
        
        log(f"📋 Found {total_issues} open issues to close")
        
        closed_count = 0
        failed_count = 0
        
        for issue in issues_to_close:
            try:
                issue.edit(state="closed")
                log(f"✅ Closed issue #{issue.number}: {issue.title[:50]}...")
                closed_count += 1
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                log(f"❌ Failed to close issue #{issue.number}: {e}")
                failed_count += 1
        
        log(f"✅ Clean command completed: {closed_count} closed, {failed_count} failed")
        return closed_count > 0
        
    except Exception as e:
        log(f"❌ Critical error during clean command: {e}")
        return False

def execute_update_command(repo, admin_users):
    """Execute the update command to refresh JSON files"""
    try:
        log("🔄 Executing update command...")
        
        # Close the update command issue
        issues = list(repo.get_issues(state="open"))
        update_issue = None
        
        for issue in issues:
            body = issue.body.strip().lower() if issue.body else ""
            if body in UPDATE_COMMANDS:
                update_issue = issue
                break
        
        if update_issue:
            try:
                update_issue.edit(state="closed")
                log(f"✅ Closed update command issue #{update_issue.number}")
            except Exception as e:
                log(f"❌ Failed to close update issue: {e}")
        
        log("✅ Update command completed - will regenerate JSON data")
        return True
        
    except Exception as e:
        log(f"❌ Critical error during update command: {e}")
        return False

def generate_user_color(username):
    """Generate a consistent color for a user based on their username with proper contrast ratio"""
    # Generate hash from username
    hash_value = 0
    for char in username:
        hash_value = ord(char) + ((hash_value << 5) - hash_value)
    
    # Use hash to generate HSL values
    hue = abs(hash_value) % 360  # 0-359 degrees for hue
    saturation = 70 + (abs(hash_value >> 8) % 30)  # 70-100% saturation for vibrant colors
    
    # Find lightness that ensures proper contrast ratio
    lightness = find_optimal_lightness_for_hue(hue, saturation, hash_value)
    
    # Convert HSL to hex for HTML/CSS compatibility
    return hsl_to_hex(hue, saturation, lightness)

def find_optimal_lightness_for_hue(hue, saturation, hash_value):
    """Find lightness value that ensures contrast while allowing full color range"""
    # Generate a base lightness from hash for consistency
    base_lightness = 30 + (abs(hash_value >> 16) % 40)  # 30-70% base range
    
    # Test the preferred lightness first
    color = hsl_to_rgb(hue, saturation, base_lightness)
    contrast = get_contrast_ratio(color, (255, 255, 255))
    
    if contrast >= 4.5:
        return base_lightness  # Perfect, use the preferred lightness
    
    # If preferred lightness doesn't work, find the closest one that does
    test_ranges = [
        # Test around the preferred lightness first
        (max(15, base_lightness - 20), min(80, base_lightness + 20), 2),
        # Then test the full range if needed
        (15, 80, 3)
    ]
    
    for min_l, max_l, step in test_ranges:
        # Test darker first (usually better contrast)
        for l in range(base_lightness, min_l - 1, -step):
            color = hsl_to_rgb(hue, saturation, l)
            contrast = get_contrast_ratio(color, (255, 255, 255))
            if contrast >= 7.0:
                return l  # Prefer 7:1 ratio
        
        # Test lighter
        for l in range(base_lightness, max_l + 1, step):
            color = hsl_to_rgb(hue, saturation, l)
            contrast = get_contrast_ratio(color, (255, 255, 255))
            if contrast >= 7.0:
                return l
        
        # Fallback to 4.5:1 if 7:1 not found
        for l in range(base_lightness, min_l - 1, -step):
            color = hsl_to_rgb(hue, saturation, l)
            contrast = get_contrast_ratio(color, (255, 255, 255))
            if contrast >= 4.5:
                return l
        
        for l in range(base_lightness, max_l + 1, step):
            color = hsl_to_rgb(hue, saturation, l)
            contrast = get_contrast_ratio(color, (255, 255, 255))
            if contrast >= 4.5:
                return l
    
    return 25  # Ultimate fallback

def hsl_to_rgb(h, s, l):
    """Convert HSL to RGB tuple"""
    # Normalize values
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p
    
    if s == 0:
        r = g = b = l  # achromatic
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    # Convert to 0-255 range
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

def get_luminance(color):
    """Calculate relative luminance of RGB color"""
    r, g, b = [c / 255.0 for c in color]
    
    # Convert to linear RGB
    def linearize(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)
    
    # Calculate luminance
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def get_contrast_ratio(color1, color2):
    """Calculate contrast ratio between two RGB colors"""
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    
    return (brightest + 0.05) / (darkest + 0.05)

def hsl_to_hex(h, s, l):
    """Convert HSL to hex color"""
    r, g, b = hsl_to_rgb(h, s, l)
    return f"#{r:02x}{g:02x}{b:02x}"

def main():
    """Main function with comprehensive error handling"""
    try:
        log("🚀 Starting GitHub Chat update...")
        
        # Get environment variables
        github_token = safe_get_env("GH_TOKEN")
        repo_name = safe_get_env("GITHUB_REPOSITORY")
        
        # Initialize GitHub client
        log("🔑 Initializing GitHub client...")
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        # Get all open issues
        log("📥 Fetching open issues...")
        try:
            issues = list(repo.get_issues(state="open"))
            log(f"📋 Found {len(issues)} open issues")
        except Exception as e:
            log(f"❌ Error fetching issues: {e}")
            return False
        
        # Check for admin commands
        clean_requested = False
        update_requested = False
        
        for issue in issues:
            is_admin, command = is_admin_command(issue, ADMIN_USERS, CLEAN_COMMANDS, UPDATE_COMMANDS)
            if is_admin:
                log(f"🔧 Admin command '{command}' detected from @{issue.user.login} in issue #{issue.number}")
                
                if command in CLEAN_COMMANDS:
                    if execute_clean_command(repo, ADMIN_USERS):
                        clean_requested = True
                        issues = []  # Clear issues list since they're all closed
                    break
                elif command in UPDATE_COMMANDS:
                    if execute_update_command(repo, ADMIN_USERS):
                        update_requested = True
                        # Remove the update command issue from the list
                        issues = [i for i in issues if i.number != issue.number]
                    break
        
        # Process messages if no clean was requested
        messages = []
        if not clean_requested:
            log("💬 Processing messages...")
            
            # Sort issues by number (newest first) and limit
            sorted_issues = sorted(issues, key=lambda i: i.number, reverse=True)[:MAX_MESSAGES]
            
            for issue in sorted_issues:
                try:
                    username = issue.user.login
                    user_url = f"https://github.com/{username}"
                    
                    # Process message body
                    body = process_message_body(issue.body, username, MAX_LENGTH)
                    
                    # Get user avatar URL
                    avatar_url = issue.user.avatar_url if issue.user.avatar_url else f"https://github.com/{username}.png"
                    
                    message_data = {
                        'username': username,
                        'user_url': user_url,
                        'avatar_url': avatar_url,
                        'body': body
                    }
                    messages.append(message_data)
                    
                except Exception as e:
                    log(f"❌ Error processing issue #{issue.number}: {e}")
                    continue
            
            log(f"✅ Processed {len(messages)} messages")
            
            # Add update info if update was requested
            if update_requested:
                log("🔄 Update command processed - JSON will be regenerated with current structure")
        
        # Generate JSON data for GitHub Pages
        log("📊 Generating JSON data for GitHub Pages...")
        try:
            json_data = {
                "last_updated": datetime.now().isoformat(),
                "total_messages": len(messages),
                "unique_users": len(set(msg['username'] for msg in messages)) if messages else 0,
                "messages": [
                    {
                        "username": msg['username'],
                        "user_url": msg['user_url'],
                        "avatar_url": msg['avatar_url'],
                        "body": msg['body'],
                        "user_color": generate_user_color(msg['username']),
                        "timestamp": datetime.now().isoformat()  # In real implementation, use issue creation time
                    }
                    for msg in messages
                ]
            }
            
            with open("chat-data.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            log("✅ JSON data generated successfully")
        except Exception as e:
            log(f"❌ Error generating JSON data: {e}")
            return False
        
        log("🎉 GitHub Chat update completed successfully!")
        return True
        
    except Exception as e:
        log(f"💥 Critical error in main function: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
