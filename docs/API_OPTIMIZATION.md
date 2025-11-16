# Flight Offers Search API Optimization Strategy

## Current Problem
The Flight Offers Search API (`shopping/flight-offers`) is very expensive and called many times:
- For each destination: 2 calls (Person 1 + Person 2)
- For 50 destinations: 100+ API calls
- Each call costs money and takes ~5 seconds

## Optimization Strategies

### 1. Pre-Validation Using Cheaper APIs (RECOMMENDED)
**Before** calling expensive Flight Offers Search, use cheaper APIs to validate routes exist:

- **Airport Routes API** (`airport.direct_destinations`) - FREE/Cheaper
  - Check if destination is in the list of direct destinations from origin
  - Only validates direct routes (not connections)
  - Very fast and cheap

- **Flight Inspiration Search API** (`shopping.flight_destinations`) - FREE/Cheaper
  - Already used for destination discovery
  - Can validate if destination appears in results
  - Uses cached data (may miss some routes)

**Implementation**: Add `pre_validate_routes` config option (default: true)
- If enabled, check Airport Routes API first
- Only call Flight Offers Search if route exists in cheaper API
- Can save 50-80% of API calls for routes that don't exist

### 2. Early Exit Strategy
**If one person has no flights, skip searching for the other person:**
- Search Person 1 first
- If Person 1 has 0 flights → skip Person 2 search
- Can save 50% of calls when routes don't exist

### 3. Reduce Max Results Parameter
**Currently requesting 250 results, but we only need top matches:**
- Change `max: 250` to `max: 10` or `max: 20`
- Faster API responses
- Lower cost per call
- We only need top 3 flights per destination anyway

### 4. Smart Destination Filtering
**Use destination discovery results more effectively:**
- Only check destinations that appear in BOTH origins' destination lists
- Skip destinations that don't appear in either list
- Already partially implemented, but can be improved

### 5. Batch Validation
**Validate multiple destinations at once:**
- Use Airport Routes API once per origin (returns all destinations)
- Check if destination is in the list before Flight Offers Search
- One cheap API call can validate 50+ destinations

## Recommended Implementation Order

1. **Add pre-validation using Airport Routes API** (Biggest impact)
2. **Reduce max results to 10-20** (Quick win)
3. **Add early exit if Person 1 has no flights** (Medium impact)
4. **Improve destination filtering** (Small impact)

## Expected Savings

- **Pre-validation**: 50-80% reduction (skip routes that don't exist)
- **Reduce max results**: 20-30% faster responses, lower cost
- **Early exit**: 50% reduction when routes don't exist
- **Combined**: 60-85% reduction in expensive API calls

## Configuration Options

```yaml
search:
  # Pre-validate routes using cheaper APIs before Flight Offers Search
  # If enabled, checks Airport Routes API first to see if route exists
  # Can save 50-80% of expensive Flight Offers Search API calls
  pre_validate_routes: true  # Default: true
  
  # Maximum results to request from Flight Offers Search API
  # Lower values = faster responses and lower cost
  # We only need top 3 flights per destination anyway
  max_flight_results: 20  # Default: 20 (was 250)
  
  # Early exit: if Person 1 has no flights, skip Person 2 search
  # Can save 50% of calls when routes don't exist
  early_exit_on_no_flights: true  # Default: true
```

