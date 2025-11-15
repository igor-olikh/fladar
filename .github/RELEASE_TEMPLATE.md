# GitHub Release Notes Template

Use this template when creating a release on GitHub.

## Release Title
```
v1.0.0 - Initial Stable Release
```

## Release Description

Copy and paste the content from `RELEASE_NOTES_v1.0.0.md` or use this template:

```markdown
# 🎉 Fladar v1.0.0 - Initial Stable Release

**Release Date:** November 15, 2025

## What's New

Fladar is a powerful Python application that helps two people find the perfect meeting destination by automatically searching flights with matching arrival times.

### ✨ Key Features

- **Automatic Destination Discovery**: Discovers destinations using Amadeus Flight API
- **Smart Flight Matching**: Matches flights with configurable arrival time windows
- **Comprehensive Filtering**: Price, stops, duration, and departure times
- **Rich CSV Output**: Detailed output with local times and airline names
- **Intelligent Caching**: Reduces API calls with smart caching
- **Automatic Timezone Detection**: All times in local timezones

### 🚀 Quick Start

```bash
poetry install
cp config.yaml.example config.yaml
# Add your Amadeus API credentials to config.yaml
poetry run python main.py
```

### 📚 Documentation

- [README.md](README.md) - Complete setup guide
- [docs/](docs/) - Detailed documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history

### 🔒 Security

Always read the [Security Checklist](docs/SECURITY_CHECKLIST.md) before adding API credentials!

### 📦 Download

**Source Code**: [Download ZIP](https://github.com/igor-olikh/fladar/archive/refs/tags/v1.0.0.zip)

**Clone**: `git clone https://github.com/igor-olikh/fladar.git -b v1.0.0`

### 🎯 Use Cases

- Planning trips with friends or family
- Finding meeting points between two cities
- Discovering travel destinations
- Comparing flight options

### 📝 Requirements

- Python 3.11+
- Amadeus API credentials (free tier available)
- See [README.md](README.md) for full requirements

### 🙏 Thank You!

Thank you for using Fladar! If you find it useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features

---

**Full Release Notes**: [RELEASE_NOTES_v1.0.0.md](RELEASE_NOTES_v1.0.0.md)
**Changelog**: [CHANGELOG.md](CHANGELOG.md)
```

## How to Create a GitHub Release

1. Go to your repository on GitHub
2. Click on "Releases" (right sidebar)
3. Click "Draft a new release"
4. **Tag version**: `v1.0.0`
5. **Release title**: `v1.0.0 - Initial Stable Release`
6. **Description**: Copy from `RELEASE_NOTES_v1.0.0.md` or use template above
7. Check "Set as the latest release"
8. Click "Publish release"

## Attachments (Optional)

You can attach:
- Source code (zip)
- Release notes PDF (if you create one)
- Screenshots (if applicable)

## Release Checklist

- [ ] Version number updated in code
- [ ] CHANGELOG.md updated
- [ ] RELEASE_NOTES created
- [ ] Git tag created
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security checklist reviewed
- [ ] GitHub release created
- [ ] Release notes published

