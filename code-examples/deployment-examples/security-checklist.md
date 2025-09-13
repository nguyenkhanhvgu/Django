# Django Production Security Checklist

## Pre-Deployment Security Checklist

Use this checklist to ensure your Django application is secure before deploying to production.

### Django Settings Security

- [ ] **DEBUG = False** - Never run with debug mode in production
- [ ] **SECRET_KEY** - Use a strong, unique secret key stored in environment variables
- [ ] **ALLOWED_HOSTS** - Specify exact domain names, never use `['*']`
- [ ] **SECURE_SSL_REDIRECT = True** - Force HTTPS redirects
- [ ] **SESSION_COOKIE_SECURE = True** - Secure session cookies
- [ ] **CSRF_COOKIE_SECURE = True** - Secure CSRF cookies
- [ ] **SECURE_BROWSER_XSS_FILTER = True** - Enable XSS filtering
- [ ] **SECURE_CONTENT_TYPE_NOSNIFF = True** - Prevent MIME type sniffing
- [ ] **X_FRAME_OPTIONS = 'DENY'** - Prevent clickjacking attacks

### HTTPS and Security Headers

- [ ] **SECURE_HSTS_SECONDS** - Set to at least 31536000 (1 year)
- [ ] **SECURE_HSTS_INCLUDE_SUBDOMAINS = True** - Include subdomains in HSTS
- [ ] **SECURE_HSTS_PRELOAD = True** - Enable HSTS preloading
- [ ] **Content Security Policy** - Implement CSP headers
- [ ] **SSL Certificate** - Valid SSL/TLS certificate installed
- [ ] **HTTP to HTTPS Redirect** - All HTTP traffic redirected to HTTPS

### Database Security

- [ ] **Database SSL** - Use SSL connections to database
- [ ] **Strong Database Password** - Use complex, unique passwords
- [ ] **Database User Permissions** - Limit database user permissions
- [ ] **Database Backups** - Automated, encrypted backups configured
- [ ] **Connection Pooling** - Implement database connection pooling
- [ ] **Database Firewall** - Restrict database access to application servers only

### Authentication and Authorization

- [ ] **Strong Password Policy** - Implement password validators
- [ ] **Session Security** - Configure secure session settings
- [ ] **Admin Interface** - Secure admin interface access
- [ ] **User Permissions** - Implement proper user permissions
- [ ] **Two-Factor Authentication** - Consider implementing 2FA
- [ ] **Account Lockout** - Implement account lockout after failed attempts

### File Upload Security

- [ ] **File Type Validation** - Validate uploaded file types
- [ ] **File Size Limits** - Set appropriate file size limits
- [ ] **Virus Scanning** - Scan uploaded files for malware
- [ ] **Secure File Storage** - Store files outside web root
- [ ] **File Access Controls** - Implement proper file access controls

### API Security (if applicable)

- [ ] **Authentication** - Implement proper API authentication
- [ ] **Rate Limiting** - Implement rate limiting for API endpoints
- [ ] **CORS Configuration** - Configure CORS properly
- [ ] **Input Validation** - Validate all API inputs
- [ ] **API Versioning** - Implement API versioning strategy

### Infrastructure Security

- [ ] **Server Hardening** - Harden server configuration
- [ ] **Firewall Configuration** - Configure firewall rules
- [ ] **SSH Security** - Secure SSH access (key-based, disable root)
- [ ] **Regular Updates** - Keep OS and packages updated
- [ ] **Intrusion Detection** - Implement intrusion detection system
- [ ] **Log Monitoring** - Monitor logs for suspicious activity

### Application Security

- [ ] **Dependency Scanning** - Scan dependencies for vulnerabilities
- [ ] **Code Review** - Conduct security code reviews
- [ ] **Static Analysis** - Use static analysis security tools
- [ ] **Penetration Testing** - Conduct regular penetration tests
- [ ] **Security Headers Testing** - Test security headers implementation

### Monitoring and Logging

- [ ] **Error Logging** - Comprehensive error logging without sensitive data
- [ ] **Access Logging** - Log all access attempts
- [ ] **Security Event Logging** - Log security-related events
- [ ] **Log Retention** - Implement proper log retention policies
- [ ] **Real-time Monitoring** - Monitor for security incidents
- [ ] **Alerting** - Set up alerts for security events

### Data Protection

- [ ] **Data Encryption** - Encrypt sensitive data at rest
- [ ] **Data Transmission** - Encrypt data in transit
- [ ] **Data Backup** - Secure, encrypted backups
- [ ] **Data Retention** - Implement data retention policies
- [ ] **GDPR Compliance** - Ensure GDPR compliance if applicable
- [ ] **PII Protection** - Protect personally identifiable information

### Environment Security

- [ ] **Environment Variables** - Use environment variables for secrets
- [ ] **Secrets Management** - Use proper secrets management system
- [ ] **Environment Separation** - Separate dev/staging/production environments
- [ ] **Access Controls** - Implement proper access controls
- [ ] **Audit Trails** - Maintain audit trails for access and changes

## Security Testing Commands

### Django Security Check
```bash
# Run Django's built-in security check
python manage.py check --deploy

# Check for common security issues
python manage.py check --tag security
```

### Dependency Vulnerability Scanning
```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check

# Check specific requirements file
safety check -r requirements/production.txt
```

### SSL/TLS Testing
```bash
# Test SSL configuration
curl -I https://yourdomain.com

# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Security Headers Testing
```bash
# Test security headers
curl -I https://yourdomain.com

# Use online tools like:
# - securityheaders.com
# - observatory.mozilla.org
```

## Security Tools and Resources

### Recommended Security Tools

1. **Bandit** - Python security linter
   ```bash
   pip install bandit
   bandit -r your_project/
   ```

2. **Safety** - Dependency vulnerability scanner
   ```bash
   pip install safety
   safety check
   ```

3. **Semgrep** - Static analysis security scanner
   ```bash
   pip install semgrep
   semgrep --config=auto your_project/
   ```

4. **OWASP ZAP** - Web application security scanner
5. **Nmap** - Network security scanner
6. **Lynis** - System security auditing tool

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Incident Response Plan

### Security Incident Response Steps

1. **Identify** - Detect and identify security incidents
2. **Contain** - Contain the incident to prevent further damage
3. **Eradicate** - Remove the threat from the environment
4. **Recover** - Restore systems to normal operation
5. **Learn** - Document lessons learned and improve security

### Emergency Contacts

- [ ] **Security Team** - Internal security team contacts
- [ ] **Hosting Provider** - Cloud provider security contacts
- [ ] **Legal Team** - Legal team for compliance issues
- [ ] **External Security** - External security consultant contacts

## Regular Security Maintenance

### Weekly Tasks
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Monitor system resource usage
- [ ] Review user access permissions

### Monthly Tasks
- [ ] Update dependencies and packages
- [ ] Review and rotate API keys
- [ ] Conduct security scans
- [ ] Review backup integrity

### Quarterly Tasks
- [ ] Conduct penetration testing
- [ ] Review and update security policies
- [ ] Security training for development team
- [ ] Disaster recovery testing

### Annual Tasks
- [ ] Comprehensive security audit
- [ ] Update incident response plan
- [ ] Review and update security architecture
- [ ] Compliance assessment and certification

## Compliance Considerations

### GDPR (General Data Protection Regulation)
- [ ] Data protection impact assessment
- [ ] Privacy by design implementation
- [ ] User consent management
- [ ] Right to be forgotten implementation
- [ ] Data breach notification procedures

### HIPAA (Health Insurance Portability and Accountability Act)
- [ ] Administrative safeguards
- [ ] Physical safeguards
- [ ] Technical safeguards
- [ ] Business associate agreements

### SOC 2 (Service Organization Control 2)
- [ ] Security controls
- [ ] Availability controls
- [ ] Processing integrity controls
- [ ] Confidentiality controls
- [ ] Privacy controls

Remember: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures to address new threats and vulnerabilities.