# Amadeus API: Test vs Production Environment

## Overview

Amadeus provides two API environments for developers: **Test** and **Production**. Understanding the differences between these environments is crucial for developing and deploying flight search applications.

## Environment URLs

- **Test Environment**: `test.api.amadeus.com`
- **Production Environment**: `api.amadeus.com`

## Key Differences

### 1. Data Availability and Real-Time Status

#### Test Environment
- **Cached/Historical Data**: Uses cached or historical flight data, not real-time availability
- **Limited Destinations**: May not have data for all routes or destinations
- **Static Data**: Flight prices and availability are not updated in real-time
- **Sample Data**: Designed for testing API integration, not for actual booking
- **Data Freshness**: Data may be outdated or not reflect current flight schedules

#### Production Environment
- **Real-Time Data**: Provides live, real-time flight availability and pricing
- **Complete Coverage**: Access to all available routes and destinations
- **Current Prices**: Prices reflect current market conditions and availability
- **Booking Ready**: Data is suitable for actual flight booking applications
- **Up-to-Date**: Continuously updated with the latest flight information

### 2. API Rate Limits

#### Test Environment
- **Free Tier**: 2,000 API calls per month
- **Rate Limit**: 10 transactions per second per user
- **Suitable For**: Development and testing

#### Production Environment
- **Free Tier**: 2,000 API calls per month (same as test)
- **Rate Limit**: Varies based on your subscription tier
- **Suitable For**: Production applications with real users

### 3. Use Cases

#### Test Environment
✅ **Recommended for:**
- Initial development and testing
- API integration testing
- Learning the API structure
- Prototyping applications
- Testing error handling
- Development without affecting production quotas

❌ **Not suitable for:**
- Actual flight bookings
- Real customer-facing applications
- Applications requiring current flight data
- Production deployments

#### Production Environment
✅ **Recommended for:**
- Production applications
- Real customer bookings
- Applications requiring accurate, real-time data
- Commercial deployments

❌ **Not suitable for:**
- Initial development (use test first)
- Testing API changes (use test first)

### 4. Data Limitations in Test Environment

The test environment has several limitations that developers should be aware of:

1. **Limited Route Coverage**: Not all origin-destination pairs may have test data
2. **Outdated Information**: Flight schedules and prices may not reflect current reality
3. **Missing Destinations**: Some destinations may not be available in test data
4. **Date Restrictions**: Test data may only be available for specific date ranges
5. **Incomplete Results**: Some API endpoints may return 404 errors for certain queries

### 5. Error Handling Differences

#### Test Environment
- May return 404 errors for routes without test data
- Some endpoints may not be fully available
- Error responses may differ from production

#### Production Environment
- More consistent error responses
- Better error messages for invalid requests
- All endpoints fully functional

## Configuration in This Application

This application allows you to switch between test and production environments using the `config.yaml` file:

```yaml
api:
  environment: "test"  # or "production"
```

### When to Use Each Environment

**Use Test Environment When:**
- Developing and testing the application
- Learning how the API works
- Prototyping new features
- Running automated tests
- You don't need real-time flight data

**Use Production Environment When:**
- Deploying to production
- Serving real users
- You need accurate, real-time flight data
- You're ready to make actual bookings

## Important Notes

⚠️ **Warning**: Never use test environment data for actual flight bookings. Test data is not guaranteed to be accurate or current.

⚠️ **API Keys**: Test and production environments require separate API credentials. You cannot use test API keys with the production environment and vice versa.

⚠️ **Data Accuracy**: Always verify that your application works correctly in the production environment before deploying to users, as test data may behave differently.

## References

- [Amadeus for Developers](https://developers.amadeus.com/)
- [Amadeus API Documentation](https://developers.amadeus.com/self-service)
- [Amadeus Test Data Guide](https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/test-data)

## Summary

| Feature | Test Environment | Production Environment |
|---------|-----------------|----------------------|
| **Data Type** | Cached/Historical | Real-time |
| **Data Accuracy** | May be outdated | Current and accurate |
| **Route Coverage** | Limited | Complete |
| **Use Case** | Development/Testing | Production |
| **Rate Limits** | 2,000 calls/month | 2,000+ calls/month |
| **Booking Ready** | ❌ No | ✅ Yes |
| **Free Tier** | ✅ Yes | ✅ Yes |

