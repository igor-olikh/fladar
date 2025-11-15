# Contributing to Fladar

Thank you for your interest in contributing to Fladar! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Git
- Amadeus API credentials (for testing)

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/fladar.git
   cd fladar
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/igor-olikh/fladar.git
   ```

4. **Install dependencies**:
   ```bash
   poetry install
   ```

5. **Set up configuration**:
   ```bash
   cp config.yaml.example config.yaml
   # Add your Amadeus API credentials to config.yaml
   ```

6. **Switch to dev branch**:
   ```bash
   git checkout dev
   git pull origin dev
   ```

## 🌿 Branching Strategy

- **`main`**: Production-ready, stable code. Only merged from `dev` after thorough testing.
- **`dev`**: Development branch. All new features and fixes go here first.

### Workflow

1. Create feature branches from `dev`
2. Make your changes
3. Submit pull request to `dev` (not `main`)
4. After review and testing, changes are merged to `dev`
5. When ready for release, `dev` is merged to `main`

## 📝 Making Changes

### Creating a Feature Branch

```bash
# Make sure you're on dev and up to date
git checkout dev
git pull upstream dev

# Create your feature branch
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### Making Your Changes

1. **Write clean, readable code**
2. **Follow existing code style**
3. **Add tests** for new features
4. **Update documentation** if needed
5. **Test your changes**:
   ```bash
   poetry run python run_tests.py
   ```

### Committing Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: description of what you added"
```

**Commit message format:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues if applicable: "Fix #123: description"

## 🧪 Testing

Before submitting a pull request:

1. **Run all tests**:
   ```bash
   poetry run python run_tests.py
   ```

2. **Test your specific changes**:
   ```bash
   poetry run python -m unittest tests.test_your_test -v
   ```

3. **Test with real API** (if applicable):
   ```bash
   poetry run python tests/test_real_api.py
   ```

4. **Check for linting errors** (if you have a linter set up)

## 📤 Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select `dev` as the base branch (not `main`)
   - Select your feature branch
   - Fill out the PR template

3. **PR Description should include**:
   - What changes you made
   - Why you made them
   - How to test the changes
   - Screenshots (if UI changes)
   - Related issues (if any)

4. **Wait for review**:
   - Address any feedback
   - Make requested changes
   - Update your PR as needed

## ✅ Code Review Checklist

Before submitting, make sure:

- [ ] Code follows existing style
- [ ] Tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No hardcoded credentials
- [ ] Security checklist reviewed (see `docs/SECURITY_CHECKLIST.md`)
- [ ] Commit messages are clear
- [ ] PR description is complete

## 🔒 Security

**IMPORTANT**: Before committing:

- [ ] Read `docs/SECURITY_CHECKLIST.md`
- [ ] Never commit `config.yaml` with real credentials
- [ ] Only commit `config.yaml.example` with placeholders
- [ ] Check for any hardcoded secrets
- [ ] Review what files are being committed

## 📚 Documentation

When adding features:

- [ ] Update README.md if needed
- [ ] Add/update docstrings in code
- [ ] Update relevant docs in `docs/` folder
- [ ] Update CHANGELOG.md (for significant changes)

## 🐛 Reporting Bugs

If you find a bug:

1. **Check existing issues** to see if it's already reported
2. **Create a new issue** with:
   - Clear title
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Error messages/logs (if any)

## 💡 Suggesting Features

Have an idea? Great!

1. **Check existing issues** for similar suggestions
2. **Create a new issue** with:
   - Clear description
   - Use case/benefit
   - Possible implementation approach (if you have ideas)

## 📋 Code Style

- Follow PEP 8 (Python style guide)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Comment complex logic

## 🎯 Areas for Contribution

We welcome contributions in:

- **New features**: Additional filtering options, output formats, etc.
- **Bug fixes**: Any issues you encounter
- **Documentation**: Improvements, examples, tutorials
- **Tests**: More test coverage
- **Performance**: Optimizations
- **UI/UX**: If we add a web interface
- **Translations**: If we add i18n support

## ❓ Questions?

- Open an issue for questions
- Check existing documentation in `docs/` folder
- Review existing code for examples

## 🙏 Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!

---

**Remember**: All pull requests should target the `dev` branch, not `main`!

