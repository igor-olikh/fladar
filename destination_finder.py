"""
Module to find destinations where both people can meet
"""
from typing import List, Dict, Optional, Set
from flight_search import FlightSearch, format_airport_code, resolve_airport_code
import logging

logger = logging.getLogger(__name__)

# Load airports database for country filtering
try:
    import airportsdata
    airports_db = airportsdata.load('IATA')
except Exception as e:
    logger.warning(f"Could not load airports database for country filtering: {e}")
    airports_db = None


def get_airport_country(airport_code: str) -> Optional[str]:
    """
    Get country code for an airport using airportsdata library
    
    Args:
        airport_code: IATA airport code
    
    Returns:
        ISO country code (e.g., 'ES', 'IL') or None if not found
    """
    if airports_db is None:
        return None
    
    try:
        airport_info = airports_db.get(airport_code.upper())
        if airport_info and 'country' in airport_info:
            return airport_info['country']
    except (KeyError, AttributeError, TypeError):
        pass
    
    return None


def is_valid_airport(airport_code: str) -> bool:
    """
    Check if an airport code is a valid airport (not a railway station or invalid code)
    
    Args:
        airport_code: IATA code to check
    
    Returns:
        True if it's a valid airport, False otherwise
    """
    if airports_db is None:
        # If we can't check, assume it's valid (fail open)
        return True
    
    code_upper = airport_code.upper()
    
    # Check if it's in the airports database
    try:
        airport_info = airports_db.get(code_upper)
        if airport_info:
            # Check if it has airport type information
            # Railway stations typically don't have proper airport data
            airport_type = airport_info.get('type', '').lower()
            if 'railway' in airport_type or 'station' in airport_type:
                return False
            return True
    except (KeyError, AttributeError, TypeError):
        pass
    
    # If not in database, check if it's in aliases (railway stations are mapped)
    from flight_search import _load_airport_aliases
    aliases = _load_airport_aliases()
    if code_upper in aliases:
        # It's a railway station/non-airport code, but we have an alias
        # The resolved airport will be checked separately
        return False
    
    # If not in database and not in aliases, it might be invalid
    # But we'll be lenient and let it through (Flight Offers Search will validate)
    return True


class DestinationFinder:
    """Finds suitable destinations where both people can meet"""
    
    def __init__(self, flight_search: FlightSearch):
        self.flight_search = flight_search
    
    def find_meeting_destinations(
        self,
        origin1: str,
        origin2: str,
        departure_date: str,
        return_date: str,
        max_price: float,
        max_stops_person1: int = 0,
        max_stops_person2: int = 0,
        arrival_tolerance_hours: int = 3,
        min_departure_time_outbound: str = None,
        min_departure_time_return: str = None,
        max_destinations: int = 50,
        use_dynamic_destinations: bool = True,
        max_flight_duration_hours: float = 0,
        nearby_airports_radius_km: int = 0,
        destinations_to_check: List[str] = None
    ) -> List[Dict]:
        """
        Find destinations where both people can meet with matching flights
        
        Args:
            origin1: IATA code for person 1's origin
            origin2: IATA code for person 2's origin
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)
            max_price: Maximum total price for both flights
            max_stops_person1: Maximum number of stops for Person 1 flights
            max_stops_person2: Maximum number of stops for Person 2 flights
            arrival_tolerance_hours: Hours tolerance for arrival times
            min_departure_time_outbound: Minimum departure time for outbound flights (HH:MM)
            min_departure_time_return: Minimum departure time for return flights (HH:MM)
                This checks when the return flight departs FROM the destination (not arrival at origin)
            max_destinations: Maximum number of destinations to check
            use_dynamic_destinations: Use Amadeus API to discover destinations dynamically
            max_flight_duration_hours: Maximum flight duration in hours (0 = no limit)
            nearby_airports_radius_km: Search radius for nearby airports (km)
            destinations_to_check: Optional list of specific destinations to check (skips discovery if provided)
        
        Returns:
            List of matching flight pairs for different destinations
        """
        # If specific destinations are provided, use only those (skip discovery)
        if destinations_to_check and len(destinations_to_check) > 0:
            # Normalize destination codes (uppercase, strip whitespace)
            destinations_to_check = [dest.upper().strip() for dest in destinations_to_check if dest.strip()]
            
            # Filter out invalid airports (railway stations, non-airport codes)
            # Note: We don't filter by country - destinations in same country as origins are allowed
            # (e.g., Alicante to Madrid is valid even though both are in Spain)
            filtered_destinations = []
            for dest in destinations_to_check:
                # Resolve railway stations to airports
                dest_resolved = resolve_airport_code(dest)
                
                # Check if it's a valid airport (not a railway station or invalid code)
                if not is_valid_airport(dest_resolved):
                    logger.debug(f"   Filtering out invalid airport code: {format_airport_code(dest)}")
                    continue
                
                filtered_destinations.append(dest_resolved)
            
            if len(filtered_destinations) < len(destinations_to_check):
                filtered_out = len(destinations_to_check) - len(filtered_destinations)
                logger.info(f"   Filtered out {filtered_out} destination(s) (invalid airports/non-airport codes)")
            
            destinations_to_check = filtered_destinations
            
            if destinations_to_check:
                logger.info(f"📋 Using specified destinations (skipping discovery)")
                logger.info(f"   Will check only these {len(destinations_to_check)} destination(s): {', '.join([format_airport_code(d) for d in destinations_to_check])}")
                logger.info(f"   Flight Offers Search will validate which destinations are actually reachable from both origins")
                logger.info(f"")
            else:
                logger.warning(f"⚠️  All specified destinations were filtered out (invalid airports/non-airport codes)")
                logger.warning(f"   Falling back to normal destination discovery")
                # Set to empty list to trigger normal discovery
                destinations_to_check = []
        
        # If destinations_to_check is empty (either not provided or all filtered out), use normal discovery
        if not destinations_to_check:
            # Get common destinations from both origins
            # Note: Inspiration Search is optional - Flight Offers Search will validate actual availability
            # For destination discovery, use the more restrictive max_stops (if either person wants direct, search for direct)
            max_stops_for_discovery = min(max_stops_person1, max_stops_person2)
            if use_dynamic_destinations:
                logger.info("📋 Using dynamic destination discovery (Inspiration Search API)")
                logger.info("   Note: Inspiration Search uses cached data and may be incomplete")
                logger.info("   Flight Offers Search will validate which destinations are actually reachable")
                destinations = self.flight_search.get_common_destinations(
                    origin1, origin2, departure_date, 
                    use_dynamic=True, 
                    max_duration_hours=max_flight_duration_hours,
                    non_stop=(max_stops_for_discovery == 0)
                )
            else:
                # Use predefined list (more reliable, especially in test environment)
                logger.info("📋 Using predefined destination list")
                logger.info("   This is more reliable than Inspiration Search, especially in test environment")
                logger.info("   Flight Offers Search will validate which destinations are actually reachable")
                destinations = self.flight_search.get_destination_suggestions(
                    origin1, departure_date, 
                    use_dynamic=False, 
                    max_duration_hours=max_flight_duration_hours,
                    non_stop=(max_stops_for_discovery == 0)
                )
            
            # Filter destinations: remove invalid airports (railway stations, non-airport codes)
            # Note: We don't filter by country - destinations in same country as origins are allowed
            # (e.g., Alicante to Madrid is valid even though both are in Spain)
            # The Flight Offers Search API will validate if flights exist from both origins
            filtered_destinations = []
            filtered_count = 0
            for dest in destinations:
                # Resolve railway stations to airports
                dest_resolved = resolve_airport_code(dest)
                
                # Check if it's a valid airport (not a railway station or invalid code)
                if not is_valid_airport(dest_resolved):
                    filtered_count += 1
                    logger.debug(f"   Filtering out invalid airport code: {format_airport_code(dest)}")
                    continue
                
                filtered_destinations.append(dest_resolved)
            
            if filtered_count > 0:
                logger.info(f"   Filtered out {filtered_count} destination(s) (invalid airports/non-airport codes)")
            
            # Limit destinations to check
            if max_destinations > 0:
                destinations_to_check = filtered_destinations[:max_destinations]
                logger.info(f"")
                logger.info(f"🎯 Will search {len(destinations_to_check)} destination(s) (out of {len(filtered_destinations)} valid destinations)")
                logger.info(f"   Limiting to {max_destinations} destinations to manage API usage")
                logger.info(f"")
            else:
                destinations_to_check = filtered_destinations
                logger.info(f"")
                logger.info(f"🎯 Will search all {len(destinations_to_check)} valid destination(s)")
                logger.info(f"   No limit set - checking all destinations (this may take longer)")
                logger.info(f"")
        
        all_matches = []
        destinations_with_matches = 0
        
        for i, destination in enumerate(destinations_to_check, 1):
            logger.info(f"")
            logger.info(f"[{i}/{len(destinations_to_check)}] Processing destination: {format_airport_code(destination)}")
            logger.info(f"{'='*80}")
            
            try:
                matches = self.flight_search.find_matching_flights(
                    origin1=origin1,
                    origin2=origin2,
                    destination=destination,
                    departure_date=departure_date,
                    return_date=return_date,
                    max_price=max_price,
                    max_stops_person1=max_stops_person1,
                    max_stops_person2=max_stops_person2,
                    arrival_tolerance_hours=arrival_tolerance_hours,
                    min_departure_time_outbound=min_departure_time_outbound,
                    min_departure_time_return=min_departure_time_return,
                    nearby_airports_radius_km=nearby_airports_radius_km,
                    max_duration_hours=max_flight_duration_hours
                )
                
                if matches:
                    destinations_with_matches += 1
                    logger.info(f"   ✓ {format_airport_code(destination)}: Found {len(matches)} matching flight pair(s)")
                    all_matches.extend(matches)
                else:
                    logger.info(f"   ✗ {format_airport_code(destination)}: No matching flights found")
                    
            except Exception as e:
                logger.error(f"   ❌ Error while searching destination {format_airport_code(destination)}: {e}")
                logger.error(f"      Continuing with next destination...")
                continue
        
        # Deduplicate matches - same flight pair might appear multiple times
        # Create a unique key for each flight pair based on flight details
        seen_pairs = set()
        deduplicated_matches = []
        
        for match in all_matches:
            # Create a unique identifier for this flight pair
            p1_flight = match.get('person1_flight', {})
            p2_flight = match.get('person2_flight', {})
            
            # Extract key identifiers from flights
            # Use first segment departure/arrival times and airlines as unique key
            try:
                p1_outbound = p1_flight.get('itineraries', [{}])[0]
                p1_outbound_segments = p1_outbound.get('segments', [])
                p1_outbound_dep = p1_outbound_segments[0].get('departure', {}).get('at', '') if p1_outbound_segments else ''
                p1_outbound_arr = p1_outbound_segments[-1].get('arrival', {}).get('at', '') if p1_outbound_segments else ''
                p1_airlines = ','.join(sorted(set(seg.get('carrierCode', '') for seg in p1_outbound_segments)))
                
                p2_outbound = p2_flight.get('itineraries', [{}])[0]
                p2_outbound_segments = p2_outbound.get('segments', [])
                p2_outbound_dep = p2_outbound_segments[0].get('departure', {}).get('at', '') if p2_outbound_segments else ''
                p2_outbound_arr = p2_outbound_segments[-1].get('arrival', {}).get('at', '') if p2_outbound_segments else ''
                p2_airlines = ','.join(sorted(set(seg.get('carrierCode', '') for seg in p2_outbound_segments)))
                
                # Create unique key: destination + both flights' key details
                unique_key = (
                    match.get('destination', ''),
                    p1_outbound_dep,
                    p1_outbound_arr,
                    p1_airlines,
                    p2_outbound_dep,
                    p2_outbound_arr,
                    p2_airlines,
                    match.get('person1_price', 0),
                    match.get('person2_price', 0)
                )
                
                if unique_key not in seen_pairs:
                    seen_pairs.add(unique_key)
                    deduplicated_matches.append(match)
                else:
                    logger.debug(f"   Skipping duplicate flight pair: {match.get('destination')} - Person 1: {p1_outbound_dep}, Person 2: {p2_outbound_dep}")
            except Exception as e:
                # If we can't create a unique key, include the match anyway (fail open)
                logger.debug(f"   Error creating unique key for match: {e}, including anyway")
                deduplicated_matches.append(match)
        
        duplicates_removed = len(all_matches) - len(deduplicated_matches)
        if duplicates_removed > 0:
            logger.info(f"   Removed {duplicates_removed} duplicate flight pair(s)")
        
        # Sort all matches by total price
        deduplicated_matches.sort(key=lambda x: x['total_price'])
        
        logger.info(f"")
        logger.info(f"📊 Search Summary:")
        logger.info(f"   Destinations checked: {len(destinations_to_check)}")
        logger.info(f"   Destinations with matches: {destinations_with_matches}")
        logger.info(f"   Total matching flight pairs found: {len(all_matches)}")
        if duplicates_removed > 0:
            logger.info(f"   Duplicates removed: {duplicates_removed}")
        logger.info(f"   Unique flight pairs: {len(deduplicated_matches)}")
        
        return deduplicated_matches

