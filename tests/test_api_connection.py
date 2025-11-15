#!/usr/bin/env python3
"""
Test script to check Amadeus API connection and see actual error messages
"""
import sys
import os
# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from flight_search import FlightSearch
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_api_connection():
    """Test Amadeus API connection with real credentials"""
    # Load config from parent directory
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config['api']['amadeus_api_key']
    api_secret = config['api']['amadeus_api_secret']
    environment = config['api'].get('environment', 'test')
    
    print("=" * 80)
    print("Testing Amadeus API Connection")
    print("=" * 80)
    print(f"Environment: {environment.upper()}")
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '***'}")
    print(f"API Secret: {'*' * len(api_secret)}")
    print()
    
    try:
        # Initialize flight search
        print("Initializing FlightSearch...")
        flight_search = FlightSearch(api_key, api_secret, environment=environment)
        print("✓ FlightSearch initialized successfully")
        print()
        
        # Try a simple search with dates from config
        departure_date = config['search']['outbound_date']
        return_date = config['search']['return_date']
        
        print(f"Testing flight search: TLV → PAR ({departure_date} to {return_date})...")
        flights = flight_search.search_flights(
            origin="TLV",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0  # search_flights still uses single max_stops parameter
        )
        
        print(f"✓ Search completed. Found {len(flights)} flight(s)")
        
        if flights:
            print("\nFirst flight details:")
            flight = flights[0]
            print(f"  Price: {flight.get('price', {}).get('total', 'N/A')} {flight.get('price', {}).get('currency', 'N/A')}")
            print(f"  Itineraries: {len(flight.get('itineraries', []))}")
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print(f"\n   Full error details:")
        import traceback
        traceback.print_exc()
        
        # Check if it's a ResponseError from Amadeus
        from amadeus import ResponseError
        if isinstance(e, ResponseError):
            print(f"\n   This is an Amadeus API ResponseError")
            print(f"   Response code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            print(f"   Response body: {e.response.body if hasattr(e, 'response') else 'N/A'}")

if __name__ == '__main__':
    test_api_connection()

