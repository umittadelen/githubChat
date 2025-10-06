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
2. **Rate Limiting**: GitHub API rate limits are respected
3. **Environment Variables**: Sensitive data is stored in environment variables
4. **Content Security Policy**: CSP headers help prevent injection attacks
5. **HTTPS Only**: All communications are encrypted

### Security Best Practices for Users

1. **Be cautious with HTML content**: This chat allows HTML, so be careful with untrusted content
2. **Don't share sensitive information**: This is a public chat system
3. **Report suspicious activity**: Contact administrators if you notice unusual behavior

### Known Security Considerations

1. HTML content is allowed and minimally filtered - users should exercise caution
2. GitHub Issues are public - all messages are visible to anyone
3. Admin commands are restricted to authorized users only

## Updates

Security updates will be published as new releases. Please keep your deployment up to date.