#!/usr/bin/env python3
"""
Flight Search Application
Finds destinations where two people can meet with matching flight arrivals

Version: 1.1.0
"""
__version__ = "1.1.0"
import yaml
import os
import sys
from typing import Optional
from flight_search import FlightSearch
from destination_finder import DestinationFinder
from output_formatter import OutputFormatter
import logging
from datetime import datetime

# Configure logging with both console and file handlers
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create debug logs directory if it doesn't exist
os.makedirs('debug_logs', exist_ok=True)

# Create file handler for debug logs
log_filename = f"debug_logs/flight_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format))

# Create console handler (INFO level for console, DEBUG for file)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)
logger.info(f"Debug logs will be saved to: {log_filename}")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)


def validate_config(config: dict) -> bool:
    """Validate configuration"""
    required_keys = [
        'origins', 'search', 'api'
    ]
    
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            return False
    
    # Check API credentials
    if not config['api'].get('amadeus_api_key') or not config['api'].get('amadeus_api_secret'):
        logger.error("Amadeus API credentials not set in config.yaml")
        logger.error("Please get your free API key at: https://developers.amadeus.com/")
        logger.error("Then add your credentials to config.yaml")
        return False
    
    return True


def main():
    """Main application entry point"""
    print("=" * 100)
    print("✈️  Flight Search Application - Find Meeting Destinations")
    print("=" * 100)
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not validate_config(config):
        sys.exit(1)
    
    # Extract configuration
    origin1 = config['origins']['person1']
    origin2 = config['origins']['person2']
    search_config = config['search']
    api_config = config['api']
    output_config = config.get('output', {})
    html_top_destinations = output_config.get('html_top_destinations', 3)
    booking_link_provider = output_config.get('booking_link_provider', 'google_flights')  # Default to Google Flights
    
    # Delete existing CSV and HTML output files from previous run if they exist
    output_format = output_config.get('format', 'console')
    csv_file = output_config.get('csv_file', 'flight_results.csv')
    html_file = output_config.get('html_file', 'flight_results.html')
    if 'csv' in output_format:
        if os.path.exists(csv_file):
            try:
                os.remove(csv_file)
                logger.info(f"Deleted previous CSV output file: {csv_file}")
            except Exception as e:
                logger.warning(f"Could not delete previous CSV file {csv_file}: {e}")
        # Also delete HTML file if it exists
        if os.path.exists(html_file):
            try:
                os.remove(html_file)
                logger.info(f"Deleted previous HTML output file: {html_file}")
            except Exception as e:
                logger.warning(f"Could not delete previous HTML file {html_file}: {e}")
    
    departure_date = search_config['outbound_date']
    flight_type = search_config.get('flight_type', 'both')  # Default to "both" for backward compatibility
    
    # Validate return_date based on flight_type
    return_date = search_config.get('return_date')
    if flight_type in ['both', 'return']:
        if not return_date:
            logger.error(f"❌ return_date is required for flight_type='{flight_type}'")
            logger.error(f"   Please add return_date to your config.yaml")
            sys.exit(1)
    # For "outbound", return_date is optional (ignored)
    
    max_price = float(search_config['max_price'])
    
    # Handle backward compatibility: check for old max_stops parameter
    if 'max_stops' in search_config and 'max_stops_person1' not in search_config:
        old_max_stops = search_config.get('max_stops', 0)
        logger.warning(f"⚠️  DEPRECATED: Old 'max_stops' parameter detected (value: {old_max_stops})")
        logger.warning(f"   Please update your config.yaml to use 'max_stops_person1' and 'max_stops_person2'")
        logger.warning(f"   See docs/MIGRATION_GUIDE.md for migration instructions")
        logger.warning(f"   Using {old_max_stops} for both persons as fallback")
        max_stops_person1 = old_max_stops
        max_stops_person2 = old_max_stops
    else:
        max_stops_person1 = search_config.get('max_stops_person1', 0)
        max_stops_person2 = search_config.get('max_stops_person2', 0)
    arrival_tolerance = search_config.get('arrival_tolerance_hours', 3)
    min_departure_time_outbound = search_config.get('min_departure_time_outbound') or None
    min_departure_time_return = search_config.get('min_departure_time_return') or None
    use_dynamic_destinations = search_config.get('use_dynamic_destinations', True)
    # Handle backward compatibility: check for old max_flight_duration_hours parameter
    if 'max_flight_duration_hours' in search_config and 'max_flight_duration_hours_person1' not in search_config:
        old_max_duration = float(search_config.get('max_flight_duration_hours', 0))
        logger.warning(f"⚠️  DEPRECATED: Old 'max_flight_duration_hours' parameter detected (value: {old_max_duration})")
        logger.warning(f"   Please update your config.yaml to use 'max_flight_duration_hours_person1' and 'max_flight_duration_hours_person2'")
        logger.warning(f"   Using {old_max_duration} for both persons as fallback")
        max_flight_duration_person1 = old_max_duration
        max_flight_duration_person2 = old_max_duration
    else:
        max_flight_duration_person1 = float(search_config.get('max_flight_duration_hours_person1', 0))
        max_flight_duration_person2 = float(search_config.get('max_flight_duration_hours_person2', 0))
    cache_expiration_days = search_config.get('destination_cache_expiration_days', 30)
    nearby_airports_radius_km = search_config.get('nearby_airports_radius_km', 0)
    return_airport_radius_km = search_config.get('return_airport_radius_km', 0)
    max_destinations_to_check = search_config.get('max_destinations_to_check', 50)
    use_flight_cache = search_config.get('use_flight_cache', True)
    # Check for destinations_to_check in search section first, then root level (for backward compatibility)
    destinations_to_check = search_config.get('destinations_to_check') or config.get('destinations_to_check', [])
    
    # Timezones are now automatically detected using airportsdata library
    # No manual configuration needed
    
    # Initialize flight search
    try:
        environment = api_config.get('environment', 'test')
        flight_search = FlightSearch(
            api_key=api_config['amadeus_api_key'],
            api_secret=api_config['amadeus_api_secret'],
            environment=environment,
            cache_expiration_days=cache_expiration_days,
            use_flight_cache=use_flight_cache
        )
    except Exception as e:
        logger.error(f"Failed to initialize flight search: {e}")
        sys.exit(1)
    
    # Initialize destination finder
    destination_finder = DestinationFinder(flight_search)
    
    # Airport code to city name mapping for display
    airport_names = {
        'TLV': 'Tel Aviv',
        'ALC': 'Alicante',
        'BCN': 'Barcelona',
        'LON': 'London',
        'PAR': 'Paris',
        'MAD': 'Madrid',
        'ROM': 'Rome',
        'AMS': 'Amsterdam',
        'BER': 'Berlin',
        'VIE': 'Vienna',
        'PRG': 'Prague',
        'ATH': 'Athens',
        'LIS': 'Lisbon',
        'DUB': 'Dublin',
        'CPH': 'Copenhagen',
        'STO': 'Stockholm',
        'OSL': 'Oslo',
        'MUC': 'Munich',
        'FCO': 'Rome',
        'BCN': 'Barcelona',
        'AGP': 'Malaga',
        'SEV': 'Seville',
        'ZUR': 'Zurich',
        'BRU': 'Brussels',
        'WAR': 'Warsaw',
        'BUD': 'Budapest',
        'ZAG': 'Zagreb',
        'HEL': 'Helsinki',
        'REK': 'Reykjavik',
        'OPO': 'Porto',
    }
    
    # Get city names for display
    origin1_name = airport_names.get(origin1.upper(), origin1)
    origin2_name = airport_names.get(origin2.upper(), origin2)
    
    # Display search parameters
    print(f"\n🔍 Search Parameters:")
    print(f"   Person 1 Origin: {origin1} ({origin1_name})")
    print(f"   Person 2 Origin: {origin2} ({origin2_name})")
    print(f"   Outbound Date: {departure_date}")
    print(f"   Return Date: {return_date}")
    print(f"   Max Price (per person): {max_price} EUR")
    print(f"   Max Stops - Person 1: {max_stops_person1}")
    print(f"   Max Stops - Person 2: {max_stops_person2}")
    print(f"   Flight Type: {flight_type}")
    print(f"   Arrival Tolerance: ±{arrival_tolerance} hours")
    if max_flight_duration_person1 > 0 or max_flight_duration_person2 > 0:
        print(f"   Max Flight Duration - Person 1: {max_flight_duration_person1} hours" + (" (no limit)" if max_flight_duration_person1 == 0 else ""))
        print(f"   Max Flight Duration - Person 2: {max_flight_duration_person2} hours" + (" (no limit)" if max_flight_duration_person2 == 0 else ""))
    print(f"   Destination Discovery: {'Dynamic (Amadeus API)' if use_dynamic_destinations else 'Predefined List'}")
    if min_departure_time_outbound:
        print(f"   Min Departure Time (Outbound): {min_departure_time_outbound}")
    if min_departure_time_return:
        print(f"   Min Departure Time (Return): {min_departure_time_return}")
    if nearby_airports_radius_km > 0:
        print(f"   Nearby Airports Radius: {nearby_airports_radius_km} km")
    if return_airport_radius_km > 0:
        print(f"   Return Airport Radius: {return_airport_radius_km} km (return flights can depart from nearby airports)")
    if destinations_to_check and len(destinations_to_check) > 0:
        print(f"   Specific Destinations to Check: {', '.join(destinations_to_check)}")
        print(f"   (Skipping destination discovery - using only specified destinations)")
    else:
        if max_destinations_to_check > 0:
            print(f"   Max Destinations to Check: {max_destinations_to_check}")
        else:
            print(f"   Max Destinations to Check: All available")
    print()
    
    # Find matching destinations
    print("🔎 Searching for matching flights...")
    print()
    results = destination_finder.find_meeting_destinations(
        origin1=origin1,
        origin2=origin2,
        departure_date=departure_date,
        return_date=return_date,
        max_price=max_price,
        max_stops_person1=max_stops_person1,
        max_stops_person2=max_stops_person2,
        arrival_tolerance_hours=arrival_tolerance,
        min_departure_time_outbound=min_departure_time_outbound,
        min_departure_time_return=min_departure_time_return,
        use_dynamic_destinations=use_dynamic_destinations,
        max_flight_duration_hours_person1=max_flight_duration_person1,
        max_flight_duration_hours_person2=max_flight_duration_person2,
        nearby_airports_radius_km=nearby_airports_radius_km,
        return_airport_radius_km=return_airport_radius_km,
        max_destinations=max_destinations_to_check,
        destinations_to_check=destinations_to_check,
        flight_type=flight_type
    )
    
    # Output results
    print()
    print("=" * 100)
    print(f"📋 RESULTS: Found {len(results)} matching flight option(s)")
    print("=" * 100)
    
    if 'console' in output_format:
        OutputFormatter.print_console(results)
    
    if 'csv' in output_format:
        OutputFormatter.export_csv(results, csv_file)
        # Also export HTML with top N destinations (configurable)
        OutputFormatter.export_html(results, html_file, top_destinations=html_top_destinations, booking_link_provider=booking_link_provider)
    
    print(f"\n✨ Search completed!")


if __name__ == '__main__':
    main()

