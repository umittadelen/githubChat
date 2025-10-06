from github import Github
import os

MAX_LENGTH = 100  # max characters per message

# Connect to GitHub
g = Github(os.environ["GH_TOKEN"])
repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

# Get all open issues
issues = repo.get_issues(state="open")
messages = []

# Sort issues by number (oldest first)
for issue in sorted(issues, key=lambda i: i.number):
    body = issue.body.strip().replace("\r", "")
    
    # Cut message to MAX_LENGTH and add "…" if trimmed
    if len(body) > MAX_LENGTH:
        body = body[:MAX_LENGTH-1] + "…"

    messages.append(body)

# Get repository info for the button link
repo_name = os.environ["GITHUB_REPOSITORY"]

# Generate README content with new message button
chat_content = "# Chat\n\n"
chat_content += f"[![New Message](https://img.shields.io/badge/💬-New_Message-blue?style=for-the-badge)](https://github.com/{repo_name}/issues/new)\n\n"

if messages:
    chat_content += "\n".join(messages) + "\n"
else:
    chat_content += "*Waiting for messages...*\n"

# Update README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(chat_content)
