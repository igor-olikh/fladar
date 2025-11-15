# Release v1.1.0 - Enhanced Flexibility and User Experience

**Release Date:** November 27, 2025

## 🎉 What's New in v1.1.0

This release introduces enhanced flexibility for flight search preferences and improves user experience with automatic cleanup features.

---

## ✨ New Features

### Separate Max Stops Configuration
- **Individual Stop Preferences**: Each person can now have different stop preferences
  - `max_stops_person1`: Maximum stops for Person 1 flights
  - `max_stops_person2`: Maximum stops for Person 2 flights
- **Use Cases**:
  - Person 1 wants direct flights only, Person 2 accepts connections
  - Different comfort levels or travel preferences
  - More flexible trip planning

### Automatic CSV Cleanup
- **Clean Start**: CSV output files are automatically deleted at startup
- **No Confusion**: Prevents mixing old results with new searches
- **Automatic**: No configuration needed - works out of the box

---

## 🔄 Breaking Changes

### Configuration Parameter Change

**⚠️ IMPORTANT:** The `max_stops` parameter has been replaced with `max_stops_person1` and `max_stops_person2`.

**Before (v1.0.0):**
```yaml
search:
  max_stops: 0
```

**After (v1.1.0):**
```yaml
search:
  max_stops_person1: 0  # Maximum stops for Person 1 flights
  max_stops_person2: 0  # Maximum stops for Person 2 flights
```

**Migration:**
- See [Migration Guide](docs/MIGRATION_GUIDE.md) for detailed instructions
- Backward compatibility: Old `max_stops` parameter will work with deprecation warnings
- Recommended: Update your config.yaml to use new parameters

---

## 📚 Documentation Updates

- **Migration Guide**: Comprehensive guide for upgrading from v1.0.0
- **Updated Examples**: All documentation updated with new parameter structure
- **API Documentation**: Updated to reflect new parameter logic
- **README**: Added migration note for users upgrading

---

## 🐛 Bug Fixes

- CSV output files from previous runs are now automatically cleaned up at startup

---

## 🔧 Technical Improvements

- **Backward Compatibility**: Automatic fallback for old `max_stops` parameter with deprecation warnings
- **Better Logging**: Clear warnings when using deprecated parameters
- **Version Management**: Proper semantic versioning and changelog tracking

---

## 📋 System Requirements

- **Python**: 3.11 or higher (unchanged)
- **Amadeus API**: Free account with API credentials (unchanged)
- **Dependencies**: All managed via Poetry (unchanged)

---

## 🚀 Quick Start for New Users

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure

Copy `config.yaml.example` to `config.yaml` and update:

```yaml
origins:
  person1: "TLV"  # Your origin
  person2: "ALC"  # Other person's origin

search:
  outbound_date: "2025-11-27"
  return_date: "2025-12-02"
  max_price: 600
  max_stops_person1: 0  # Direct flights only for Person 1
  max_stops_person2: 1  # Up to 1 stop for Person 2
```

### 3. Run

```bash
poetry run python main.py
```

---

## 📖 Upgrading from v1.0.0

If you're upgrading from v1.0.0, please follow these steps:

1. **Read the Migration Guide**: See [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
2. **Update Your Config**: Replace `max_stops` with `max_stops_person1` and `max_stops_person2`
3. **Test Your Configuration**: Run the application to verify everything works

**Quick Migration:**
```yaml
# Old (v1.0.0)
max_stops: 0

# New (v1.1.0)
max_stops_person1: 0
max_stops_person2: 0
```

---

## 📦 Download

- **Source Code**: [Download ZIP](https://github.com/igor-olikh/fladar/archive/v1.1.0.zip)
- **Git Tag**: `v1.1.0`
- **Release Page**: [View on GitHub](https://github.com/igor-olikh/fladar/releases/tag/v1.1.0)

---

## 🔗 Links

- **Documentation**: [README.md](README.md)
- **Migration Guide**: [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Issues**: [Report an Issue](https://github.com/igor-olikh/fladar/issues)

---

## 🙏 Thank You

Thank you for using Fladar! If you encounter any issues or have suggestions, please open an issue on GitHub.

---

## 📝 Full Changelog

For a complete list of changes, see [CHANGELOG.md](CHANGELOG.md).

**Key Changes:**
- Added `max_stops_person1` and `max_stops_person2` parameters
- Automatic CSV cleanup at startup
- Backward compatibility with deprecation warnings
- Comprehensive migration guide
- Updated all documentation

---

**Previous Release**: [v1.0.0](RELEASE_NOTES_v1.0.0.md)

