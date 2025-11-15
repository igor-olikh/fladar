# Flight Search Application - Project Explanation

## What is This Project?

This is a **Python application that helps two people find a meeting destination** by searching for flights from their respective home cities. The application:

1. **Takes two origin cities** (e.g., Tel Aviv and Alicante)
2. **Finds a common destination** where both people can meet
3. **Searches for flights** from both origins to that destination
4. **Matches flights** that arrive within a specified time window (e.g., ±3 hours)
5. **Filters results** by price, departure times, number of stops, etc.
6. **Outputs results** in console and/or CSV format with local times for each city

### The Problem It Solves

When two people want to meet somewhere, they need to:
- Find a destination that both can reach
- Find flights that arrive around the same time
- Stay within budget constraints
- Meet time preferences (e.g., no early morning flights)

This application automates this entire process by searching through multiple destinations and finding the best matching flight pairs.

---

## How It Works: The Logic

### Step 1: Destination Discovery

The application needs to find potential meeting destinations. There are two approaches:

#### Option A: Dynamic Discovery (API-based)
- Uses Amadeus Flight Inspiration Search API to discover destinations dynamically
- Searches for destinations reachable from each origin city
- Finds **common destinations** (destinations reachable from both origins)
- **Example**:
  ```
  From Tel Aviv (TLV): [Paris, London, Madrid, Rome, Amsterdam, ...]
  From Alicante (ALC): [Paris, London, Madrid, Rome, Barcelona, ...]
  
  Common destinations: [Paris, London, Madrid, Rome, ...]
  ```

#### Option B: Predefined List (Fallback)
- Uses a curated list of 32 popular European destinations
- More reliable when API doesn't have data for certain origins
- Faster (no API calls needed)
- **Why European?** Because:
  - Tel Aviv is close to Europe
  - Alicante is in Europe
  - European cities are a good "middle ground" - not too far from either origin

### Step 2: Flight Search

For each potential destination, the application:

1. **Searches flights for Person 1** (e.g., TLV → Destination)
   - Gets all available flights on the specified dates
   - Filters by: max stops, departure time constraints, price

2. **Searches flights for Person 2** (e.g., ALC → Destination)
   - Same filtering criteria

3. **Finds matching pairs**:
   - Outbound flights that arrive within the tolerance window (e.g., ±3 hours)
   - Return flights that meet the same criteria
   - Both flights must be on the same day

### Step 3: Filtering and Matching

The application applies multiple filters:

#### Price Filtering
- Checks if each person's flight price is within `max_price`
- Calculates total price (Person 1 + Person 2)
- Only includes flights where both people's prices are acceptable

#### Time Filtering
- **Departure Time Constraints**:
  - `min_departure_time_outbound`: Don't fly earlier than this time (outbound)
  - `min_departure_time_return`: Don't fly earlier than this time (return)
  - Applies to both Person 1 and Person 2

#### Arrival Time Matching
- **Arrival Tolerance**: Flights must arrive within ±X hours of each other
- Example: If Person 1 arrives at 14:00, Person 2 must arrive between 11:00-17:00 (if tolerance is 3 hours)

#### Stops Filtering
- Can filter for direct flights only (`max_stops: 0`)
- Or allow connections (`max_stops: 1, 2, etc.`)

### Step 4: Output Formatting

Results are formatted with:

1. **Console Output**: Human-readable format showing:
   - Destination
   - Total price and individual prices
   - Flight details (departure, arrival, duration, airlines)
   - For both outbound and return flights

2. **CSV Output**: Structured data with:
   - Route information (From → To)
   - Prices (total and per person)
   - **UTC times** for all flights
   - **Local times** for each city:
     - Person 1 departure/arrival in Tel Aviv local time
     - Person 2 departure/arrival in Alicante local time
     - Destination arrival/departure in destination local time
   - Flight durations, airlines, etc.

---

## Example Scenario

### Input
- **Person 1 Origin**: Tel Aviv (TLV)
- **Person 2 Origin**: Alicante (ALC)
- **Outbound Date**: 2025-11-20
- **Return Date**: 2025-11-25
- **Max Price**: 400 EUR per person
- **Max Stops**: 0 (direct flights only)
- **Arrival Tolerance**: 6 hours
- **Min Departure Time**: 14:00 (both outbound and return)

### Process

1. **Find Destinations**:
   - Discovers: Paris, London, Madrid, Rome, Amsterdam, etc.
   - Or uses predefined list: 32 European cities

2. **For Each Destination** (e.g., Paris):
   - Search: TLV → PAR (Person 1)
   - Search: ALC → PAR (Person 2)
   - Find flights arriving within 6 hours of each other
   - Check prices are ≤ 400 EUR each
   - Check departure times are ≥ 14:00
   - Check return flights meet same criteria

3. **Example Match Found**:
   ```
   Destination: Paris (PAR)
   
   Person 1 (TLV → PAR):
   - Outbound: Departs 16:35 (TLV local), Arrives 00:45 (Paris local)
   - Return: Departs 07:05 (Paris local), Arrives 15:35 (TLV local)
   - Price: 284.92 EUR
   
   Person 2 (ALC → PAR):
   - Outbound: Departs 21:00 (ALC local), Arrives 23:15 (Paris local)
   - Return: Departs 07:45 (Paris local), Arrives 09:50 (ALC local)
   - Price: 187.86 EUR
   
   Total: 472.78 EUR
   Arrival Difference: ~23 hours (Person 1 arrives Nov 21, Person 2 arrives Nov 20)
   ```

4. **Output**:
   - Console: Formatted display of all matching flights
   - CSV: Structured data with all details including local times

---

## Why This Logic?

### Why Find Common Destinations?

- **Efficiency**: Only search destinations both people can reach
- **Practicality**: Avoids searching destinations only one person can access
- **Fairness**: Ensures both people have similar travel times

### Why Filter by Arrival Time?

- **Meeting Coordination**: People need to arrive around the same time
- **Hotel Check-in**: Usually need to check in together
- **Practical Planning**: Easier to coordinate if arrivals are close

### Why Filter by Price?

- **Budget Constraints**: Each person has a maximum budget
- **Fair Comparison**: Compare total cost of meeting at different destinations
- **Cost Efficiency**: Find the most affordable meeting point

### Why Filter by Departure Time?

- **Personal Preferences**: Some people don't want early morning flights
- **Practicality**: Easier to get to airport at certain times
- **Flexibility**: Can set different times for outbound vs return

### Why Use Local Times?

- **User-Friendly**: People think in their local timezone
- **Planning**: Easier to plan when you see times in your timezone
- **Coordination**: Each person can see times in their own timezone

---

## How to Use It

### Prerequisites

1. **Python 3.11+** installed
2. **Poetry** for dependency management
3. **Amadeus API credentials** (free at https://developers.amadeus.com/self-service)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fladar
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Configure the application**:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your settings
   ```

### Configuration

Edit `config.yaml`:

```yaml
# Origin cities (always the same)
origins:
  person1: "TLV"  # Tel Aviv
  person2: "ALC"  # Alicante

# Search parameters
search:
  outbound_date: "2025-11-20"  # When to fly out
  return_date: "2025-11-25"    # When to return
  max_price: 400               # Maximum price per person (EUR)
  max_stops: 0                 # 0 = direct flights only
  arrival_tolerance_hours: 6   # How close arrivals should be
  min_departure_time_outbound: "14:00"  # Don't fly earlier than this
  min_departure_time_return: "14:00"    # Don't fly earlier than this
  use_dynamic_destinations: true  # Use API or predefined list

# API Configuration
api:
  amadeus_api_key: "YOUR_API_KEY"
  amadeus_api_secret: "YOUR_API_SECRET"
  environment: "test"  # or "production" or "live"

# Output settings
output:
  format: "console,csv"  # or "console" or "csv"
  csv_file: "flight_results.csv"
```

### Running the Application

```bash
poetry run python main.py
```

### Output

1. **Console Output**: Shows matching flights in a readable format
2. **CSV File**: Detailed data with all flight information and local times

---

## Key Features

### 1. Intelligent Destination Discovery
- Automatically finds destinations reachable from both origins
- Falls back to predefined list if API doesn't have data
- Filters out destinations that are too far (if configured)

### 2. Smart Flight Matching
- Matches flights by arrival time tolerance
- Ensures both people can meet at the destination
- Handles timezone differences automatically

### 3. Comprehensive Filtering
- Price constraints per person
- Departure time preferences
- Number of stops (direct vs connections)
- Flight duration limits (if configured)

### 4. Local Time Display
- Shows times in each person's local timezone
- Shows destination times in destination timezone
- Makes planning easier for each person

### 5. Flexible Output
- Console output for quick viewing
- CSV output for detailed analysis
- Can export to spreadsheet for comparison

### 6. Error Handling
- Graceful fallback if API fails
- Detailed error messages
- Continues searching even if some destinations fail

---

## Technical Architecture

### Components

1. **FlightSearch** (`flight_search.py`):
   - Handles Amadeus API communication
   - Searches for flights
   - Applies filters (price, time, stops)
   - Manages authentication

2. **DestinationFinder** (`destination_finder.py`):
   - Discovers potential destinations
   - Finds common destinations from both origins
   - Orchestrates the search process

3. **OutputFormatter** (`output_formatter.py`):
   - Formats results for console display
   - Exports to CSV with local times
   - Handles timezone conversions

4. **Main** (`main.py`):
   - Loads configuration
   - Initializes components
   - Runs the search
   - Handles logging

### APIs Used

1. **Flight Offers Search API**: Gets actual flight offers with prices
2. **Flight Inspiration Search API**: Discovers destinations dynamically
3. **Timezone Data**: Converts UTC times to local times

---

## Example Use Cases

### Use Case 1: Weekend Meeting
- **Scenario**: Two friends want to meet for a weekend
- **Configuration**: 
  - Short date range (2-3 days)
  - Moderate price limit
  - Prefer direct flights
- **Result**: Finds nearby destinations with convenient flights

### Use Case 2: Business Meeting
- **Scenario**: Two business partners need to meet
- **Configuration**:
  - Specific dates
  - Higher price limit
  - No early morning flights
  - Direct flights preferred
- **Result**: Finds professional meeting locations with convenient schedules

### Use Case 3: Budget Travel
- **Scenario**: Two people want to meet on a budget
- **Configuration**:
  - Low price limit
  - Flexible dates
  - Allow connections (cheaper)
- **Result**: Finds most affordable meeting destinations

---

## Limitations and Future Improvements

### Current Limitations

1. **Max Flight Duration Filtering**: Parameter exists but not fully implemented
2. **Limited Destination Data**: Test environment has limited data for some origins
3. **No Multi-City Support**: Only handles two origins and one destination
4. **No Date Flexibility**: Requires specific dates (no "flexible dates" search)

### Potential Improvements

1. **Implement Duration Filtering**: Filter destinations by actual flight duration
2. **Add Date Flexibility**: Search across date ranges
3. **Multi-City Support**: Handle more than two people
4. **Price Alerts**: Notify when prices drop
5. **Destination Recommendations**: Suggest destinations based on preferences
6. **Visual Output**: Generate maps or charts of results

---

## Troubleshooting

### Common Issues

1. **401 Authentication Error**:
   - Check API credentials in `config.yaml`
   - Verify API key has correct permissions
   - Ensure environment matches credentials (test vs production)

2. **404 No Data Found**:
   - Test environment has limited data
   - Try using predefined destinations (`use_dynamic_destinations: false`)
   - Switch to production environment

3. **No Results Found**:
   - Check if dates are in the future
   - Relax price constraints
   - Increase arrival tolerance
   - Allow connections (increase `max_stops`)

4. **Timezone Issues**:
   - Verify timezone configuration in `config.yaml`
   - Check that airport codes are correct

---

## Summary

This application solves the practical problem of finding a meeting destination for two people by:

1. **Discovering** potential destinations both can reach
2. **Searching** for flights from both origins
3. **Matching** flights that arrive around the same time
4. **Filtering** by price, time preferences, and other constraints
5. **Presenting** results in a clear, actionable format

The logic is designed to be:
- **Efficient**: Only searches relevant destinations
- **Practical**: Considers real-world constraints (price, time, stops)
- **User-Friendly**: Shows times in local timezones
- **Flexible**: Configurable for different use cases
- **Robust**: Handles errors gracefully with fallbacks

This makes it easy for two people to find the best place to meet, with flights that work for both of them.

