# Security Checklist - Pre-Commit Review

This document describes what to check before committing code to ensure no sensitive information is exposed in the repository.

## 🔒 Critical Checks

### 1. Configuration Files

**Check:** `config.yaml` should NEVER be committed
- ✅ `config.yaml` is in `.gitignore`
- ✅ Only `config.yaml.example` (with placeholders) should be tracked
- ❌ Never commit `config.yaml` with real API keys

**How to verify:**
```bash
# Check if config.yaml is tracked
git ls-files | grep config.yaml

# Should only show: config.yaml.example
# Should NOT show: config.yaml
```

**What to look for:**
- Real API keys (not "YOUR_API_KEY_HERE")
- Real API secrets (not "YOUR_API_SECRET_HERE")
- Any actual credentials

### 2. API Keys and Secrets

**Check:** No real API credentials in any tracked files

**Search for sensitive patterns:**
```bash
# Search for API key patterns (should only find placeholders)
git grep -i "amadeus_api_key\|amadeus_api_secret" -- "*.py" "*.yaml" "*.yml" "*.md"

# Should only find:
# - "YOUR_API_KEY_HERE"
# - "YOUR_API_SECRET_HERE"
# - Example/test code
# Should NOT find actual keys like: "abc123xyz..." or "sk_live_..."
```

**What to look for:**
- Long alphanumeric strings that look like API keys
- Keys starting with common patterns: `sk_`, `pk_`, `AKIA`, `ghp_`, etc.
- Any strings that look like secrets (long random strings)

### 3. Environment Variables

**Check:** No hardcoded environment variables with real values

**Search for:**
```bash
git grep -i "os.environ\|getenv\|environ\[" -- "*.py"
```

**What to look for:**
- Hardcoded values instead of reading from environment/config
- Actual credentials in environment variable assignments

### 4. Cache Files

**Check:** Cache files don't contain sensitive information

**Files to review:**
- `data/destinations_cache/*.json` - Should only contain destination data
- `data/flights_cache/*.json` - Should only contain flight data

**What to look for:**
- API keys in cached responses
- Authentication tokens
- Personal information (though flight data is generally safe)

**Note:** Cache files are currently tracked in git. Consider:
- Moving them to `.gitignore` if they contain any sensitive data
- Or keeping them if they're safe (just flight/destination data)

### 5. Log Files

**Check:** No log files with sensitive information

**Files to check:**
- `debug_logs/*.log` - Should be in `.gitignore` ✅
- Any `*.log` files

**What to look for:**
- API keys in error messages
- Full request/response bodies with credentials
- Stack traces exposing file paths with sensitive data

### 6. Output Files

**Check:** No output files with sensitive data

**Files to check:**
- `*.csv` files (should be in `.gitignore` ✅)
- `flight_results.csv` (should be in `.gitignore` ✅)

**What to look for:**
- Personal information
- API keys in output
- Any sensitive data

### 7. Python Files

**Check:** No hardcoded credentials in source code

**Search for:**
```bash
# Search for common credential patterns
git grep -E "(api[_-]?key|api[_-]?secret|password|token|credential)" -- "*.py" -i

# Search for long strings that might be keys
git grep -E "[a-zA-Z0-9]{32,}" -- "*.py"
```

**What to look for:**
- Hardcoded API keys
- Hardcoded secrets
- Passwords
- Tokens
- Any long random strings

### 8. Documentation Files

**Check:** Documentation only contains placeholders, not real keys

**Files to check:**
- `README.md`
- `docs/*.md`
- `PROJECT_EXPLANATION.md`
- `FLIGHT_RESULTS_EXPLANATION.md`

**What to look for:**
- Only "YOUR_API_KEY_HERE" type placeholders
- No actual credentials in examples
- No real API keys in screenshots or examples

## 🔍 Automated Checks

### Pre-Commit Hook (Optional)

You can create a pre-commit hook to automatically check for secrets:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for real API keys (not placeholders)
if git diff --cached | grep -E "amadeus_api_key|amadeus_api_secret" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example"; then
    echo "ERROR: Found potential API key in staged files!"
    echo "Make sure you're only committing config.yaml.example with placeholders"
    exit 1
fi

# Check if config.yaml is being committed
if git diff --cached --name-only | grep -E "^config\.yaml$"; then
    echo "ERROR: config.yaml should not be committed!"
    echo "Only config.yaml.example should be tracked"
    exit 1
fi

exit 0
```

### Using git-secrets (Advanced)

Install and configure git-secrets for automatic detection:

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or download from: https://github.com/awslabs/git-secrets

# Configure for this repo
cd /path/to/fladar
git secrets --install
git secrets --register-aws  # For AWS patterns
git secrets --add 'amadeus.*[a-zA-Z0-9]{32,}'  # Custom pattern
```

## 📋 Manual Review Checklist

Before each commit, manually verify:

- [ ] `config.yaml` is NOT in the commit (check with `git status`)
- [ ] Only `config.yaml.example` is tracked
- [ ] All API key references are placeholders ("YOUR_API_KEY_HERE")
- [ ] No real credentials in any Python files
- [ ] No credentials in documentation files
- [ ] Cache files don't contain sensitive data
- [ ] Log files are not committed
- [ ] Output files (CSV) are not committed
- [ ] No hardcoded secrets in source code
- [ ] Environment variables are read from config, not hardcoded

## 🚨 If You Find Sensitive Information

If you accidentally commit sensitive information:

1. **Immediately revoke the exposed credentials:**
   - Go to Amadeus Developer Portal
   - Regenerate API keys
   - Update your local `config.yaml`

2. **Remove from git history:**
   ```bash
   # Remove file from history (if it was committed)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config.yaml" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (WARNING: This rewrites history)
   git push origin --force --all
   ```

3. **Verify removal:**
   ```bash
   # Check git history
   git log --all --full-history -- config.yaml
   ```

4. **Update .gitignore:**
   - Ensure `config.yaml` is in `.gitignore`
   - Verify it's working: `git status` should not show `config.yaml`

## ✅ Current Security Status

### Files in .gitignore (Safe):
- ✅ `config.yaml` - Contains real API keys
- ✅ `*.csv` - Output files
- ✅ `debug_logs/` - Log files
- ✅ `*.log` - Log files
- ✅ `data/flights_cache/` - Flight cache (may contain data)
- ✅ `.venv/` - Virtual environment

### Files Tracked (Should be safe):
- ✅ `config.yaml.example` - Only placeholders
- ✅ `data/destinations_cache/*.json` - Only destination data (no credentials)
- ✅ `data/airport_names.json` - Public data
- ✅ `data/airline_names.json` - Public data
- ⚠️ `data/destinations_cache/*.json` - Cache files (review if needed)

### Recommended Actions:
1. ✅ `config.yaml` is properly ignored
2. ✅ Only example config is tracked
3. ⚠️ Consider moving cache files to `.gitignore` if they grow large
4. ✅ All source code uses config file (no hardcoded keys)

## 📝 Notes

- **Never commit `config.yaml`** - It contains your real API credentials
- **Always use `config.yaml.example`** - This is the template with placeholders
- **Review cache files** - They're currently tracked; ensure they don't contain sensitive data
- **Check before pushing** - Run the manual checklist before each push
- **Use environment variables** - For CI/CD, use environment variables instead of config files

## 🔗 Related Documentation

- [Amadeus API Security Best Practices](https://developers.amadeus.com/get-started/security-4)
- [Git Secrets Management](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

