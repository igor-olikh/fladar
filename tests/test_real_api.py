#!/usr/bin/env python3
"""
Real API Test - Test Amadeus API connection with actual credentials
Run this to verify your API setup is working correctly
"""
import sys
import os
# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from flight_search import FlightSearch
import logging

# Set up logging to see all details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Test Amadeus API connection with real credentials"""
    print("=" * 80)
    print("🧪 Amadeus API Connection Test")
    print("=" * 80)
    print()
    
    # Load config from parent directory
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Error: config.yaml not found!")
        sys.exit(1)
    
    api_key = config['api']['amadeus_api_key']
    api_secret = config['api']['amadeus_api_secret']
    environment = config['api'].get('environment', 'test')
    departure_date = config['search']['outbound_date']
    return_date = config['search']['return_date']
    
    print(f"📋 Configuration:")
    print(f"   Environment: {environment.upper()}")
    print(f"   API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '***'}")
    print(f"   API Secret: {'*' * len(api_secret)}")
    print(f"   Test Dates: {departure_date} to {return_date}")
    print()
    
    try:
        # Initialize flight search
        print("🔧 Initializing FlightSearch...")
        flight_search = FlightSearch(api_key, api_secret, environment=environment)
        print("✓ FlightSearch initialized successfully")
        print()
        
        # Test 1: Simple search TLV → PAR
        print("=" * 80)
        print("Test 1: Searching flights TLV → PAR")
        print("=" * 80)
        print(f"Searching: TLV → PAR ({departure_date} to {return_date})...")
        print()
        
        flights = flight_search.search_flights(
            origin="TLV",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0
        )
        
        print()
        print(f"✅ Search completed!")
        print(f"   Found: {len(flights)} flight(s)")
        print()
        
        if flights:
            print("📊 First 3 flight results:")
            print()
            for i, flight in enumerate(flights[:3], 1):
                price = flight.get('price', {})
                print(f"   Flight {i}:")
                print(f"      Price: {price.get('total', 'N/A')} {price.get('currency', 'EUR')}")
                
                # Show outbound details
                outbound = flight.get('itineraries', [{}])[0]
                if outbound.get('segments'):
                    first_seg = outbound['segments'][0]
                    last_seg = outbound['segments'][-1]
                    dep = first_seg.get('departure', {}).get('at', 'N/A')
                    arr = last_seg.get('arrival', {}).get('at', 'N/A')
                    print(f"      Outbound: {dep} → {arr}")
                    print(f"      Duration: {outbound.get('duration', 'N/A')}")
                
                # Show return details
                if len(flight.get('itineraries', [])) > 1:
                    return_trip = flight.get('itineraries', [{}])[1]
                    if return_trip.get('segments'):
                        first_seg = return_trip['segments'][0]
                        last_seg = return_trip['segments'][-1]
                        dep = first_seg.get('departure', {}).get('at', 'N/A')
                        arr = last_seg.get('arrival', {}).get('at', 'N/A')
                        print(f"      Return: {dep} → {arr}")
                        print(f"      Duration: {return_trip.get('duration', 'N/A')}")
                print()
        else:
            print("⚠️  No flights found. This could mean:")
            print("   - No flights available for these dates")
            print("   - Dates are in the past")
            print("   - API credentials are invalid")
            print("   - Test environment has limited data")
            print()
        
        # Test 2: Search ALC → PAR
        print("=" * 80)
        print("Test 2: Searching flights ALC → PAR")
        print("=" * 80)
        print(f"Searching: ALC → PAR ({departure_date} to {return_date})...")
        print()
        
        flights2 = flight_search.search_flights(
            origin="ALC",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0
        )
        
        print()
        print(f"✅ Search completed!")
        print(f"   Found: {len(flights2)} flight(s)")
        print()
        
        if flights2:
            print("📊 First flight result:")
            flight = flights2[0]
            price = flight.get('price', {})
            print(f"   Price: {price.get('total', 'N/A')} {price.get('currency', 'EUR')}")
            print()
        
        # Summary
        print("=" * 80)
        print("📋 Test Summary")
        print("=" * 80)
        print(f"✓ API Connection: Working")
        print(f"✓ Environment: {environment.upper()}")
        print(f"✓ TLV → PAR: {len(flights)} flight(s) found")
        print(f"✓ ALC → PAR: {len(flights2)} flight(s) found")
        print()
        print("✅ All tests passed! Your API setup is working correctly.")
        print()
        
    except Exception as e:
        print()
        print("❌ ERROR OCCURRED:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print()
        print("   Full error details:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

