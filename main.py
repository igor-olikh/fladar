#!/usr/bin/env python3
"""
Flight Search Application
Finds destinations where two people can meet with matching flight arrivals
"""
import yaml
import os
import sys
from typing import Optional
from flight_search import FlightSearch
from destination_finder import DestinationFinder
from output_formatter import OutputFormatter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    
    departure_date = search_config['outbound_date']
    return_date = search_config['return_date']
    max_price = float(search_config['max_price'])
    max_stops = search_config.get('max_stops', 0)
    arrival_tolerance = search_config.get('arrival_tolerance_hours', 3)
    min_departure_time_outbound = search_config.get('min_departure_time_outbound') or None
    min_departure_time_return = search_config.get('min_departure_time_return') or None
    use_dynamic_destinations = search_config.get('use_dynamic_destinations', True)
    max_flight_duration = float(search_config.get('max_flight_duration_hours', 0))
    
    # Initialize flight search
    try:
        environment = api_config.get('environment', 'test')
        flight_search = FlightSearch(
            api_key=api_config['amadeus_api_key'],
            api_secret=api_config['amadeus_api_secret'],
            environment=environment
        )
    except Exception as e:
        logger.error(f"Failed to initialize flight search: {e}")
        sys.exit(1)
    
    # Initialize destination finder
    destination_finder = DestinationFinder(flight_search)
    
    # Display search parameters
    print(f"\n🔍 Search Parameters:")
    print(f"   Person 1 Origin: {origin1} (Tel Aviv)")
    print(f"   Person 2 Origin: {origin2} (Alicante)")
    print(f"   Outbound Date: {departure_date}")
    print(f"   Return Date: {return_date}")
    print(f"   Max Price (per person): {max_price} EUR")
    print(f"   Max Stops: {max_stops}")
    print(f"   Arrival Tolerance: ±{arrival_tolerance} hours")
    if max_flight_duration > 0:
        print(f"   Max Flight Duration: {max_flight_duration} hours")
    print(f"   Destination Discovery: {'Dynamic (Amadeus API)' if use_dynamic_destinations else 'Predefined List'}")
    if min_departure_time_outbound:
        print(f"   Min Departure Time (Outbound): {min_departure_time_outbound}")
    if min_departure_time_return:
        print(f"   Min Departure Time (Return): {min_departure_time_return}")
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
        max_stops=max_stops,
        arrival_tolerance_hours=arrival_tolerance,
        min_departure_time_outbound=min_departure_time_outbound,
        min_departure_time_return=min_departure_time_return,
        use_dynamic_destinations=use_dynamic_destinations,
        max_flight_duration_hours=max_flight_duration
    )
    
    # Output results
    output_format = output_config.get('format', 'console')
    
    print()
    print("=" * 100)
    print(f"📋 RESULTS: Found {len(results)} matching flight option(s)")
    print("=" * 100)
    
    if 'console' in output_format:
        OutputFormatter.print_console(results)
    
    if 'csv' in output_format:
        csv_file = output_config.get('csv_file', 'flight_results.csv')
        OutputFormatter.export_csv(results, csv_file)
    
    print(f"\n✨ Search completed!")


if __name__ == '__main__':
    main()

