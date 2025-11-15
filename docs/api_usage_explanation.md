# API Usage Explanation

## Overview

This application uses **three Amadeus APIs** to find meeting destinations for two people. Here's what each API does and when it's used.

**Authentication**: The application uses pre-authentication to ensure access tokens are obtained before making API calls. This prevents most authentication errors (401) and ensures reliable API access.

**Documentation Verified**: All API parameters and response structures have been verified against the official Amadeus API documentation as of the last update.

## APIs Used

### 1. Flight Offers Search API
**Purpose**: Get actual flight offers (prices, schedules, airlines) for a specific route

**Official Documentation**: 
- [Flight Offers Search API - Amadeus for Developers](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search)
- [Flight APIs Tutorial](https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/resources/flights/)

**When Used**: 
- For every origin-destination pair we want to check
- Called twice per destination: once for Person 1 (TLV → destination) and once for Person 2 (ALC → destination)

**What It Returns**:
- List of available flights with:
  - Prices (in EUR or other currency)
  - Departure and arrival times
  - Flight duration
  - Number of stops
  - Airlines
  - Booking classes

**Example Call**:
```python
amadeus.shopping.flight_offers_search.get(
    originLocationCode="TLV",      # Required: IATA code of origin airport
    destinationLocationCode="PAR",  # Required: IATA code of destination airport
    departureDate="2025-11-20",     # Required: Departure date (YYYY-MM-DD)
    returnDate="2025-11-25",        # Required for round-trip: Return date (YYYY-MM-DD)
    adults=1,                        # Required: Number of adult passengers
    max=250                          # Optional: Maximum number of results (default: 250)
)
```

**Official Documentation**: 
- [Flight Offers Search API Reference](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api-reference)

**Usage Statistics** (from your dashboard):
- **Requests**: 431 (most used API)
- **Errors**: 24
- **Avg Response Time**: 5451ms (slowest, but most important)

**Why So Many Requests?**
- We check multiple destinations (e.g., 32 predefined destinations)
- For each destination, we make 2 calls (Person 1 + Person 2)
- So 32 destinations × 2 people = 64+ API calls minimum
- Plus return flights are included in each call

---

### 2. Flight Inspiration Search API (Flight Destinations)
**Purpose**: Discover destinations dynamically from an origin airport

**Official Documentation**: 
- [Flight Inspiration Search API - Amadeus for Developers](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search)
- [Flight Destinations API Reference](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search/api-reference)

**When Used**: 
- Only when `use_dynamic_destinations: true` in config
- Called once per origin to find available destinations
- Currently **failing in test environment** (404 errors for TLV/ALC)
- May also return 401 errors if authentication fails

**What It Returns**:
- List of destination airport codes reachable from the origin
- Can be filtered by price, duration, or other criteria

**Example Call**:
```python
amadeus.shopping.flight_destinations.get(
    origin="TLV",
    departureDate="2025-11-20,2025-12-20",  # Date range (optional but recommended)
    viewBy="DESTINATION",  # Group by destination
    oneWay=False,  # Round-trip flights
    nonStop=True  # Optional: Only destinations with direct flights (when both max_stops_person1=0 and max_stops_person2=0)
)
```

**Non-Stop Parameter**:
- When both `max_stops_person1: 0` and `max_stops_person2: 0` in config, the application automatically sets `nonStop=True` in the API call
- This filters destinations to only those with direct flights available
- More efficient: avoids searching destinations that only have connecting flights
- Improves search performance when user wants direct flights only

**Authentication**:
- The application uses pre-authentication to ensure access tokens are obtained before API calls
- If you receive 401 errors, check your API credentials in `config.yaml`
- Ensure your API key has permission for the Flight Inspiration Search API endpoint

**Usage Statistics** (from your dashboard):
- **Requests**: 16
- **Errors**: 16 (100% error rate - all 404s)
- **Avg Response Time**: 291ms

**Why All Errors?**
- Test environment doesn't have data for TLV (Tel Aviv) or ALC (Alicante)
- API returns 404: "No response found for this query"
- May also return 401 if authentication fails (missing/invalid credentials)
- Application correctly falls back to predefined destination list

**Error Handling**:
- **401 Errors**: Authentication failures - check API credentials and permissions
- **404 Errors**: No data available for the origin in test environment
- Both errors trigger automatic fallback to predefined destination list

**Current Status**: 
- ❌ Not working in test environment (404 for TLV/ALC)
- ✅ Should work in production environment
- ✅ Fallback to predefined list works correctly
- ✅ Improved authentication and error handling implemented

---

### 3. Airport Nearest Relevant API
**Purpose**: Find nearby airports within a specified radius

**Official Documentation**: 
- [Airport Nearest Relevant API - Amadeus for Developers](https://developers.amadeus.com/self-service/category/airport/api-doc/airport-nearest-relevant)
- [Airport & City Search APIs](https://developers.amadeus.com/self-service/category/airport)

**When Used**: 
- **NOW USED** when `nearby_airports_radius_km > 0` in config
- Called to find alternative airports within a radius of the origin
- Helps find more flight options for major cities like Tel Aviv

**Example Call**:
```python
amadeus.reference_data.locations.airports.get(
    latitude=32.0114,    # Required: Latitude of origin location
    longitude=34.8867,   # Required: Longitude of origin location
    radius=200           # Required: Search radius in kilometers
)
```

**What It Returns**:
- List of airports within the specified radius
- Each airport includes IATA code, name, and distance

**Why We Use It**:
- Major cities like Tel Aviv may have multiple airports serving the area
- Expands search to nearby airports to find more flight options
- Configurable via `nearby_airports_radius_km` parameter (default: 0 = disabled)

---

## How Destinations Are Decided

### Logic Overview

The goal is to find destinations where **both people can meet** with reasonable flight times. We want destinations that are:
- ✅ **Reachable from both origins** (TLV and ALC)
- ✅ **Not too far** (reasonable flight duration for both)
- ✅ **Have available flights** on the specified dates

### Example: Tel Aviv (TLV) and Alicante (ALC)

**Origins:**
- Person 1: **TLV** (Tel Aviv, Israel)
- Person 2: **ALC** (Alicante, Spain)

**Good Destination Examples** (close to both):
- ✅ **PAR** (Paris, France) - ~4-5 hours from TLV, ~2 hours from ALC
- ✅ **LON** (London, UK) - ~5 hours from TLV, ~2.5 hours from ALC
- ✅ **MAD** (Madrid, Spain) - ~5 hours from TLV, ~1 hour from ALC
- ✅ **ROM** (Rome, Italy) - ~3 hours from TLV, ~2 hours from ALC
- ✅ **AMS** (Amsterdam, Netherlands) - ~5 hours from TLV, ~2.5 hours from ALC
- ✅ **BER** (Berlin, Germany) - ~4 hours from TLV, ~2.5 hours from ALC

**Bad Destination Examples** (too far):
- ❌ **BKK** (Bangkok, Thailand) - ~10 hours from TLV, ~14 hours from ALC
- ❌ **NYC** (New York, USA) - ~12 hours from TLV, ~8 hours from ALC
- ❌ **SYD** (Sydney, Australia) - ~20 hours from TLV, ~24 hours from ALC

**Why These Are Bad:**
- Very long flight times (10+ hours)
- Expensive flights
- Not practical for a short meeting trip
- One person would have a much longer journey than the other

### Current Process

1. **Check Configuration**:
   - If `use_dynamic_destinations: true` → Try Flight Inspiration Search API
   - If `use_dynamic_destinations: false` → Use predefined list

2. **Dynamic Discovery** (when enabled):
   - Call Flight Inspiration Search API for TLV → Get list of destinations from Tel Aviv
   - Call Flight Inspiration Search API for ALC → Get list of destinations from Alicante
   - If both `max_stops_person1=0` and `max_stops_person2=0`, automatically sets `nonStop=True` to only get destinations with direct flights
   - Find **common destinations** (destinations reachable from both origins)
   - **Currently fails** → Falls back to predefined list

3. **Predefined List** (fallback or when disabled):
   - Uses a hardcoded list of 32 popular **European destinations**
   - Includes: PAR, LON, MAD, ROM, AMS, BER, VIE, BCN, MUC, FCO, etc.
   - These are destinations likely to have flights from both TLV and ALC
   - **Why European?** Because:
     - TLV is in the Middle East, close to Europe
     - ALC is in Europe
     - European cities are a good "middle ground" - not too far from either origin

4. **Find Common Destinations**:
   ```
   Destinations from TLV: [PAR, LON, MAD, ROM, BKK, NYC, AMS, BER, ...]
   Destinations from ALC: [PAR, LON, MAD, ROM, AMS, BER, BCN, MUC, ...]
   
   Common destinations: [PAR, LON, MAD, ROM, AMS, BER, ...]
   ```
   - Only destinations that appear in **both lists** are considered
   - This ensures both people can reach the destination

5. **Filter by Max Flight Duration** (if configured):
   - **Parameter**: `max_flight_duration_hours` in config.yaml
   - **Current Status**: ✅ **FULLY IMPLEMENTED**
   - Filters flights where both outbound and return durations exceed the limit
   - Duration is parsed from ISO 8601 format (e.g., "PT19H50M" = 19.83 hours)
   - **Example**: If `max_flight_duration_hours: 6`, flights with duration > 6 hours are excluded
   - Applied during flight search, not during destination discovery

6. **Limit Destinations**:
   - Only checks first `max_destinations` (default: 50) destinations
   - This limits API usage and search time

### Step-by-Step Example: TLV + ALC → Finding Meeting Destinations

**Step 1: Get Destinations from Each Origin**
```
From TLV (Tel Aviv):
  → API returns: [PAR, LON, MAD, ROM, AMS, BER, BKK, NYC, IST, ATH, ...]
  
From ALC (Alicante):
  → API returns: [PAR, LON, MAD, ROM, AMS, BER, BCN, MUC, VIE, FCO, ...]
```

**Step 2: Find Common Destinations**
```
Common = Intersection of both lists
Common = [PAR, LON, MAD, ROM, AMS, BER, ...]
```

**Step 3: Filter by Distance/Duration** (if max_flight_duration_hours is set)
```
For each destination in Common:
  - Check flight duration from TLV
  - Check flight duration from ALC
  - If both are ≤ max_flight_duration_hours → Keep
  - If either is > max_flight_duration_hours → Remove

Example with max_flight_duration_hours: 6:
  PAR: TLV→PAR (4.5h) ✅, ALC→PAR (2h) ✅ → Keep
  LON: TLV→LON (5h) ✅, ALC→LON (2.5h) ✅ → Keep
  BKK: TLV→BKK (10h) ❌ → Remove (too far)
  NYC: TLV→NYC (12h) ❌ → Remove (too far)
```

**Step 4: Search Flights for Remaining Destinations**
```
For each destination in filtered list:
  - Search flights: TLV → destination
  - Search flights: ALC → destination
  - Find matching pairs (arrivals within tolerance)
  - Check prices, times, etc.
```

### Why We Prefer Closer Destinations

1. **Practicality**: Shorter flights are more convenient
2. **Cost**: Shorter flights are usually cheaper
3. **Time**: Less travel time = more meeting time
4. **Fairness**: Both people have similar travel times
5. **Flexibility**: More flight options for shorter routes

### Current Limitations

✅ **Max Flight Duration Filtering**: Now fully implemented
- Flights exceeding `max_flight_duration_hours` are filtered out
- Both outbound and return flight durations are checked
- Applied during flight search phase

---

## Max Flight Duration Parameter

### Current Status

**Parameter Exists**: ✅ Yes
- Config: `max_flight_duration_hours: 0` (0 = no limit)
- Example: `max_flight_duration_hours: 6` (only flights within 6 hours)

**Implementation Status**: ✅ **FULLY IMPLEMENTED**
- Parameter is passed through all functions
- **Actively filters flights** by duration during search
- Both outbound and return flight durations are checked
- Flights exceeding the limit are excluded from results

### How It Works

1. **Get list of destinations** (from API or predefined list)
2. **For each destination**, search flights using Flight Offers Search API
3. **Parse flight duration** from ISO 8601 format (e.g., "PT19H50M")
4. **Filter flights** where either outbound or return duration > `max_flight_duration_hours`
5. **Only include flights** that meet the duration requirement

### Duration Parsing

- ISO 8601 format: `PT19H50M` = 19 hours, 50 minutes = 19.83 hours
- Both outbound and return durations must be ≤ `max_flight_duration_hours`
- If either leg exceeds the limit, the entire flight is filtered out

---

## Recommendations

### To Reduce API Usage

1. **Use Predefined List**: Set `use_dynamic_destinations: false`
   - Avoids 16 failed API calls
   - Uses curated list of likely destinations

2. **Limit Destinations**: Reduce `max_destinations` in code
   - Currently defaults to 50
   - Could reduce to 10-20 most likely destinations

3. **Implement Duration Filtering**:
   - Add quick duration check before full flight search
   - Filter out destinations that are too far
   - Reduces unnecessary Flight Offers Search calls

### To Fix Flight Inspiration Search

1. **Switch to Production**: 
   - Test environment doesn't have TLV/ALC data
   - Production should have complete data
   - Update config: `environment: "production"`

2. **Use Predefined List**:
   - More reliable in test environment
   - Faster (no API calls needed)
   - Curated list of good destinations

---

## Summary

| API | Purpose | Status | Usage | Documentation |
|-----|---------|--------|-------|---------------|
| **Flight Offers Search** | Get actual flights | ✅ Working | 431 requests (main API) | [Official Docs](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search) |
| **Flight Inspiration Search** | Find destinations | ⚠️ Limited (test env) | 16 requests, 404/401 errors | [Official Docs](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search) |
| **nonStop Parameter** | Filter direct flights | ✅ Implemented | Used when both max_stops_person1=0 and max_stops_person2=0 | Automatically set based on config |
| **Airport Nearest Relevant** | Find nearby airports | ✅ Used when radius > 0 | Used for nearby airport search | [Official Docs](https://developers.amadeus.com/self-service/category/airport/api-doc/airport-nearest-relevant) |

**Destination Selection**: Currently uses predefined list (32 destinations) due to Flight Inspiration Search API limitations in test environment (404 for TLV/ALC). Falls back automatically on errors.

**Authentication**: Pre-authentication implemented to prevent 401 errors. Enhanced error handling provides clear guidance for authentication issues.

**Max Flight Duration**: ✅ Fully implemented - filters flights by duration during search phase.

**Error Handling**: 
- 401 errors: Authentication failures - check credentials and permissions
- 404 errors: No data available - automatic fallback to predefined list
- Both errors are handled gracefully with detailed logging

## Additional Resources

- **Amadeus for Developers Portal**: [developers.amadeus.com](https://developers.amadeus.com/)
- **Self-Service APIs Documentation**: [Self-Service APIs](https://developers.amadeus.com/self-service)
- **Flight APIs Guide**: [Flight APIs Tutorial](https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/resources/flights/)
- **API Reference**: [API Reference](https://developers.amadeus.com/self-service/apis-docs)
- **Python SDK**: [Amadeus Python SDK](https://github.com/amadeus4dev/amadeus-python)

