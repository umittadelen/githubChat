#!/usr/bin/env python3
"""
GitHub Chat System - A real-time chat using GitHub Issues
Supports markdown, HTML, and admin commands for moderation.
"""

from github import Github
import os
import sys
import time
from datetime import datetime
import re

# Configuration
MAX_LENGTH = 500  # max characters per message (increased for HTML content)
ADMIN_USERS = ["umittadelen"]  # List of admin users
CLEAN_COMMANDS = ["/clean", "/reset", "/clear"]  # Only slash commands for security
MAX_MESSAGES = 50  # Limit number of messages to prevent performance issues

def log(message):
    """Enhanced logging with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def safe_get_env(var_name, default=None):
    """Safely get environment variables with error handling"""
    value = os.environ.get(var_name, default)
    if not value and default is None:
        log(f"❌ ERROR: Required environment variable '{var_name}' not found")
        sys.exit(1)
    return value

def sanitize_html(text):
    """Basic HTML sanitization to prevent XSS"""
    if not text:
        return text
    
    # Remove potentially dangerous tags and attributes
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'on\w+\s*=\s*["\'][^"\']*["\']',  # Remove onclick, onload, etc.
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

def is_admin_command(issue, admin_users, clean_commands):
    """Check if an issue contains an admin command"""
    try:
        if not issue or not issue.user:
            return False, None
            
        username = issue.user.login
        if username not in admin_users:
            return False, None
            
        body = issue.body.strip().lower() if issue.body else ""
        if body in clean_commands:
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

def generate_chat_content(messages, repo_name):
    """Generate the README chat content"""
    try:
        # Header
        chat_content = "# 💬 Chat\n\n"
        
        # Buttons
        unique_users = len(set(msg['username'] for msg in messages)) if messages else 0
        chat_content += f"[![New Message](https://img.shields.io/badge/💬-New_Message-blue?style=for-the-badge)](https://github.com/{repo_name}/issues/new?template=chat-message.md) "
        chat_content += f"[![Online Users](https://img.shields.io/badge/👥-{unique_users}_users-green?style=for-the-badge)](https://github.com/{repo_name}/issues) "
        chat_content += f"[![Messages](https://img.shields.io/badge/📝-{len(messages)}_messages-orange?style=for-the-badge)](#)\n\n"
        
        if messages:
            chat_content += "---\n\n"
            
            # Add timestamp info
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            chat_content += f"*Last updated: {timestamp}*\n\n"
            
            for i, message_data in enumerate(messages, 1):
                username = message_data['username']
                user_url = message_data['user_url']
                body = message_data['body']
                
                # Enhanced styling
                message_style = (
                    "margin: 15px 0; padding: 15px; "
                    "border-left: 4px solid #0366d6; "
                    "background: linear-gradient(135deg, #f6f8fa 0%, #e1e4e8 100%); "
                    "border-radius: 8px; "
                    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; "
                    "box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                )
                username_style = "font-weight: bold; color: #0366d6; text-decoration: none; font-size: 14px;"
                body_style = "margin-top: 8px; line-height: 1.6; color: #24292e;"
                
                chat_content += f"""<div style="{message_style}">
<div>
<a href="{user_url}" style="{username_style}">@{username}</a>
</div>
<div style="{body_style}">{body}</div>
</div>

"""
                
                # Add separator between messages (except after the last message)
                if i < len(messages):
                    chat_content += "---\n\n"
        else:
            chat_content += "---\n\n"
            chat_content += "*Chat is empty. Start the conversation!*\n\n"
        
        return chat_content
        
    except Exception as e:
        log(f"❌ Error generating chat content: {e}")
        return "# 💬 Chat\n\n*Error generating chat content*\n"

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
        for issue in issues:
            is_admin, command = is_admin_command(issue, ADMIN_USERS, CLEAN_COMMANDS)
            if is_admin:
                log(f"🧹 Admin command '{command}' detected from @{issue.user.login} in issue #{issue.number}")
                if execute_clean_command(repo, ADMIN_USERS):
                    clean_requested = True
                    issues = []  # Clear issues list since they're all closed
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
                    
                    message_data = {
                        'username': username,
                        'user_url': user_url,
                        'body': body
                    }
                    messages.append(message_data)
                    
                except Exception as e:
                    log(f"❌ Error processing issue #{issue.number}: {e}")
                    continue
            
            log(f"✅ Processed {len(messages)} messages")
        
        # Generate README content
        log("📝 Generating README content...")
        chat_content = generate_chat_content(messages, repo_name)
        
        # Update README.md
        log("💾 Updating README.md...")
        try:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(chat_content)
            log("✅ README.md updated successfully")
        except Exception as e:
            log(f"❌ Error writing README.md: {e}")
            return False
        
        log("🎉 GitHub Chat update completed successfully!")
        return True
        
    except Exception as e:
        log(f"💥 Critical error in main function: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
