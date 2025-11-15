# Alternative APIs for Finding Destination Airports

## Current Issue
The Airport Routes API (`/v1/airport/direct-destinations`) is returning only 8 destinations for Alicante (ALC), but there should be many more direct destinations available.

## Current APIs in Use

### 1. Flight Inspiration Search API (Primary)
- **Endpoint**: `shopping.flight_destinations.get()`
- **Status**: Currently used as the primary method
- **Limitation**: Returns cached/trending destinations, may not include all airports
- **Parameters**: `origin`, `departureDate`, `viewBy='DESTINATION'`, `oneWay`, `nonStop`
- **Reference**: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search

### 2. Airport Routes API (Fallback)
- **Endpoint**: `airport.direct_destinations.get()`
- **Status**: Currently used as fallback when Inspiration Search fails
- **Limitation**: Only returns 8 destinations for ALC (incomplete results)
- **Parameters**: Only `departureAirportCode` (no pagination, no max limit parameter)
- **Reference**: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-routes

## Potential Solutions

### Option 1: Enhanced Flight Inspiration Search API Usage
The Flight Inspiration Search API might return more destinations if used with different parameters:
- Try different `viewBy` options (DATE, DURATION, WEEK, COUNTRY)
- Use wider date ranges
- Try without `nonStop` filter to get destinations with connections
- Check if there's a `max` parameter to increase results

**Investigation Needed**: Check if Flight Inspiration Search API has pagination or max results parameter.

### Option 2: Flight Offers Search API (Brute Force Approach)
- **Endpoint**: `shopping.flight_offers_search.get()`
- **Approach**: Use a predefined list of common destinations and check which ones have flights
- **Pros**: Returns real-time data, comprehensive
- **Cons**: Requires many API calls (one per destination), slower, uses more API quota
- **Reference**: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search

**How it would work**:
1. Use a comprehensive list of European/international airports
2. For each destination, call Flight Offers Search API with origin and destination
3. If flights are found, add destination to list
4. This would find ALL destinations with available flights (not just direct)

### Option 3: Reference Data APIs
- **Airport Search**: `reference_data.locations.airports.get()`
- **Approach**: Get all airports in a region/country, then filter by checking flight availability
- **Limitation**: Still requires Flight Offers Search to verify availability

### Option 4: Airport Predictions API
- **Endpoint**: `airport.predictions.on_time` (found in SDK)
- **Status**: ❌ Not suitable - provides on-time performance predictions, not destination lists
- **Purpose**: Predicts flight delays/on-time performance for specific flights

### Option 5: Schedule API
- **Endpoint**: `schedule.flights.get()` (found in SDK)
- **Status**: ❌ Not suitable - requires carrier code and flight number
- **Purpose**: Retrieves flight status for a specific flight (carrier + flight number + date)
- **Limitation**: Cannot be used to discover destinations - requires knowing the flight details first

## Recommended Investigation Steps

1. **Check Airport Routes API Response**:
   - ✅ Verified: API only accepts `departureAirportCode` parameter (no pagination, no max limit)
   - ⚠️ **Action Needed**: Check actual API response for pagination links or metadata
   - ⚠️ **Action Needed**: Test with different airports to see if 8-result limit is consistent
   - ⚠️ **Action Needed**: Review API response structure for any pagination indicators

2. **Test Flight Inspiration Search API Variations**:
   - ⚠️ **Action Needed**: Try without `nonStop` parameter to get destinations with connections
   - ⚠️ **Action Needed**: Try different `viewBy` values (DATE, DURATION, WEEK, COUNTRY)
   - ⚠️ **Action Needed**: Try wider date ranges (currently using 60 days)
   - ⚠️ **Action Needed**: Check response for pagination links or `meta` field with result counts
   - ⚠️ **Action Needed**: Check if removing `nonStop=True` when `max_stops > 0` returns more destinations

3. **Investigate Airport Predictions API**:
   - ✅ Checked: `airport.predictions.on_time` - provides on-time predictions, not destination lists
   - ❌ Not suitable for finding destinations

4. **Consider Hybrid Approach**:
   - Use Airport Routes API for direct destinations (even if limited to 8)
   - Use Flight Inspiration Search API **without `nonStop` filter** for additional destinations (including those with connections)
   - Combine and deduplicate results from both APIs
   - Use predefined list as final fallback

5. **Most Promising Solution**:
   - **Current Issue**: When `max_stops > 0`, the code still uses `nonStop=True` in Flight Inspiration Search API
   - **Fix**: Remove `nonStop=True` parameter when `max_stops > 0` to get destinations with connections
   - **Expected Result**: This should return destinations that are reachable with connections, not just direct flights
   - **For Alicante**: This might return many more destinations than the 8 direct ones from Airport Routes API
   - **Note**: Airport Routes API always returns only direct destinations (no connections), so it will always be limited

## Notes

- The Airport Routes API documentation shows it only accepts `departureAirportCode` parameter
- No pagination or max limit parameters are documented
- The API might have an internal limit or might only return a subset of routes
- Flight Inspiration Search API uses cached data and may not include all destinations
- Flight Offers Search API provides real-time data but requires destination to be specified

## References

- [Amadeus Airport Routes API](https://developers.amadeus.com/self-service/category/flights/api-doc/airport-routes)
- [Amadeus Flight Inspiration Search API](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search)
- [Amadeus Flight Offers Search API](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search)

