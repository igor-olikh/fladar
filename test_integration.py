"""
Integration test to verify the application can find at least one result
"""
import unittest
import yaml
import os
from unittest.mock import Mock, patch, MagicMock

# Try to import amadeus, if not available, we'll mock it in tests
try:
    from amadeus import Client, ResponseError
except ImportError:
    Client = None
    ResponseError = Exception

from flight_search import FlightSearch
from destination_finder import DestinationFinder


class TestFindAtLeastOneResult(unittest.TestCase):
    """Test that the application can find at least one matching result"""
    
    def setUp(self):
        """Set up test with realistic mock data"""
        # Create realistic flight data that would match
        self.mock_flight_tlv = {
            'price': {'total': '300.00', 'currency': 'EUR'},
            'itineraries': [
                {
                    'duration': 'PT4H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-15T08:00:00Z', 'iataCode': 'TLV'},
                            'arrival': {'at': '2024-12-15T12:30:00Z', 'iataCode': 'PAR'},
                            'numberOfStops': 0,
                            'carrierCode': 'LY'
                        }
                    ]
                },
                {
                    'duration': 'PT4H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-22T14:00:00Z', 'iataCode': 'PAR'},
                            'arrival': {'at': '2024-12-22T18:30:00Z', 'iataCode': 'TLV'},
                            'numberOfStops': 0,
                            'carrierCode': 'LY'
                        }
                    ]
                }
            ]
        }
        
        self.mock_flight_alc = {
            'price': {'total': '250.00', 'currency': 'EUR'},
            'itineraries': [
                {
                    'duration': 'PT2H0M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-15T10:00:00Z', 'iataCode': 'ALC'},
                            'arrival': {'at': '2024-12-15T12:00:00Z', 'iataCode': 'PAR'},  # 30 min before TLV
                            'numberOfStops': 0,
                            'carrierCode': 'VY'
                        }
                    ]
                },
                {
                    'duration': 'PT2H0M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-22T15:00:00Z', 'iataCode': 'PAR'},
                            'arrival': {'at': '2024-12-22T17:00:00Z', 'iataCode': 'ALC'},
                            'numberOfStops': 0,
                            'carrierCode': 'VY'
                        }
                    ]
                }
            ]
        }
    
    @patch('flight_search.Client')
    def test_find_matching_result(self, mock_client):
        """Test that we can find at least one matching result"""
        # Setup mocks
        mock_amadeus = Mock()
        mock_client.return_value = mock_amadeus
        
        # Mock destination suggestions
        destinations = ["PAR", "LON", "MAD", "BCN"]
        
        # Mock flight search - return flights for PAR, empty for others
        def flight_search_side_effect(*args, **kwargs):
            origin = kwargs.get('originLocationCode')
            destination = kwargs.get('destinationLocationCode')
            
            if destination == 'PAR':
                if origin == 'TLV':
                    return Mock(data=[self.mock_flight_tlv])
                elif origin == 'ALC':
                    return Mock(data=[self.mock_flight_alc])
            return Mock(data=[])
        
        mock_amadeus.shopping.flight_offers_search.get.side_effect = flight_search_side_effect
        mock_amadeus.reference_data.locations.airports.get.return_value = Mock(data=[])
        
        # Create flight search
        flight_search = FlightSearch("test_key", "test_secret")
        flight_search.amadeus = mock_amadeus
        
        # Override destination suggestions
        flight_search.get_destination_suggestions = lambda origin, date: destinations
        
        # Create destination finder
        destination_finder = DestinationFinder(flight_search)
        
        # Search for matching destinations
        results = destination_finder.find_meeting_destinations(
            origin1="TLV",
            origin2="ALC",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_price=500.0,  # Both flights are under 500
            max_stops=0,
            arrival_tolerance_hours=3,  # 30 min difference is within 3 hours
            max_destinations=10
        )
        
        # Should find at least one result
        self.assertGreater(len(results), 0, "Should find at least one matching flight pair")
        
        # Verify the result
        match = results[0]
        self.assertEqual(match['destination'], 'PAR')
        self.assertLessEqual(match['person1_price'], 500.0)
        self.assertLessEqual(match['person2_price'], 500.0)
        self.assertIn('person1_flight', match)
        self.assertIn('person2_flight', match)
    
    @patch('flight_search.Client')
    def test_price_filtering(self, mock_client):
        """Test that price filtering works correctly"""
        mock_amadeus = Mock()
        mock_client.return_value = mock_amadeus
        
        # Create expensive flight
        expensive_flight = self.mock_flight_tlv.copy()
        expensive_flight['price']['total'] = '600.00'  # Over max price
        
        def flight_search_side_effect(*args, **kwargs):
            origin = kwargs.get('originLocationCode')
            if origin == 'TLV':
                return Mock(data=[expensive_flight])
            else:
                return Mock(data=[self.mock_flight_alc])
        
        mock_amadeus.shopping.flight_offers_search.get.side_effect = flight_search_side_effect
        mock_amadeus.reference_data.locations.airports.get.return_value = Mock(data=[])
        
        flight_search = FlightSearch("test_key", "test_secret")
        flight_search.amadeus = mock_amadeus
        flight_search.get_destination_suggestions = lambda origin, date: ["PAR"]
        
        destination_finder = DestinationFinder(flight_search)
        
        results = destination_finder.find_meeting_destinations(
            origin1="TLV",
            origin2="ALC",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_price=500.0,  # TLV flight is 600, should be filtered out
            max_stops=0,
            arrival_tolerance_hours=3
        )
        
        # Should find no results because TLV flight is too expensive
        self.assertEqual(len(results), 0)
    
    @patch('flight_search.Client')
    def test_arrival_time_matching(self, mock_client):
        """Test that arrival time matching works correctly"""
        mock_amadeus = Mock()
        mock_client.return_value = mock_amadeus
        
        # Create flight with arrival too far apart
        late_flight = self.mock_flight_alc.copy()
        late_flight['itineraries'][0]['segments'][0]['arrival']['at'] = '2024-12-15T18:00:00Z'  # 5.5 hours after TLV
        
        def flight_search_side_effect(*args, **kwargs):
            origin = kwargs.get('originLocationCode')
            if origin == 'TLV':
                return Mock(data=[self.mock_flight_tlv])
            else:
                return Mock(data=[late_flight])
        
        mock_amadeus.shopping.flight_offers_search.get.side_effect = flight_search_side_effect
        mock_amadeus.reference_data.locations.airports.get.return_value = Mock(data=[])
        
        flight_search = FlightSearch("test_key", "test_secret")
        flight_search.amadeus = mock_amadeus
        flight_search.get_destination_suggestions = lambda origin, date: ["PAR"]
        
        destination_finder = DestinationFinder(flight_search)
        
        results = destination_finder.find_meeting_destinations(
            origin1="TLV",
            origin2="ALC",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_price=500.0,
            max_stops=0,
            arrival_tolerance_hours=3  # 5.5 hours is outside tolerance
        )
        
        # Should find no results because arrivals are too far apart
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()

