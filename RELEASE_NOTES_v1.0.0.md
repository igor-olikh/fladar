# Release v1.0.0 - Initial Stable Release

**Release Date:** November 15, 2025

## 🎉 Welcome to Fladar v1.0.0!

Fladar is a powerful Python application that helps two people find the perfect meeting destination by automatically searching flights with matching arrival times. This is our first stable release, ready for production use.

---

## 🚀 What's New

### Core Features

- **Automatic Destination Discovery**: No need to manually list destinations - the app discovers them automatically using Amadeus Flight API
- **Smart Flight Matching**: Finds flights where both people arrive within a configurable time window (default: ±6 hours)
- **Comprehensive Filtering**: Filter by price, stops, duration, and departure times
- **Rich Output**: Detailed CSV with local times, airline names, and human-readable descriptions

### Advanced Features

- **Nearby Airports Search**: Search from multiple airports within a configurable radius
- **Intelligent Caching**: Reduces API calls with smart caching of destinations and flight data
- **Automatic Timezone Detection**: All times shown in local timezones automatically
- **Airport Alias Resolution**: Automatically resolves railway stations and other non-airport codes to nearest airports
- **Full Airline Names**: See airline names, not just codes (e.g., "Swiss International Air Lines" instead of "LX")

### Developer Experience

- **Comprehensive Documentation**: Extensive documentation in `docs/` folder
- **Security Best Practices**: Security checklist and proper credential management
- **Extensive Testing**: Unit tests, integration tests, and API connection tests
- **Clean Architecture**: Modular design with clear separation of concerns

---

## 📋 System Requirements

- **Python**: 3.11 or higher
- **Amadeus API**: Free account with API credentials (2,000 calls/month on free tier)
- **Dependencies**: All managed via Poetry (see `pyproject.toml`)

---

## 🎯 Quick Start

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure

Copy `config.yaml.example` to `config.yaml` and add your Amadeus API credentials:

```yaml
api:
  amadeus_api_key: "YOUR_API_KEY_HERE"
  amadeus_api_secret: "YOUR_API_SECRET_HERE"
  environment: "test"  # or "production"
```

### 3. Run

```bash
poetry run python main.py
```

For detailed setup instructions, see [README.md](README.md).

---

## 📊 What You Get

### Console Output
- Real-time progress updates
- Matching flight pairs with detailed information
- Human-readable flight details

### CSV Output
- Complete flight information
- Local times for all airports
- Airline names (not just codes)
- Human-readable descriptions
- Duration and stops information

---

## 🔧 Configuration Options

- **Origins**: Configure two origin cities (IATA codes)
- **Dates**: Set outbound and return dates
- **Price**: Maximum price per person
- **Stops**: Maximum number of stops (0 = direct only)
- **Time Constraints**: Minimum departure times for outbound and return
- **Duration**: Maximum flight duration
- **Nearby Airports**: Search radius for nearby airports
- **Caching**: Configure cache expiration and usage

See `config.yaml.example` for all available options.

---

## 📚 Documentation

- **[README.md](README.md)**: Complete setup and usage guide
- **[docs/PROJECT_EXPLANATION.md](docs/PROJECT_EXPLANATION.md)**: Detailed project overview
- **[docs/FLIGHT_RESULTS_EXPLANATION.md](docs/FLIGHT_RESULTS_EXPLANATION.md)**: How to read the output
- **[docs/api_usage_explanation.md](docs/api_usage_explanation.md)**: Amadeus API details
- **[docs/amadeus_test_vs_production.md](docs/amadeus_test_vs_production.md)**: Test vs Production guide
- **[docs/SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md)**: Security best practices

---

## 🧪 Testing

Run all tests:

```bash
poetry run python run_tests.py
```

Test API connection:

```bash
poetry run python tests/test_real_api.py
```

---

## 🔒 Security

- ✅ No hardcoded credentials
- ✅ `config.yaml` properly excluded from git
- ✅ Security checklist for contributors
- ✅ Example config with placeholders only

**Important**: Always read the [Security Checklist](docs/SECURITY_CHECKLIST.md) before adding API credentials!

---

## 🐛 Known Limitations

- **Test Environment**: Limited data coverage in Amadeus test environment (some origins may not have data)
- **API Rate Limits**: Free tier has 2,000 calls/month limit
- **Cache Files**: Currently tracked in git (contains only public data, no credentials)

---

## 🛣️ Roadmap

Future releases may include:
- Web interface
- Additional output formats (JSON, Excel)
- More filtering options
- Flight price alerts
- Historical price tracking

---

## 🤝 Contributing

Contributions are welcome! See [README.md](README.md) for contribution guidelines.

This project is licensed under GPL-3.0. See [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/igor-olikh/fladar/issues)
- **Documentation**: See `docs/` folder
- **Security**: See [docs/SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md)

---

## 🙏 Acknowledgments

- **Amadeus API**: For providing flight data
- **Open Source Community**: For the amazing libraries that make this possible

---

## 📝 Changelog

For detailed changelog, see [CHANGELOG.md](CHANGELOG.md).

---

## 🎊 Thank You!

Thank you for using Fladar! We hope it helps you find the perfect meeting destination.

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 🔄 Contributing improvements

---

**Download**: [v1.0.0](https://github.com/igor-olikh/fladar/releases/tag/v1.0.0)

**Full Changelog**: [v1.0.0](https://github.com/igor-olikh/fladar/compare/v1.0.0)

