# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-15

### ✨ Added
- **Separate Max Stops Configuration**: Added `max_stops_person1` and `max_stops_person2` parameters to allow different stop preferences for each person
- **Automatic CSV Cleanup**: CSV output file is now automatically deleted at startup to prevent confusion from old results
- **Migration Guide**: Added `docs/MIGRATION_GUIDE.md` to help users upgrade from v1.0.0

### 🔄 Changed
- **Breaking Change**: Replaced single `max_stops` parameter with `max_stops_person1` and `max_stops_person2` in configuration
  - Old config files using `max_stops` will need to be updated
  - See `docs/MIGRATION_GUIDE.md` for migration instructions

### 📚 Documentation
- Updated all documentation to reflect new parameter structure
- Added comprehensive migration guide for upgrading from v1.0.0
- Updated README.md, PROJECT_EXPLANATION.md, and all API documentation

### 🐛 Fixed
- CSV output files from previous runs are now automatically cleaned up at startup

---

## [1.0.0] - 2025-11-15

### 🎉 Initial Release

First stable release of Fladar - Flight Meeting Destination Finder.

### ✨ Features

- **Dynamic Destination Discovery**: Automatically finds destinations using Amadeus Flight Inspiration Search API
- **Smart Flight Matching**: Matches flights where both people arrive within configurable time window (±3-6 hours)
- **Price Filtering**: Filters by maximum price per person for round-trip flights
- **Time Constraints**: Separate minimum departure times for outbound and return flights
- **Stops Control**: Configurable maximum stops (default: direct flights only)
- **Duration Filtering**: Optional maximum flight duration limit
- **Nearby Airports Search**: Search from nearby airports within configurable radius
- **Intelligent Caching**: Caches destination and flight data to reduce API calls
- **Rich CSV Output**: Detailed CSV with local times, airline names, human-readable descriptions
- **Automatic Timezone Detection**: Automatic timezone detection for all airports
- **Airport Alias Resolution**: Automatically resolves non-airport codes (e.g., railway stations) to nearest airports
- **Airline Name Mapping**: Full airline names in output (not just codes)
- **Human-Readable Formats**: Duration, stops, and descriptions in easy-to-read format

### 🔧 Technical Features

- **Amadeus API Integration**: Full integration with Amadeus Flight API
- **Test/Production Environment Support**: Switch between test and production API environments
- **Comprehensive Error Handling**: Detailed error messages and logging
- **Modular Architecture**: Clean separation of concerns (FlightSearch, DestinationFinder, OutputFormatter)
- **Extensive Testing**: Unit tests, integration tests, and API connection tests
- **Comprehensive Documentation**: Detailed documentation in `docs/` folder
- **Security Best Practices**: Security checklist and proper credential management

### 📚 Documentation

- Complete README with quick start guide
- API usage explanation
- Test vs Production environment guide
- Security checklist
- Project explanation
- Flight results explanation
- GitHub setup guides

### 🛠️ Configuration

- YAML-based configuration
- Support for multiple search parameters
- Configurable caching
- Flexible output formats (console, CSV, or both)

### 🧪 Testing

- Unit tests for core functionality
- Integration tests for end-to-end workflows
- API connection tests
- Test runner script

### 🔒 Security

- `.gitignore` properly configured
- Security checklist for pre-commit review
- No hardcoded credentials
- Example config file with placeholders

### 📦 Dependencies

- Python 3.11+
- Amadeus SDK
- PyYAML
- pytz
- airportsdata
- timezonefinder

### 🎯 Use Cases

- Planning trips with friends or family
- Finding meeting points between two cities
- Discovering travel destinations
- Comparing flight options

### 📝 Notes

- Requires Amadeus API credentials (free tier available)
- Free tier includes 2,000 API calls per month
- Test environment has limited data coverage
- Production environment recommended for real searches

---

## Version History

- **1.1.0** (2025-11-15): Added separate max_stops configuration per person, automatic CSV cleanup
- **1.0.0** (2025-11-15): Initial stable release

[1.1.0]: https://github.com/igor-olikh/fladar/releases/tag/v1.1.0
[1.0.0]: https://github.com/igor-olikh/fladar/releases/tag/v1.0.0

