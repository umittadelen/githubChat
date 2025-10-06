from github import Github
import os

MAX_LENGTH = 500  # max characters per message (increased for HTML content)

# Connect to GitHub
g = Github(os.environ["GH_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

# Get all open issues
issues = repo.get_issues(state="open")
messages = []

# Check for admin clean command first
clean_requested = False
for issue in issues:
    if issue.user.login == "umittadelen" and issue.body and issue.body.strip().lower() == "/clean":
        print("🧹 Admin command detected: Cleaning chat...")
        clean_requested = True
        break

# If clean was requested, close all issues
if clean_requested:
    for clean_issue in repo.get_issues(state="open"):
        clean_issue.edit(state="closed")
        print(f"Closed issue #{clean_issue.number}")
    print("✅ Chat cleaned successfully!")
    messages = []  # No messages to display
else:
    # Sort issues by number (newest first) and process messages
    for issue in sorted(issues, key=lambda i: i.number, reverse=True):
        username = issue.user.login
        user_url = f"https://github.com/{username}"
        body = issue.body
        
        # Handle empty or None body
        if not body or not body.strip():
            body = "*[no message]*"
        else:
            body = body.strip().replace("\r", "")
        
        # For HTML content, be more generous with length limits
        # Check if message contains HTML tags
        contains_html = '<' in body and '>' in body
        
        # Calculate available space for message (accounting for clickable username and formatting)
        username_prefix_length = len(f"@{username}: ")  # Calculate length as if it were plain text
        
        if contains_html:
            # For HTML content, use a more generous limit
            available_length = MAX_LENGTH * 2 - username_prefix_length
        else:
            # For regular text, use normal limit
            available_length = MAX_LENGTH - username_prefix_length
        
        # Cut message to available length and add "…" if trimmed
        if len(body) > available_length:
            body = body[:available_length-1] + "…"
        
        # Store username, user_url, and message separately for better formatting
        message_data = {
            'username': username,
            'user_url': user_url,
            'body': body
        }
        messages.append(message_data)

# Get repository info for the button link
repo_name = os.environ["GITHUB_REPOSITORY"]

# Generate README content with new message button
chat_content = "# 💬 Chat\n\n"
chat_content += f"[![New Message](https://img.shields.io/badge/💬-New_Message-blue?style=for-the-badge)](https://github.com/{repo_name}/issues/new?template=chat-message.md) "
chat_content += f"[![Online Users](https://img.shields.io/badge/👥-{len(set(msg['username'] for msg in messages)) if messages else 0}_users-green?style=for-the-badge)](https://github.com/{repo_name}/issues)\n\n"

if messages:
    chat_content += "---\n\n"
    chat_content += f"**💭 {len(messages)} message{'s' if len(messages) != 1 else ''}**\n\n"
    
    for i, message_data in enumerate(messages, 1):
        username = message_data['username']
        user_url = message_data['user_url']
        body = message_data['body']
        
        # Create HTML-styled message container with inline styles (GitHub compatible)
        message_style = "margin: 10px 0; padding: 12px; border-left: 4px solid #0366d6; background: #f6f8fa; border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;"
        username_style = "font-weight: bold; color: #0366d6; text-decoration: none;"
        body_style = "margin-top: 8px; line-height: 1.5;"
        
        chat_content += f"""<div style="{message_style}">
<a href="{user_url}" style="{username_style}">@{username}</a>
<div style="{body_style}">{body}</div>
</div>

"""
        
        # Add separator between messages (except after the last message)
        if i < len(messages):
            chat_content += "---\n\n"
else:
    chat_content += "---\n\n"

# Update README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(chat_content)
