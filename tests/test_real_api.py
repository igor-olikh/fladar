#!/usr/bin/env python3
"""
Real API Test - Test Amadeus API connection with actual credentials
Run this to verify your API setup is working correctly
"""
import sys
import os
import unittest
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

class TestRealAPI(unittest.TestCase):
    """Test Amadeus API connection with real credentials"""
    
    def setUp(self):
        """Set up test - skip if config.yaml doesn't exist"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        if not os.path.exists(config_path):
            self.skipTest("config.yaml not found - skipping real API test (requires real credentials)")
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def test_real_api_connection(self):
        """Test Amadeus API connection with real credentials"""
        config = self.config
        
        api_key = config['api']['amadeus_api_key']
        api_secret = config['api']['amadeus_api_secret']
        environment = config['api'].get('environment', 'test')
        departure_date = config['search']['outbound_date']
        return_date = config['search']['return_date']
        
        # Initialize flight search
        flight_search = FlightSearch(api_key, api_secret, environment=environment)
        
        # Test 1: Simple search TLV → PAR
        flights = flight_search.search_flights(
            origin="TLV",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0  # search_flights still uses single max_stops parameter
        )
        
        # Just verify the search completed without error
        self.assertIsInstance(flights, list)
        
        # Test 2: Search ALC → PAR
        flights2 = flight_search.search_flights(
            origin="ALC",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0  # search_flights still uses single max_stops parameter
        )
        
        # Just verify the search completed without error
        self.assertIsInstance(flights2, list)

if __name__ == '__main__':
    unittest.main()

