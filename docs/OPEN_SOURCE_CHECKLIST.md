# Open Source Release Checklist

This document outlines all the steps you need to complete before making Fladar open source on GitHub.

## 🔴 CRITICAL - Security & Credentials

### ✅ Already Done
- [x] `config.yaml` is in `.gitignore` (not tracked in git)
- [x] Only `config.yaml.example` with placeholders is tracked
- [x] Security checklist exists (`docs/SECURITY_CHECKLIST.md`)
- [x] SECURITY.md exists for vulnerability reporting

### ⚠️ ACTION REQUIRED

1. **Verify `config.yaml` is NOT in git history**
   ```bash
   git ls-files | grep config.yaml
   # Should only show: config.yaml.example
   # Should NOT show: config.yaml
   ```
   - ✅ **Status**: Already verified - `config.yaml` is NOT tracked

2. **Check git history for any committed credentials**
   ```bash
   # Search entire git history for API keys
   git log --all --full-history -p | grep -i "amadeus_api_key\|amadeus_api_secret" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example"
   ```
   - ⚠️ **ACTION**: Run this command and verify no real credentials appear in history
   - If credentials are found in history, you'll need to:
     - Revoke those credentials immediately
     - Consider using `git filter-branch` or BFG Repo-Cleaner to remove them from history
     - Or create a fresh repository without the history

3. **Verify local `config.yaml` contains no secrets that could be accidentally committed**
   - ⚠️ **ACTION**: Double-check that `config.yaml` is properly ignored
   - Current status: File exists locally with real credentials, but is in `.gitignore` ✅

4. **Review all tracked files for sensitive data**
   ```bash
   # Check for any hardcoded credentials in tracked files
   git grep -i "api_key\|api_secret\|password\|token" -- "*.py" "*.yaml" "*.md" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret"
   ```
   - ⚠️ **ACTION**: Review results - should only find placeholders and documentation

---

## 📝 Documentation

### ✅ Already Done
- [x] README.md exists and is comprehensive
- [x] LICENSE file exists (GPL-3.0)
- [x] CONTRIBUTING.md exists (`.github/CONTRIBUTING.md`)
- [x] CHANGELOG.md exists
- [x] Security checklist exists (`docs/SECURITY_CHECKLIST.md`)
- [x] SECURITY.md exists for vulnerability reporting
- [x] CODE_OF_CONDUCT.md exists
- [x] Multiple documentation files in `docs/` folder
- [x] Release notes exist (v1.0.0 and v1.1.0)

### ⚠️ ACTION REQUIRED

1. **Verify `pyproject.toml` author email**
   - Current: `"Igor Olikh <igor-olikh@users.noreply.github.com>"`
   - ✅ **Status**: Already using GitHub noreply email (privacy-friendly)

2. **Verify CODE_OF_CONDUCT.md**
   - ✅ **Status**: CODE_OF_CONDUCT.md exists and is properly configured

3. **Verify SECURITY.md**
   - ✅ **Status**: SECURITY.md exists for vulnerability reporting

4. **Review and update README.md**
   - ✅ Already comprehensive
   - ⚠️ **ACTION**: Verify all links work (especially GitHub links)
   - ⚠️ **ACTION**: Ensure all examples use placeholders, not real credentials

5. **Add GitHub Topics** (After repository is public)
   - ⚠️ **ACTION**: Add relevant topics to repository for discoverability
   - Suggested topics: `flight-search`, `amadeus-api`, `travel`, `python`, `flight-finder`, `meeting-destinations`, `travel-planner`
   - See `.github/TOPICS.md` for more suggestions

---

## 🔧 Code Quality

### ✅ Already Done
- [x] Code is well-structured and modular
- [x] Error handling is comprehensive
- [x] Logging is implemented
- [x] Tests exist (unit tests, integration tests)
- [x] Type hints are used in some places

### ⚠️ ACTION REQUIRED

1. **Review TODO/FIXME comments**
   - ⚠️ **ACTION**: Search for TODO/FIXME comments and either:
     - Implement them
     - Create GitHub issues for them
     - Remove them if not needed
   ```bash
   grep -r "TODO\|FIXME\|XXX\|HACK" --include="*.py"
   ```

2. **Code formatting consistency**
   - ⚠️ **ACTION**: Consider adding a formatter (black, autopep8) and formatter config
   - ⚠️ **ACTION**: Consider adding a linter (flake8, pylint) and linting config

3. **Add type hints everywhere** (Optional but recommended)
   - ⚠️ **ACTION**: Add type hints to all functions for better code documentation

---

## 🧪 Testing

### ✅ Already Done
- [x] Test files exist (`tests/` directory)
- [x] Test runner script exists (`run_tests.py`)
- [x] Unit tests, integration tests, and API connection tests exist

### ⚠️ ACTION REQUIRED

1. **Ensure all tests pass**
   ```bash
   poetry run python run_tests.py
   ```
   - ⚠️ **ACTION**: Run all tests and fix any failures

2. **Verify CI/CD** (Recommended)
   - ✅ **Status**: GitHub Actions workflow exists (`.github/workflows/test.yml`)
   - ✅ Tests run on push/PR for main and dev branches
   - ✅ Tests run on Python 3.11 and 3.12
   - ⚠️ **OPTIONAL**: Consider adding:
     - Security scanning (e.g., `github/codeql-action`)
     - Dependency vulnerability scanning (e.g., `snyk/actions/python`)
     - Code linting/formatting checks

---

## 📦 Dependencies & Configuration

### ✅ Already Done
- [x] `pyproject.toml` exists with Poetry configuration
- [x] `requirements.txt` exists (alternative to Poetry)
- [x] Dependencies are clearly specified
- [x] Python version requirement is specified (3.11+)

### ⚠️ ACTION REQUIRED

1. **Verify all dependencies are necessary**
   - ⚠️ **ACTION**: Review dependencies and remove any unused ones

2. **Pin dependency versions** (Optional but recommended for stability)
   - ⚠️ **ACTION**: Consider pinning exact versions or using version ranges
   - Current: Uses `>=` which is fine for flexibility
   - Note: `poetry.lock` pins exact versions for reproducible builds

3. **Check dependency licenses**
   - ⚠️ **ACTION**: Verify all dependency licenses are compatible with GPL-3.0
   - Main dependencies:
     - `amadeus` - Check license compatibility
     - `pyyaml` - MIT License (compatible)
     - `pytz` - MIT License (compatible)
     - `airportsdata` - Check license
     - `timezonefinder` - Check license
   - ⚠️ **ACTION**: Document dependency licenses in README or separate file
   - ⚠️ **ACTION**: Run license check tool (e.g., `pip-licenses` or `poetry show --tree`)

---

## 🗂️ Repository Structure

### ✅ Already Done
- [x] `.gitignore` is properly configured
- [x] Project structure is clean and organized
- [x] Documentation is well-organized in `docs/` folder

### ⚠️ ACTION REQUIRED

1. **Clean up untracked files**
   - ⚠️ **ACTION**: Review untracked files and either:
     - Add to `.gitignore` if they shouldn't be tracked
     - Remove if they're temporary
     - Commit if they should be tracked
   ```bash
   git status
   ```

2. **Review cached data files**
   - Current: `data/destinations_cache/` is tracked (contains only public data)
   - Current: `data/flights_cache/` is in `.gitignore` ✅
   - ⚠️ **ACTION**: Verify `data/destinations_cache/` files don't contain any sensitive data
   - ⚠️ **ACTION**: Consider if you want to include cache files in the repository or remove them

3. **Remove or clean up debug logs**
   - Current: `debug_logs/` is in `.gitignore` ✅
   - ⚠️ **ACTION**: Verify no log files are tracked in git
   ```bash
   git ls-files | grep "\.log$"
   ```

4. **Remove generated output files**
   - Current: `*.csv` and `flight_results.html` are in `.gitignore` ✅
   - ⚠️ **ACTION**: Verify no output files are tracked
   ```bash
   git ls-files | grep -E "\.csv$|\.html$"
   ```

---

## 🔢 Version Management

### ✅ Already Done
- [x] Version specified in `pyproject.toml` (1.1.0)
- [x] Version specified in `main.py` (`__version__ = "1.1.0"`)
- [x] CHANGELOG.md follows Keep a Changelog format
- [x] Semantic versioning is used

### ⚠️ ACTION REQUIRED

1. **Verify version consistency**
   ```bash
   # Check version in pyproject.toml
   grep "version = " pyproject.toml
   
   # Check version in main.py
   grep "__version__" main.py
   
   # Check latest version in CHANGELOG.md
   head -20 CHANGELOG.md
   ```
   - ⚠️ **ACTION**: Ensure all version numbers match
   - Current: All files show version 1.1.0 ✅

2. **Before each release:**
   - [ ] Update version in `pyproject.toml`
   - [ ] Update version in `main.py`
   - [ ] Update CHANGELOG.md with new version entry
   - [ ] Ensure all changes are documented in CHANGELOG.md
   - [ ] Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   - [ ] Push tag: `git push origin vX.Y.Z`

---

## 🔨 Build Reproducibility

### ✅ Already Done
- [x] `poetry.lock` exists (locks dependency versions)
- [x] `requirements.txt` exists (alternative installation method)
- [x] Build system specified in `pyproject.toml`

### ⚠️ ACTION REQUIRED

1. **Verify reproducible builds**
   ```bash
   # Test clean installation
   rm -rf .venv poetry.lock
   poetry install
   poetry run python -c "import flight_search; print('✓ Build successful')"
   ```
   - ⚠️ **ACTION**: Verify installation works from scratch
   - ⚠️ **ACTION**: Test on multiple Python versions (3.11, 3.12)

2. **Document build process**
   - ✅ README.md includes installation instructions
   - ⚠️ **OPTIONAL**: Add `BUILD.md` with detailed build instructions

---

## 🔐 GitHub Repository Settings

### ⚠️ ACTION REQUIRED (After making repository public)

1. **Repository Description**
   - ⚠️ **ACTION**: Add a clear, concise description
   - Suggested: "Find meeting destinations for two people by automatically searching flights with matching arrival times"

2. **Repository Topics**
   - ⚠️ **ACTION**: Add relevant topics (see `.github/TOPICS.md`)

3. **Enable Issues**
   - ⚠️ **ACTION**: Enable GitHub Issues for bug reports and feature requests

4. **Enable Discussions** (Optional)
   - ⚠️ **ACTION**: Consider enabling GitHub Discussions for Q&A

5. **Add Repository Badges** (Optional)
   - ⚠️ **ACTION**: Add badges to README (license, Python version, etc.)
   - Example:
     ```markdown
     ![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
     ![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
     ```

6. **Set up Branch Protection** (Recommended)
   - ⚠️ **ACTION**: Protect `main` branch:
     - Require pull request reviews
     - Require status checks to pass
     - Require branches to be up to date

---

## 📋 Pre-Release Checklist

Before making the repository public, complete this final checklist:

### Security
- [ ] Verified `config.yaml` is NOT in git history
- [ ] Searched entire git history for credentials
- [ ] Verified all tracked files contain no real credentials
- [ ] Reviewed `.gitignore` is comprehensive
- [ ] Tested that `config.yaml` cannot be accidentally committed
- [ ] SECURITY.md exists and is accessible
- [ ] Security vulnerability reporting process is documented

### Documentation
- [ ] Verified author email in `pyproject.toml` (or confirmed privacy-friendly)
- [ ] CODE_OF_CONDUCT.md exists
- [ ] SECURITY.md exists
- [ ] Verified all README links work
- [ ] Reviewed all documentation for accuracy
- [ ] Ensured all examples use placeholders
- [ ] CHANGELOG.md is up to date

### Code
- [ ] All tests pass
- [ ] Reviewed and addressed TODO/FIXME comments
- [ ] Code is clean and well-documented
- [ ] No hardcoded secrets or credentials
- [ ] CI/CD pipeline passes
- [ ] Code compiles without errors

### Repository
- [ ] Cleaned up untracked files
- [ ] Reviewed cached data files
- [ ] Verified no log files are tracked
- [ ] Verified no output files are tracked
- [ ] Repository structure is clean
- [ ] Version numbers are consistent across all files
- [ ] Dependency licenses are verified and documented

### GitHub
- [ ] Repository description is set
- [ ] Topics are added
- [ ] Issues are enabled
- [ ] README badges are added (optional)
- [ ] Branch protection is configured (recommended)
- [ ] SECURITY.md is accessible (GitHub will show security policy link)

---

## 🚀 Making It Public

Once all items above are completed:

1. **Final verification**
   ```bash
   # Double-check for any secrets
   git grep -i "api_key\|api_secret" -- "*.py" "*.yaml" "*.md" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret"
   
   # Verify config.yaml is not tracked
   git ls-files | grep config.yaml
   
   # Check git status
   git status
   ```

2. **Commit any final changes**
   ```bash
   git add .
   git commit -m "chore: Final preparations for open source release"
   git push origin main
   ```

3. **Make repository public**
   - Go to GitHub repository settings
   - Scroll to "Danger Zone"
   - Click "Change visibility"
   - Select "Make public"

4. **Post-release tasks**
   - [ ] Add repository topics
   - [ ] Create a GitHub release for current version (v1.1.0)
   - [ ] Create git tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
   - [ ] Push tag: `git push origin v1.1.0`
   - [ ] Share on social media/communities (optional)
   - [ ] Monitor issues and pull requests

---

## 📚 Additional Resources

- [GitHub Open Source Guide](https://opensource.guide/)
- [Choose a License](https://choosealicense.com/)
- [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

## ✅ Quick Verification Script

Run this script to quickly verify critical items:

```bash
#!/bin/bash
echo "🔍 Verifying open source readiness..."

echo ""
echo "1. Checking config.yaml is not tracked..."
if git ls-files | grep -q "^config\.yaml$"; then
    echo "   ❌ ERROR: config.yaml is tracked in git!"
else
    echo "   ✅ config.yaml is not tracked"
fi

echo ""
echo "2. Checking for real API keys in tracked files..."
if git grep -i "amadeus_api_key\|amadeus_api_secret" -- "*.py" "*.yaml" "*.md" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret" | grep -q .; then
    echo "   ❌ WARNING: Found potential API keys in tracked files!"
    git grep -i "amadeus_api_key\|amadeus_api_secret" -- "*.py" "*.yaml" "*.md" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret"
else
    echo "   ✅ No real API keys found in tracked files"
fi

echo ""
echo "3. Checking for log files in git..."
if git ls-files | grep -q "\.log$"; then
    echo "   ⚠️  WARNING: Log files are tracked in git"
    git ls-files | grep "\.log$"
else
    echo "   ✅ No log files tracked"
fi

echo ""
echo "4. Checking for output files in git..."
if git ls-files | grep -qE "\.csv$|flight_results\.html$"; then
    echo "   ⚠️  WARNING: Output files are tracked in git"
    git ls-files | grep -E "\.csv$|flight_results\.html$"
else
    echo "   ✅ No output files tracked"
fi

echo ""
echo "5. Checking essential files exist..."
files=("README.md" "LICENSE" ".github/CONTRIBUTING.md" "CHANGELOG.md" "pyproject.toml" ".gitignore" "SECURITY.md" "CODE_OF_CONDUCT.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file is missing!"
    fi
done

echo ""
echo "6. Checking version consistency..."
pyproject_version=$(grep "version = " pyproject.toml | sed 's/.*version = "\(.*\)"/\1/')
main_version=$(grep "__version__" main.py | sed 's/.*__version__ = "\(.*\)"/\1/')
if [ "$pyproject_version" == "$main_version" ]; then
    echo "   ✅ Versions match: $pyproject_version"
else
    echo "   ❌ Version mismatch: pyproject.toml=$pyproject_version, main.py=$main_version"
fi

echo ""
echo "7. Checking for SECURITY.md..."
if [ -f "SECURITY.md" ]; then
    echo "   ✅ SECURITY.md exists"
else
    echo "   ⚠️  SECURITY.md is missing (recommended)"
fi

echo ""
echo "✅ Verification complete!"
```

Save this as `verify_opensource.sh`, make it executable (`chmod +x verify_opensource.sh`), and run it.

---

## 📦 Release Process

### Pre-Release Steps

1. **Update version numbers**
   ```bash
   # Update pyproject.toml
   # Update main.py __version__
   # Update CHANGELOG.md with new version entry
   ```

2. **Run verification script**
   ```bash
   ./verify_opensource.sh
   ```

3. **Run all tests**
   ```bash
   poetry run python run_tests.py
   ```

4. **Check for secrets**
   ```bash
   git grep -i "api_key\|api_secret" -- "*.py" "*.yaml" "*.md" | grep -v "YOUR_API_KEY\|YOUR_API_SECRET\|example\|test_key\|test_secret"
   ```

5. **Update CHANGELOG.md**
   - Add new version entry
   - Document all changes since last release
   - Follow [Keep a Changelog](https://keepachangelog.com/) format

6. **Commit changes**
   ```bash
   git add .
   git commit -m "chore: Prepare release vX.Y.Z"
   git push origin main
   ```

### Creating a Release

1. **Create and push tag**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

2. **Create GitHub Release**
   - Go to GitHub repository → Releases → Draft a new release
   - Select the tag you just created
   - Use CHANGELOG.md content for release notes
   - Mark as "Latest release" if this is the newest version
   - Publish release

3. **Post-release verification**
   - [ ] Verify release appears on GitHub
   - [ ] Verify tag is pushed
   - [ ] Verify release notes are correct
   - [ ] Test installation from GitHub release (if applicable)

---

**Last Updated**: 2025-11-17
**Version**: 2.0

