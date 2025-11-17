# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Fladar, please report it responsibly. **Do not open a public GitHub issue.**

### How to Report

1. **Email**: Send details to `igor-olikh@users.noreply.github.com`
2. **Subject**: Include `[SECURITY]` in the subject line
3. **Details**: Please include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 7 days
- **Updates**: We will keep you informed of our progress
- **Resolution**: We will work to resolve the issue as quickly as possible

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We will not disclose the vulnerability publicly until a fix is available
- We will coordinate with you on the disclosure timeline

## Security Best Practices

### For Users

1. **Never commit `config.yaml`** - Always use `config.yaml.example` as a template
2. **Protect API credentials** - Keep your Amadeus API keys secure
3. **Use environment variables** - For CI/CD, use environment variables instead of config files
4. **Regular updates** - Keep Fladar and its dependencies up to date
5. **Review dependencies** - Be aware of what dependencies are installed

### For Contributors

1. **No hardcoded secrets** - Never commit API keys, passwords, or tokens
2. **Use placeholders** - Always use placeholders like `YOUR_API_KEY_HERE` in examples
3. **Review before commit** - Run the security checklist before committing
4. **Test safely** - Use test credentials in test environments only

## Known Security Considerations

### API Credentials

- Fladar requires Amadeus API credentials to function
- These credentials are stored locally in `config.yaml` (not tracked in git)
- Never share your API credentials publicly
- If credentials are exposed, revoke them immediately in the Amadeus Developer Portal

### Dependencies

- All dependencies are managed through Poetry (`pyproject.toml`)
- Dependencies are regularly updated for security patches
- Review `poetry.lock` for the exact versions in use

### Data Privacy

- Fladar processes flight search data from the Amadeus API
- No personal data is stored permanently (caching is optional and local)
- Cache files may contain flight search results (public data, not personal information)

## Security Checklist

Before each release, we verify:

- [ ] No secrets in git history
- [ ] No hardcoded credentials in source code
- [ ] All dependencies are up to date
- [ ] Security vulnerabilities in dependencies are addressed
- [ ] `.gitignore` properly excludes sensitive files
- [ ] Documentation uses placeholders, not real credentials

## Additional Resources

- [Amadeus API Security Best Practices](https://developers.amadeus.com/get-started/security-4)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Last Updated**: 2025-11-17

