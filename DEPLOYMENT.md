# Production Deployment Guide

## Prerequisites

- GitHub repository with Issues enabled
- GitHub Actions enabled
- GitHub Pages enabled
- Python 3.11+ for development

## Environment Setup

### 1. Repository Configuration

1. Fork or clone this repository
2. Enable GitHub Issues in repository settings
3. Enable GitHub Actions in repository settings
4. Enable GitHub Pages (source: GitHub Actions)

### 2. Environment Variables

Set up the following secrets in your GitHub repository:

- `GH_TOKEN`: GitHub Personal Access Token with `repo` scope

### 3. Configuration Files

Update the following files with your repository information:

**index.html:**
```javascript
const GITHUB_REPO = 'your-username/your-repo-name';
```

**update_chat.py:**
```python
ADMIN_USERS = ["your-github-username"]  # Add your admin users
```

## Production Features

### Security
- ✅ Input sanitization and XSS protection
- ✅ Rate limiting awareness
- ✅ Environment variable security
- ✅ Content Security Policy ready
- ✅ HTTPS enforcement

### Performance
- ✅ Caching with Service Worker
- ✅ Offline functionality
- ✅ Background sync
- ✅ Performance monitoring
- ✅ Error tracking
- ✅ Page visibility optimization

### User Experience
- ✅ Progressive Web App (PWA) support
- ✅ Mobile responsive design
- ✅ Loading states and error handling
- ✅ Auto-refresh with smart pausing
- ✅ Network status awareness

### Monitoring & Logging
- ✅ Structured logging
- ✅ Error reporting
- ✅ Performance metrics
- ✅ Backup creation
- ✅ Retry mechanisms

## Deployment Steps

### 1. Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Update configuration
# Edit index.html and update_chat.py with your repository details
```

### 2. GitHub Configuration
1. Go to repository Settings > Secrets and Variables > Actions
2. Add `GH_TOKEN` secret with your GitHub Personal Access Token
3. Go to Settings > Pages
4. Set source to "GitHub Actions"

### 3. Test Deployment
1. Create a test issue using the chat message template
2. Verify GitHub Actions workflow runs successfully
3. Check that GitHub Pages site is accessible
4. Test all functionality including admin commands

### 4. Domain Setup (Optional)
1. Add custom domain in GitHub Pages settings
2. Update meta tags in index.html with your domain
3. Configure DNS records for your domain

## Monitoring

### Health Checks
- Monitor GitHub Actions workflow status
- Check error logs in workflow runs
- Monitor GitHub API rate limits
- Verify backup file creation

### Performance Metrics
- Page load times
- API response times
- Service Worker cache hit rates
- Error rates and types

## Maintenance

### Regular Tasks
- Review and rotate GitHub tokens
- Monitor repository size and clean up if needed
- Update dependencies in requirements.txt
- Review admin user list

### Scaling Considerations
- GitHub API rate limits (5,000 requests/hour)
- GitHub Issues limit (no hard limit, but performance considerations)
- GitHub Pages bandwidth limits
- Service Worker cache size limits

## Troubleshooting

### Common Issues

**GitHub Actions failing:**
- Check if GH_TOKEN is properly set
- Verify token has correct permissions
- Check rate limit status

**Messages not appearing:**
- Verify GitHub Actions workflow completed
- Check if admin commands are filtering messages
- Verify GitHub Pages deployment

**Performance issues:**
- Monitor GitHub API rate limits
- Check Service Worker cache
- Verify auto-refresh intervals

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Security Considerations

1. **Token Security**: Keep GitHub tokens secure and rotate regularly
2. **Admin Access**: Limit admin users to trusted individuals
3. **Content Moderation**: Monitor for inappropriate content
4. **Rate Limiting**: Respect GitHub API limits to avoid being blocked

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Open an issue in the repository
4. Consult GitHub's documentation for API and Pages limits