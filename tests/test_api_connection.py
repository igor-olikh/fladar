#!/usr/bin/env python3
"""
Test script to check Amadeus API connection and see actual error messages
"""
import sys
import os
import unittest
# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from flight_search import FlightSearch
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestAPIConnection(unittest.TestCase):
    """Test Amadeus API connection with real credentials"""
    
    def setUp(self):
        """Set up test - skip if config.yaml doesn't exist"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        if not os.path.exists(config_path):
            self.skipTest("config.yaml not found - skipping API connection test (requires real credentials)")
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def test_api_connection(self):
        """Test Amadeus API connection with real credentials"""
        config = self.config
    
        api_key = config['api']['amadeus_api_key']
        api_secret = config['api']['amadeus_api_secret']
        environment = config['api'].get('environment', 'test')
        
        # Initialize flight search
        flight_search = FlightSearch(api_key, api_secret, environment=environment)
        
        # Try a simple search with dates from config
        departure_date = config['search']['outbound_date']
        return_date = config['search']['return_date']
        
        flights = flight_search.search_flights(
            origin="TLV",
            destination="PAR",
            departure_date=departure_date,
            return_date=return_date,
            max_stops=0  # search_flights still uses single max_stops parameter
        )
        
        # Just verify the search completed without error
        self.assertIsInstance(flights, list)

if __name__ == '__main__':
    unittest.main()

