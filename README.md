# Flight Search Application

A Python application that finds destinations where two people can meet by searching for flights with matching arrival times.

## Features

- 🔍 Automatically finds destinations where both people can meet
- ⏰ Matches flight arrivals within ±3 hours (configurable)
- 💰 Filters by maximum price per person
- ⏱️ Optional time constraints (minimum departure/arrival times)
- 🚫 Configurable maximum stops (default: direct flights only)
- 📊 Outputs results to console and/or CSV

## Setup

### 1. Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or on macOS with Homebrew:
```bash
brew install poetry
```

### 2. Install Dependencies with Poetry

This project uses Poetry for dependency management. Poetry will automatically create a virtual environment in the `.venv` directory.

```bash
# Install dependencies (creates virtual environment automatically)
poetry install

# Verify the virtual environment is set up
poetry env info
```

**Note:** The virtual environment is automatically created in `.venv/` directory within the project. Poetry is configured to use Python 3.11.

### Alternative: Using pip (not recommended)

If you prefer not to use Poetry, you can still use pip:

```bash
pip install -r requirements.txt
```

### 3. Get Amadeus API Credentials

1. Go to [Amadeus for Developers](https://developers.amadeus.com/)
2. Sign up for a free account
3. Create a new app to get your API Key and API Secret
4. The free tier includes 2,000 API calls per month

### 4. Configure the Application

Edit `config.yaml` and add your API credentials:

```yaml
api:
  amadeus_api_key: "YOUR_API_KEY_HERE"
  amadeus_api_secret: "YOUR_API_SECRET_HERE"
```

You can also customize:
- Origin cities (default: Tel Aviv and Alicante)
- Dates for outbound and return flights
- Maximum price per person
- Maximum number of stops
- Arrival time tolerance
- Optional time constraints

## Usage

1. Update `config.yaml` with your search parameters
2. Run the application:

**With Poetry (recommended):**
```bash
poetry run python main.py
```

**Or activate the virtual environment first:**
```bash
# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Then run
python main.py
```

The application will:
1. Search multiple destinations automatically
2. Find flights from both origins to each destination
3. Match flights where arrivals are within the tolerance window
4. Filter by price and other constraints
5. Display results in console and/or export to CSV

## Configuration Options

### Origins
- `person1`: IATA code for person 1's origin (default: "TLV" - Tel Aviv)
- `person2`: IATA code for person 2's origin (default: "ALC" - Alicante)

### Search Parameters
- `outbound_date`: Departure date (format: YYYY-MM-DD)
- `return_date`: Return date (format: YYYY-MM-DD)
- `max_price`: Maximum total round-trip price per person (in EUR)
- `max_stops`: Maximum number of stops (0 = direct flights only)
- `arrival_tolerance_hours`: Hours tolerance for arrival times (default: 3)
- `min_departure_time`: Minimum departure time (format: HH:MM, optional)
- `min_arrival_time`: Minimum arrival time (format: HH:MM, optional)

### Output Settings
- `format`: Output format - "console", "csv", or "console,csv"
- `csv_file`: Path for CSV output file

## Example Output

The application will display:
- Destination city
- Total price for both flights
- Individual flight details for each person:
  - Outbound and return flight times
  - Flight duration
  - Number of stops
  - Airlines
  - Price

Results are sorted by total price (cheapest first).

## Notes

- The application searches popular European destinations by default
- Amadeus API has rate limits on the free tier (2,000 calls/month)
- Flight prices and availability are subject to change
- IATA airport codes are used (e.g., TLV for Tel Aviv, ALC for Alicante)

## Running Tests

Run all tests to verify the application works correctly:

**With Poetry:**
```bash
poetry run python run_tests.py
```

Or run specific test files:

```bash
poetry run python -m unittest test_flight_search test_integration -v
```

**Without Poetry:**
```bash
python3 run_tests.py
# or
python3 -m unittest test_flight_search test_integration -v
```

The integration tests verify that the application can find at least one matching result with realistic flight data.

## Troubleshooting

**Error: "Amadeus API credentials not set"**
- Make sure you've added your API key and secret to `config.yaml`

**Error: "No matching flights found"**
- Try increasing `max_price`
- Try increasing `arrival_tolerance_hours`
- Try allowing stops by setting `max_stops` to 1 or 2
- Check that your dates are valid and in the future

**API Rate Limit Errors**
- The free tier has 2,000 calls per month
- Each destination search uses multiple API calls
- Consider reducing the number of destinations searched

