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

### 1.1. Pricing Data Differences

#### Test Environment Pricing
- **Not Real Prices**: Prices in the test environment are **NOT real or accurate**
- **Sample/Test Values**: Prices are sample values used for testing API functionality
- **May Be Outdated**: Prices may reflect historical values from when test data was created
- **No Booking Validity**: Prices cannot be used for actual booking - they are for testing only
- **Inconsistent Pricing**: Prices may not follow real-world pricing patterns or market dynamics
- **Fixed Values**: Some routes may always return the same price regardless of date or availability
- **Currency Accuracy**: Currency values may not reflect actual exchange rates

**⚠️ Critical Warning**: Never use test environment prices for:
- Making booking decisions
- Price comparisons
- Budget planning
- Showing prices to end users
- Any production use case

#### Production Environment Pricing
- **Real-Time Market Prices**: Prices reflect actual current market rates
- **Accurate and Current**: Prices are updated in real-time based on availability and demand
- **Booking Valid**: Prices shown are the actual prices you would pay when booking
- **Dynamic Pricing**: Prices follow real-world pricing patterns (higher for popular dates, lower for off-peak)
- **Currency Accuracy**: Exchange rates are current and accurate
- **Availability-Based**: Prices change based on seat availability and booking class
- **Supplier Rates**: Prices come directly from airlines and reflect their current pricing

**✅ Production prices are:**
- Suitable for actual bookings
- Accurate for customer-facing applications
- Reliable for price comparisons
- Valid for budget planning
- Current and up-to-date

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
6. **Unrealistic Prices**: Prices may be artificially low or high, not reflecting real market conditions
7. **No Price Variation**: Prices may not change based on booking date, seasonality, or demand
8. **Missing Price Components**: Some price breakdowns (taxes, fees) may be incomplete or incorrect

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

## Official Documentation

For the most up-to-date and official information, please refer to:

- [Amadeus for Developers - Main Portal](https://developers.amadeus.com/)
- [Amadeus Self-Service API Documentation](https://developers.amadeus.com/self-service)
- [Amadeus API Reference](https://developers.amadeus.com/self-service/apis-docs)
- [Amadeus Getting Started Guide](https://developers.amadeus.com/get-started)

**Note**: The information in this document is based on standard API practices and observations from using the Amadeus API. For the most current and accurate information about test vs production environments, please consult the official Amadeus documentation linked above.

## Summary

| Feature | Test Environment | Production Environment |
|---------|-----------------|----------------------|
| **Data Type** | Cached/Historical | Real-time |
| **Data Accuracy** | May be outdated | Current and accurate |
| **Route Coverage** | Limited | Complete |
| **Price Accuracy** | ❌ Not real - sample/test values only | ✅ Real market prices |
| **Price Validity** | ❌ Cannot use for booking | ✅ Valid for actual bookings |
| **Price Updates** | ❌ Static/fixed | ✅ Dynamic, real-time |
| **Use Case** | Development/Testing | Production |
| **Rate Limits** | 2,000 calls/month | 2,000+ calls/month |
| **Booking Ready** | ❌ No | ✅ Yes |
| **Free Tier** | ✅ Yes | ✅ Yes |

## Price Comparison Example

### Test Environment
```
Route: TLV → PAR
Date: 2025-11-20
Price: 284.99 EUR
Status: ⚠️ Sample/test price - NOT valid for booking
```

### Production Environment
```
Route: TLV → PAR
Date: 2025-11-20
Price: 450.00 EUR (example - actual price varies)
Status: ✅ Real market price - valid for booking
```

**Important**: The same route and date may show completely different prices between test and production environments. Always use production environment for any price-related decisions.

