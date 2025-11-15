"""
Module to find destinations where both people can meet
"""
from typing import List, Dict
from flight_search import FlightSearch, format_airport_code
import logging

logger = logging.getLogger(__name__)


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
        nearby_airports_radius_km: int = 0
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
        
        Returns:
            List of matching flight pairs for different destinations
        """
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
        
        # Limit destinations to check
        if max_destinations > 0:
            destinations_to_check = destinations[:max_destinations]
            logger.info(f"")
            logger.info(f"🎯 Will search {len(destinations_to_check)} destination(s) (out of {len(destinations)} available)")
            logger.info(f"   Limiting to {max_destinations} destinations to manage API usage")
            logger.info(f"")
        else:
            destinations_to_check = destinations
            logger.info(f"")
            logger.info(f"🎯 Will search all {len(destinations_to_check)} available destination(s)")
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

