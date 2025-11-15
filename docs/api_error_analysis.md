# API Error Analysis: Flight Destinations API Errors (404 and 401)

## Issue Summary

When calling the Amadeus Flight Destinations API, you may encounter two types of errors:
1. **404 Error**: No data available for the requested origin (common in test environment)
2. **401 Error**: Authentication failure - missing or invalid Authorization header

## Error Types

### 1. 404 Error: No Data Available

#### Input
- **Endpoint**: `shopping.flight_destinations.get`
- **Origin**: `TLV` (Tel Aviv)
- **Environment**: Test (`test.api.amadeus.com`)
- **Full URL**: `https://test.api.amadeus.com/v1/shopping/flight-destinations?origin=TLV`

#### Output (Error Response)

**Status Code**: `404`

**Error Details**:
```json
{
  "errors": [{
    "status": 404,
    "code": 1797,
    "title": "NOT FOUND",
    "detail": "No response found for this query"
  }]
}
```

### 2. 401 Error: Authentication Failure

#### Input
- **Endpoint**: `shopping.flight_destinations.get`
- **Origin**: Any origin
- **Environment**: Test or Production
- **Cause**: Missing or invalid API credentials

#### Output (Error Response)

**Status Code**: `401`

**Error Details**:
```json
{
  "errors": [{
    "code": 38191,
    "title": "Invalid HTTP header",
    "detail": "Missing or invalid format for mandatory Authorization header",
    "status": 401
  }]
}
```

**Response Headers**:
```
Date: Sat, 15 Nov 2025 00:01:24 GMT
Content-Type: application/vnd.amadeus+json
Content-Length: 103
Connection: close
Ama-Request-Id: 0001XG41B5QQQB
Ama-Gateway-Request-Id: rrt-04b5a71285808aec6-b-de-2403711-96163777-1
Server: Amadeus
```

## Root Causes

### 404 Error Root Cause

The test environment (`test.api.amadeus.com`) does not have test data available for all origins. Specifically:
- **TLV (Tel Aviv)** - No test data available
- **ALC (Alicante)** - No test data available

This is a known limitation of the Amadeus test environment. The test environment has limited coverage and may not include data for all airport codes.

### 401 Error Root Cause

Authentication failures occur when:
1. **Invalid API Credentials**: The API key or secret in `config.yaml` is incorrect or expired
2. **Missing Permissions**: The API key doesn't have permission to access the Flight Inspiration Search API
3. **Token Expiration**: The authentication token expired and wasn't refreshed (rare with SDK)
4. **Environment Mismatch**: Using test credentials with production environment or vice versa

**Note**: The application now includes pre-authentication to ensure tokens are obtained before API calls, which should prevent most 401 errors.

## Solutions

### For 404 Errors

The application correctly handles 404 errors by:
1. Catching the `ResponseError` exception
2. Logging the error with full details (ERROR level)
3. Falling back to a predefined list of popular destinations
4. Continuing with the flight search using the predefined destinations

### For 401 Errors

The application now includes improved authentication handling:

1. **Pre-Authentication**: 
   - The `FlightSearch` class now pre-authenticates on initialization
   - Makes a test API call to ensure access token is obtained and cached
   - This prevents most 401 errors from occurring

2. **Credential Verification**:
   - Verifies API credentials are set before making API calls
   - Validates credentials exist in the configuration

3. **Enhanced Error Messages**:
   - Provides clear guidance when 401 errors occur
   - Explains possible causes and solutions
   - Directs users to verify credentials and check API permissions

4. **Automatic Fallback**:
   - Falls back to predefined destination list if API call fails
   - Application continues to work even if dynamic discovery fails

### How to Fix 401 Errors

If you encounter 401 errors:

1. **Verify API Credentials**:
   ```yaml
   api:
     amadeus_api_key: "YOUR_API_KEY_HERE"
     amadeus_api_secret: "YOUR_API_SECRET_HERE"
   ```

2. **Check API Key Permissions**:
   - Log in to [Amadeus Developer Portal](https://developers.amadeus.com/self-service)
   - Verify your API key has access to "Flight Inspiration Search" API
   - Ensure the API key is not expired or revoked

3. **Verify Environment**:
   - Ensure you're using test credentials with `environment: "test"`
   - Or production credentials with `environment: "production"`
   - Don't mix test and production credentials

4. **Get New Credentials**:
   - If credentials are invalid, get new ones from [Amadeus Self-Service](https://developers.amadeus.com/self-service)

## Debug Logging

All API calls and errors are now logged with full details to:
- **Console**: INFO level and above (user-friendly messages)
- **Debug Log File**: `debug_logs/flight_search_YYYYMMDD_HHMMSS.log` (DEBUG level with full details)

### What's Logged

For each API call:
- Endpoint name
- Parameters (origin, destination, dates, etc.)
- Hostname/environment
- Response type and data structure
- Full error details (status code, URL, headers, body)
- Parsed error information

## Recommendations

### For 404 Errors

1. **For Development/Testing**: 
   - Use the predefined destination list (already implemented as fallback)
   - Or use origins that have test data available (check Amadeus documentation)
   - Set `use_dynamic_destinations: false` in config to skip API calls

2. **For Production**:
   - Switch to production environment (`api.amadeus.com`)
   - Production environment should have data for all origins
   - Update `config.yaml`: `environment: "production"`

3. **Alternative Approach**:
   - Use the Flight Offers Search API directly with a predefined list of destinations
   - This avoids the Flight Destinations API limitation in test environment

### For 401 Errors

1. **Verify Credentials**:
   - Double-check API key and secret in `config.yaml`
   - Ensure no extra spaces or quotes around credentials
   - Verify credentials are for the correct environment (test vs production)

2. **Check API Permissions**:
   - Log in to Amadeus Developer Portal
   - Verify API key has access to Flight Inspiration Search API
   - Check if API key is active and not expired

3. **Test Authentication**:
   - The application now pre-authenticates on startup
   - Check debug logs to see if authentication succeeds
   - Look for "Pre-authentication successful" in logs

4. **Use Predefined List**:
   - If authentication continues to fail, set `use_dynamic_destinations: false`
   - This bypasses the Flight Inspiration Search API entirely
   - Application will use the predefined destination list

## Error Code Reference

- **Error Code 1797**: "NOT FOUND - No response found for this query"
  - Status: 404
  - Indicates the requested data is not available in the test environment
  - Common for origins/destinations not included in test data
  - **Solution**: Use predefined destination list or switch to production environment

- **Error Code 38191**: "Invalid HTTP header - Missing or invalid format for mandatory Authorization header"
  - Status: 401
  - Indicates authentication failure
  - **Possible Causes**:
    - Invalid or expired API credentials
    - Missing API key or secret in configuration
    - API key doesn't have permission for this endpoint
    - Token not obtained before API call (should be rare with pre-authentication)
  - **Solution**: Verify API credentials, check permissions, ensure environment matches credentials

## Verification

To verify this is working correctly, check the debug log file:
```bash
cat debug_logs/flight_search_*.log | grep -A 10 "API Call Details"
```

The logs will show:
- Exact API call being made
- Full error response
- Fallback to predefined destinations
- Successful continuation of the search

