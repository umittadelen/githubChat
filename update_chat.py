from github import Github
import os

MAX_LENGTH = 100  # max characters per message

# Connect to GitHub
g = Github(os.environ["GH_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

# Get all open issues
issues = repo.get_issues(state="open")
messages = []

# Sort issues by number (newest first)
for issue in sorted(issues, key=lambda i: i.number, reverse=True):
    username = issue.user.login
    body = issue.body
    
    # Handle admin commands (only for umittadelen)
    if username == "umittadelen" and body and body.strip().lower() == "/clean":
        print("🧹 Admin command detected: Cleaning chat...")
        # Close all open issues to clean the chat
        for clean_issue in repo.get_issues(state="open"):
            clean_issue.edit(state="closed")
            print(f"Closed issue #{clean_issue.number}")
        print("✅ Chat cleaned successfully!")
        # Clear messages list since we closed all issues
        messages = []
        break
    
    # Handle empty or None body
    if not body or not body.strip():
        body = "*[no message]*"
    else:
        body = body.strip().replace("\r", "")
    
    # Calculate available space for message (accounting for username and formatting)
    username_prefix = f"{username}: "
    available_length = MAX_LENGTH - len(username_prefix)
    
    # Cut message to available length and add "…" if trimmed
    if len(body) > available_length:
        body = body[:available_length-1] + "…"
    
    # Format as "username: message"
    formatted_message = f"{username}: {body}"
    messages.append(formatted_message)

# Get repository info for the button link
repo_name = os.environ["GITHUB_REPOSITORY"]

# Generate README content with new message button
chat_content = "# 💬 Chat\n\n"
chat_content += f"[![New Message](https://img.shields.io/badge/💬-New_Message-blue?style=for-the-badge)](https://github.com/{repo_name}/issues/new?template=chat-message.md) "
chat_content += f"[![Online Users](https://img.shields.io/badge/👥-{len(set(msg.split(':')[0] for msg in messages)) if messages else 0}_users-green?style=for-the-badge)](https://github.com/{repo_name}/issues)\n\n"

if messages:
    chat_content += "---\n\n"
    chat_content += f"**💭 {len(messages)} message{'s' if len(messages) != 1 else ''}**\n\n"
    for i, message in enumerate(messages, 1):
        # Extract username and message parts
        parts = message.split(': ', 1)
        if len(parts) == 2:
            username, msg = parts
            chat_content += f"> **@{username}**: {msg}\n\n"
        else:
            chat_content += f"> {message}\n\n"
else:
    chat_content += "---\n\n"
    chat_content += "💭 *No messages yet. Be the first to start the conversation!*\n\n"
    chat_content += "👆 *Click the button above to send a message*\n"

# Update README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(chat_content)
