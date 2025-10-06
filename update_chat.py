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
    body = issue.body.strip().replace("\r", "")
    
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
chat_content = "# Chat\n\n"
chat_content += f"[![New Message](https://img.shields.io/badge/💬-New_Message-blue?style=for-the-badge)](https://github.com/{repo_name}/issues/new)\n\n"

if messages:
    chat_content += "---\n\n"  # Add a separator line
    for message in messages:
        chat_content += f"**{message}**\n\n"  # Make each message bold and add extra spacing
else:
    chat_content += "*Waiting for messages...*\n"

# Update README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(chat_content)
