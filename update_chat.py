from github import Github
import os

MAX_LENGTH = 100  # max characters per message

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
        
        # Calculate available space for message (accounting for clickable username and formatting)
        # Account for markdown link format: [username](url)
        username_link = f"[**@{username}**]({user_url})"
        username_prefix_length = len(f"@{username}: ")  # Calculate length as if it were plain text
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
        
        # Create clickable username link and render markdown in message body
        username_link = f"[**@{username}**]({user_url})"
        chat_content += f"> {username_link}: {body}\n\n"
else:
    chat_content += "---\n\n"
    chat_content += "💭 *No messages yet. Be the first to start the conversation!*\n\n"
    chat_content += "👆 *Click the button above to send a message*\n\n"
    chat_content += "✨ *Tip: You can use **markdown** formatting in your messages!*\n"

# Update README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(chat_content)
