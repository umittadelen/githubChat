# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in GitHub Chat, please report it to us in a responsible manner.

### How to Report

1. **DO NOT** open a public issue for security vulnerabilities
2. Send an email to the repository owner with:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if available)

### Security Measures

This application implements several security measures:

1. **Input Sanitization**: HTML content is sanitized to prevent XSS attacks
2. **Event Handler Filtering**: Auto-executing events (onload, onerror, etc.) are blocked
3. **User Interaction Only**: Only user-triggered events (onclick) are permitted
4. **JavaScript URL Blocking**: javascript: URLs are filtered out
5. **Rate Limiting**: GitHub API rate limits are respected
6. **Environment Variables**: Sensitive data is stored in environment variables
7. **Content Security Policy**: CSP headers help prevent injection attacks
8. **HTTPS Only**: All communications are encrypted

### Allowed vs Blocked Events

**✅ Allowed (User-triggered):**
- `onclick` - User must click to trigger

**❌ Blocked (Auto-executing):**
- `onload`, `onerror` - Execute automatically when page/element loads
- `onmouseover`, `onmouseout` - Execute on mouse hover
- `onfocus`, `onblur` - Execute on element focus changes
- `onchange`, `onsubmit` - Execute on form interactions
- `onkeydown`, `onkeyup` - Execute on keyboard input
- And many other automatic event handlers

### Security Best Practices for Users

1. **Be cautious with HTML content**: This chat allows HTML, so be careful with untrusted content
2. **Don't share sensitive information**: This is a public chat system
3. **Report suspicious activity**: Contact administrators if you notice unusual behavior

### Known Security Considerations

1. **HTML content is allowed with restrictions** - Auto-executing events are blocked, only user-triggered events (onclick) permitted
2. **GitHub Issues are public** - All messages are visible to anyone
3. **Admin commands are restricted** - Only authorized users can execute admin commands
4. **Clickjacking protection** - Users should verify the authenticity of interactive elements before clicking

## Updates

Security updates will be published as new releases. Please keep your deployment up to date.