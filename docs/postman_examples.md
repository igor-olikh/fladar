# Postman Examples for Amadeus API Testing

This document provides examples for testing Amadeus API calls using Postman or cURL.

## Prerequisites

1. **Get Amadeus API Credentials**:
   - Sign up at [Amadeus for Developers](https://developers.amadeus.com/)
   - Get your `API Key` and `API Secret`
   - Create an app in the developer portal

2. **Get Access Token**:
   - First, you need to obtain an OAuth 2.0 access token
   - Use the token in the `Authorization` header

---

## 1. Get Access Token (OAuth 2.0)

### cURL Example

```bash
curl -X POST "https://api.amadeus.com/v1/security/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_API_KEY&client_secret=YOUR_API_SECRET"
```

### Postman Setup

1. **Method**: `POST`
2. **URL**: `https://api.amadeus.com/v1/security/oauth2/token`
3. **Headers**:
   - `Content-Type: application/x-www-form-urlencoded`
4. **Body** (x-www-form-urlencoded):
   - `grant_type`: `client_credentials`
   - `client_id`: `YOUR_API_KEY`
   - `client_secret`: `YOUR_API_SECRET`

### Response Example

```json
{
  "type": "amadeusOAuth2Token",
  "username": "your-email@example.com",
  "application_name": "Your App Name",
  "client_id": "YOUR_API_KEY",
  "token_type": "Bearer",
  "access_token": "YOUR_ACCESS_TOKEN_HERE",
  "expires_in": 1799,
  "state": "approved",
  "scope": ""
}
```

**Save the `access_token` value** - you'll need it for the next request.

---

## 2. Flight Inspiration Search API (Flight Destinations)

### Example from Your Log

**URL**: `https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15%2C2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True`

### cURL Example

```bash
curl -X GET "https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Postman Setup

1. **Method**: `GET`
2. **URL**: `https://api.amadeus.com/v1/shopping/flight-destinations`
3. **Headers**:
   - `Authorization: Bearer YOUR_ACCESS_TOKEN_HERE`
4. **Query Parameters**:
   - `origin`: `TLV` (required)
   - `departureDate`: `2025-11-15,2026-01-19` (optional, date range)
   - `viewBy`: `DESTINATION` (optional, groups by destination)
   - `oneWay`: `False` (optional, false for round-trip)
   - `nonStop`: `True` (optional, true for direct flights only)

### Postman Collection JSON

You can import this into Postman:

```json
{
  "info": {
    "name": "Amadeus Flight Inspiration Search",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Access Token",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "grant_type",
              "value": "client_credentials"
            },
            {
              "key": "client_id",
              "value": "YOUR_API_KEY"
            },
            {
              "key": "client_secret",
              "value": "YOUR_API_SECRET"
            }
          ]
        },
        "url": {
          "raw": "https://api.amadeus.com/v1/security/oauth2/token",
          "protocol": "https",
          "host": ["api", "amadeus", "com"],
          "path": ["v1", "security", "oauth2", "token"]
        }
      }
    },
    {
      "name": "Flight Destinations - TLV with nonStop",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}",
            "type": "text"
          }
        ],
        "url": {
          "raw": "https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True",
          "protocol": "https",
          "host": ["api", "amadeus", "com"],
          "path": ["v1", "shopping", "flight-destinations"],
          "query": [
            {
              "key": "origin",
              "value": "TLV"
            },
            {
              "key": "departureDate",
              "value": "2025-11-15,2026-01-19"
            },
            {
              "key": "viewBy",
              "value": "DESTINATION"
            },
            {
              "key": "oneWay",
              "value": "False"
            },
            {
              "key": "nonStop",
              "value": "True"
            }
          ]
        }
      }
    }
  ]
}
```

### Response Example

```json
{
  "data": [
    {
      "type": "flight-destination",
      "origin": "TLV",
      "destination": "ATH",
      "departureDate": "2025-11-20",
      "returnDate": "2025-11-25",
      "price": {
        "total": "245.50",
        "currency": "EUR"
      },
      "links": {
        "flightDates": "https://api.amadeus.com/v1/shopping/flight-dates?origin=TLV&destination=ATH&departureDate=2025-11-15,2026-01-19&oneWay=false&nonStop=true&viewBy=DURATION",
        "flightOffers": "https://api.amadeus.com/v1/shopping/flight-offers?originLocationCode=TLV&destinationLocationCode=ATH&departureDate=2025-11-20&returnDate=2025-11-25&adults=1&nonStop=true"
      }
    },
    {
      "type": "flight-destination",
      "origin": "TLV",
      "destination": "PAR",
      "departureDate": "2025-11-20",
      "returnDate": "2025-11-25",
      "price": {
        "total": "320.00",
        "currency": "EUR"
      },
      "links": {
        "flightDates": "https://api.amadeus.com/v1/shopping/flight-dates?origin=TLV&destination=PAR&departureDate=2025-11-15,2026-01-19&oneWay=false&nonStop=true&viewBy=DURATION",
        "flightOffers": "https://api.amadeus.com/v1/shopping/flight-offers?originLocationCode=TLV&destinationLocationCode=PAR&departureDate=2025-11-20&returnDate=2025-11-25&adults=1&nonStop=true"
      }
    }
  ],
  "meta": {
    "count": 2,
    "links": {
      "self": "https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True"
    }
  }
}
```

---

## 3. Alternative Examples

### Without nonStop Parameter (All Flights)

```bash
curl -X GET "https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### For Test Environment

Replace `api.amadeus.com` with `test.api.amadeus.com`:

```bash
curl -X GET "https://test.api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Different Origin (e.g., ALC)

```bash
curl -X GET "https://api.amadeus.com/v1/shopping/flight-destinations?origin=ALC&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 4. Postman Environment Variables

To make testing easier, set up environment variables in Postman:

1. Create a new environment (e.g., "Amadeus Production")
2. Add variables:
   - `base_url`: `https://api.amadeus.com` (or `https://test.api.amadeus.com` for test)
   - `api_key`: `YOUR_API_KEY`
   - `api_secret`: `YOUR_API_SECRET`
   - `access_token`: (will be set automatically after getting token)

3. Use variables in requests:
   - URL: `{{base_url}}/v1/shopping/flight-destinations`
   - Authorization: `Bearer {{access_token}}`

---

## 5. Troubleshooting

### 401 Unauthorized
- Check that your access token is valid (tokens expire after ~30 minutes)
- Verify your API credentials are correct
- Make sure you're using the correct environment (test vs production)

### 404 Not Found
- In test environment, some origins (like TLV) may not have data
- Try a different origin (e.g., MAD, PAR, LON)
- Switch to production environment for complete data

### 400 Bad Request
- Check parameter names and values
- Ensure date format is correct: `YYYY-MM-DD` or `YYYY-MM-DD,YYYY-MM-DD`
- Verify `viewBy` is either `DESTINATION` or `DURATION`
- Ensure `oneWay` and `nonStop` are boolean values (`True`/`False`)

---

## 6. Official Documentation

- **Flight Inspiration Search API**: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search
- **API Reference**: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search/api-reference
- **Authentication Guide**: https://developers.amadeus.com/get-started/apis-docs/guides/authentication-oauth-2-0

---

## Quick Test Script

Save this as `test_amadeus.sh`:

```bash
#!/bin/bash

# Set your credentials
API_KEY="YOUR_API_KEY"
API_SECRET="YOUR_API_SECRET"

# Get access token
echo "Getting access token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://api.amadeus.com/v1/security/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$API_KEY&client_secret=$API_SECRET")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Failed to get access token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Access token obtained: ${ACCESS_TOKEN:0:20}..."

# Test Flight Destinations API
echo ""
echo "Testing Flight Destinations API..."
curl -X GET "https://api.amadeus.com/v1/shopping/flight-destinations?origin=TLV&departureDate=2025-11-15,2026-01-19&viewBy=DESTINATION&oneWay=False&nonStop=True" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
```

Make it executable: `chmod +x test_amadeus.sh`
Run it: `./test_amadeus.sh`

