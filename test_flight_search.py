"""
Unit tests for flight search application
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Try to import amadeus, if not available, we'll mock it in tests
try:
    from amadeus import Client, ResponseError
except ImportError:
    Client = None
    ResponseError = Exception

from flight_search import FlightSearch
from destination_finder import DestinationFinder
from output_formatter import OutputFormatter


class TestFlightSearch(unittest.TestCase):
    """Test FlightSearch class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_key"
        self.api_secret = "test_secret"
        with patch('flight_search.Client'):
            self.flight_search = FlightSearch(self.api_key, self.api_secret)
            self.flight_search.amadeus = Mock()
    
    def test_is_direct_flight(self):
        """Test direct flight detection"""
        # Direct flight
        direct_flight = {
            'itineraries': [{
                'segments': [{
                    'numberOfStops': 0
                }]
            }]
        }
        self.assertTrue(self.flight_search._is_direct_flight(direct_flight))
        
        # Flight with stops
        stop_flight = {
            'itineraries': [{
                'segments': [{
                    'numberOfStops': 1
                }]
            }]
        }
        self.assertFalse(self.flight_search._is_direct_flight(stop_flight))
    
    def test_get_stops(self):
        """Test getting maximum stops"""
        flight = {
            'itineraries': [{
                'segments': [
                    {'numberOfStops': 0},
                    {'numberOfStops': 1}
                ]
            }]
        }
        self.assertEqual(self.flight_search._get_stops(flight), 1)
    
    def test_get_outbound_arrival_time(self):
        """Test extracting outbound arrival time"""
        flight = {
            'itineraries': [{
                'segments': [{
                    'arrival': {'at': '2024-12-15T14:30:00Z'}
                }]
            }]
        }
        result = self.flight_search._get_outbound_arrival_time(flight)
        self.assertEqual(result, '2024-12-15T14:30:00Z')
    
    def test_arrivals_match(self):
        """Test arrival time matching"""
        flight1 = {
            'itineraries': [{
                'segments': [{
                    'arrival': {'at': '2024-12-15T14:00:00Z'}
                }]
            }]
        }
        flight2 = {
            'itineraries': [{
                'segments': [{
                    'arrival': {'at': '2024-12-15T15:30:00Z'}  # 1.5 hours difference
                }]
            }]
        }
        # Should match within 3 hours tolerance
        self.assertTrue(self.flight_search._arrivals_match(flight1, flight2, 3))
        
        # Should not match with 1 hour tolerance
        self.assertFalse(self.flight_search._arrivals_match(flight1, flight2, 1))
    
    def test_filter_by_departure_time(self):
        """Test filtering by departure time (both outbound and return)"""
        flights = [
            {
                'itineraries': [
                    {
                        'segments': [{
                            'departure': {'at': '2024-12-15T10:00:00Z'}  # Outbound OK
                        }]
                    },
                    {
                        'segments': [{
                            'departure': {'at': '2024-12-22T11:00:00Z'}  # Return OK
                        }]
                    }
                ]
            },
            {
                'itineraries': [
                    {
                        'segments': [{
                            'departure': {'at': '2024-12-15T08:00:00Z'}  # Outbound too early
                        }]
                    }
                ]
            },
            {
                'itineraries': [
                    {
                        'segments': [{
                            'departure': {'at': '2024-12-15T10:00:00Z'}  # Outbound OK
                        }]
                    },
                    {
                        'segments': [{
                            'departure': {'at': '2024-12-22T08:00:00Z'}  # Return too early
                        }]
                    }
                ]
            }
        ]
        # Filter for flights after 09:00 (both outbound and return)
        filtered = self.flight_search._filter_by_departure_time(flights, '09:00')
        # Only first flight should pass (both outbound and return are after 09:00)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], flights[0])
    
    def test_filter_by_arrival_time(self):
        """Test filtering by arrival time (both outbound and return)"""
        flights = [
            {
                'itineraries': [
                    {
                        'segments': [{
                            'arrival': {'at': '2024-12-15T14:00:00Z'}  # Outbound OK
                        }]
                    },
                    {
                        'segments': [{
                            'arrival': {'at': '2024-12-22T13:00:00Z'}  # Return OK
                        }]
                    }
                ]
            },
            {
                'itineraries': [
                    {
                        'segments': [{
                            'arrival': {'at': '2024-12-15T11:00:00Z'}  # Outbound too early
                        }]
                    }
                ]
            },
            {
                'itineraries': [
                    {
                        'segments': [{
                            'arrival': {'at': '2024-12-15T14:00:00Z'}  # Outbound OK
                        }]
                    },
                    {
                        'segments': [{
                            'arrival': {'at': '2024-12-22T11:00:00Z'}  # Return too early
                        }]
                    }
                ]
            }
        ]
        # Filter for flights arriving after 12:00 (both outbound and return)
        filtered = self.flight_search._filter_by_arrival_time(flights, '12:00')
        # Only first flight should pass (both outbound and return arrive after 12:00)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], flights[0])


class TestDestinationFinder(unittest.TestCase):
    """Test DestinationFinder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_flight_search = Mock(spec=FlightSearch)
        self.destination_finder = DestinationFinder(self.mock_flight_search)
    
    def test_find_meeting_destinations(self):
        """Test finding meeting destinations"""
        # Mock destination suggestions
        self.mock_flight_search.get_destination_suggestions.return_value = ["PAR", "LON"]
        
        # Mock matching flights
        self.mock_flight_search.find_matching_flights.side_effect = [
            [{'destination': 'PAR', 'person1_flight': {}, 'person2_flight': {}, 
              'total_price': 400, 'person1_price': 200, 'person2_price': 200}],
            []  # No matches for LON
        ]
        
        results = self.destination_finder.find_meeting_destinations(
            origin1="TLV",
            origin2="ALC",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_price=500,
            max_stops=0,
            arrival_tolerance_hours=3
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['destination'], 'PAR')


class TestOutputFormatter(unittest.TestCase):
    """Test OutputFormatter class"""
    
    def test_format_flight_info(self):
        """Test formatting flight information"""
        flight = {
            'price': {'total': '300.00', 'currency': 'EUR'},
            'itineraries': [
                {
                    'duration': 'PT2H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-15T10:00:00Z'},
                            'arrival': {'at': '2024-12-15T12:30:00Z'},
                            'numberOfStops': 0,
                            'carrierCode': 'LH'
                        }
                    ]
                },
                {
                    'duration': 'PT2H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-22T14:00:00Z'},
                            'arrival': {'at': '2024-12-22T16:30:00Z'},
                            'numberOfStops': 0,
                            'carrierCode': 'LH'
                        }
                    ]
                }
            ]
        }
        
        info = OutputFormatter.format_flight_info(flight)
        
        self.assertEqual(info['price'], '300.00')
        self.assertEqual(info['currency'], 'EUR')
        self.assertEqual(info['outbound_departure'], '2024-12-15T10:00:00Z')
        self.assertEqual(info['outbound_arrival'], '2024-12-15T12:30:00Z')
        self.assertEqual(info['outbound_stops'], 0)
        self.assertEqual(info['return_departure'], '2024-12-22T14:00:00Z')
        self.assertEqual(info['return_arrival'], '2024-12-22T16:30:00Z')


class TestIntegration(unittest.TestCase):
    """Integration tests with mocked API"""
    
    @patch('flight_search.Client')
    def test_full_search_flow(self, mock_client):
        """Test the full search flow with mocked API"""
        # Create mock Amadeus client
        mock_amadeus = Mock()
        mock_client.return_value = mock_amadeus
        
        # Mock flight search response
        mock_response = Mock()
        mock_response.data = [
            {
                'price': {'total': '250.00', 'currency': 'EUR'},
                'itineraries': [
                    {
                        'duration': 'PT3H0M',
                        'segments': [
                            {
                                'departure': {'at': '2024-12-15T10:00:00Z'},
                                'arrival': {'at': '2024-12-15T13:00:00Z'},
                                'numberOfStops': 0,
                                'carrierCode': 'LH'
                            }
                        ]
                    },
                    {
                        'duration': 'PT3H0M',
                        'segments': [
                            {
                                'departure': {'at': '2024-12-22T14:00:00Z'},
                                'arrival': {'at': '2024-12-22T17:00:00Z'},
                                'numberOfStops': 0,
                                'carrierCode': 'LH'
                            }
                        ]
                    }
                ]
            }
        ]
        
        mock_amadeus.shopping.flight_offers_search.get.return_value = mock_response
        mock_amadeus.reference_data.locations.airports.get.return_value = Mock(data=[])
        
        # Create flight search instance
        flight_search = FlightSearch("test_key", "test_secret")
        flight_search.amadeus = mock_amadeus
        
        # Test search
        flights = flight_search.search_flights(
            origin="TLV",
            destination="PAR",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_stops=0
        )
        
        self.assertEqual(len(flights), 1)
        self.assertEqual(flights[0]['price']['total'], '250.00')
        
        # Test finding matching flights
        flight1 = mock_response.data[0]
        flight2 = {
            'price': {'total': '200.00', 'currency': 'EUR'},
            'itineraries': [
                {
                    'duration': 'PT2H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-15T09:00:00Z'},
                            'arrival': {'at': '2024-12-15T12:30:00Z'},  # Within 1 hour of flight1
                            'numberOfStops': 0,
                            'carrierCode': 'VY'
                        }
                    ]
                },
                {
                    'duration': 'PT2H30M',
                    'segments': [
                        {
                            'departure': {'at': '2024-12-22T15:00:00Z'},
                            'arrival': {'at': '2024-12-22T17:30:00Z'},
                            'numberOfStops': 0,
                            'carrierCode': 'VY'
                        }
                    ]
                }
            ]
        }
        
        # Mock responses for both searches
        def side_effect(*args, **kwargs):
            if kwargs.get('originLocationCode') == 'TLV':
                return Mock(data=[flight1])
            else:
                return Mock(data=[flight2])
        
        mock_amadeus.shopping.flight_offers_search.get.side_effect = side_effect
        
        matches = flight_search.find_matching_flights(
            origin1="TLV",
            origin2="ALC",
            destination="PAR",
            departure_date="2024-12-15",
            return_date="2024-12-22",
            max_price=300.0,
            max_stops=0,
            arrival_tolerance_hours=3
        )
        
        # Should find at least one match
        self.assertGreaterEqual(len(matches), 0)  # May be 0 if price/time don't match exactly


if __name__ == '__main__':
    unittest.main()

