# API Usage Explanation

## Overview

This application uses **three Amadeus APIs** to find meeting destinations for two people. Here's what each API does and when it's used.

## APIs Used

### 1. Flight Offers Search API
**Purpose**: Get actual flight offers (prices, schedules, airlines) for a specific route

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
    originLocationCode="TLV",
    destinationLocationCode="PAR",
    departureDate="2025-11-20",
    returnDate="2025-11-25",
    adults=1,
    max=250
)
```

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

**When Used**: 
- Only when `use_dynamic_destinations: true` in config
- Called once per origin to find available destinations
- Currently **failing in test environment** (404 errors)

**What It Returns**:
- List of destination airport codes reachable from the origin
- Can be filtered by price, duration, or other criteria

**Example Call**:
```python
amadeus.shopping.flight_destinations.get(
    origin="TLV"
)
```

**Usage Statistics** (from your dashboard):
- **Requests**: 16
- **Errors**: 16 (100% error rate - all 404s)
- **Avg Response Time**: 291ms

**Why All Errors?**
- Test environment doesn't have data for TLV (Tel Aviv) or ALC (Alicante)
- API returns 404: "No response found for this query"
- Application correctly falls back to predefined destination list

**Current Status**: 
- ❌ Not working in test environment
- ✅ Should work in production environment
- ✅ Fallback to predefined list works correctly

---

### 3. Airport Nearest Relevant API
**Purpose**: Find nearby airports (not currently used in this application)

**When Used**: 
- **NOT USED** in the current implementation
- May have been called during testing or exploration

**Usage Statistics** (from your dashboard):
- **Requests**: 1
- **Errors**: 1
- **Avg Response Time**: 75ms

**Why Not Used?**
- Our application uses specific origin airports (TLV and ALC)
- We don't need to find alternative nearby airports
- This API would be useful if we wanted to expand search to nearby airports

---

## How Destinations Are Decided

### Current Process

1. **Check Configuration**:
   - If `use_dynamic_destinations: true` → Try Flight Inspiration Search API
   - If `use_dynamic_destinations: false` → Use predefined list

2. **Dynamic Discovery** (when enabled):
   - Call Flight Inspiration Search API for TLV
   - Call Flight Inspiration Search API for ALC
   - Find common destinations (destinations reachable from both origins)
   - **Currently fails** → Falls back to predefined list

3. **Predefined List** (fallback or when disabled):
   - Uses a hardcoded list of 32 popular European destinations
   - Includes: PAR, LON, MAD, ROM, AMS, BER, VIE, etc.
   - These are destinations likely to have flights from both TLV and ALC

4. **Filter by Max Flight Duration** (if configured):
   - **Parameter**: `max_flight_duration_hours` in config.yaml
   - **Current Status**: ⚠️ **Parameter exists but NOT fully implemented**
   - The parameter is passed through the code but not actively filtering destinations
   - **Needs Implementation**: Should filter destinations based on actual flight duration

5. **Limit Destinations**:
   - Only checks first `max_destinations` (default: 50) destinations
   - This limits API usage and search time

---

## Max Flight Duration Parameter

### Current Status

**Parameter Exists**: ✅ Yes
- Config: `max_flight_duration_hours: 0` (0 = no limit)
- Example: `max_flight_duration_hours: 5` (only destinations within 5 hours)

**Implementation Status**: ⚠️ **Partially Implemented**
- Parameter is passed through all functions
- But **not actively filtering** destinations by flight duration
- The Flight Inspiration Search API doesn't support duration filtering directly
- We would need to:
  1. Get destinations from API
  2. For each destination, check flight duration using Flight Offers Search
  3. Filter out destinations with flights longer than max duration

### How It Should Work

1. **Get list of destinations** (from API or predefined list)
2. **For each destination**:
   - Make a test Flight Offers Search call
   - Check the flight duration
   - If duration > `max_flight_duration_hours`, skip this destination
3. **Only search destinations** that meet the duration requirement

### Current Workaround

Since duration filtering isn't fully implemented, you can:
- Use predefined destinations that are known to be close (e.g., European cities)
- Manually review results and filter by duration in the output
- Set `use_dynamic_destinations: false` to use the curated predefined list

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

| API | Purpose | Status | Usage |
|-----|---------|--------|-------|
| **Flight Offers Search** | Get actual flights | ✅ Working | 431 requests (main API) |
| **Flight Inspiration Search** | Find destinations | ❌ Failing (test env) | 16 requests, all errors |
| **Airport Nearest Relevant** | Find nearby airports | ⚠️ Not used | 1 request (testing) |

**Destination Selection**: Currently uses predefined list (32 destinations) due to Flight Inspiration Search API failures in test environment.

**Max Flight Duration**: Parameter exists but needs implementation to actually filter destinations by flight duration.

