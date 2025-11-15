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
        max_stops: int = 0,
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
            max_stops: Maximum number of stops
            arrival_tolerance_hours: Hours tolerance for arrival times
            min_departure_time_outbound: Minimum departure time for outbound flights (HH:MM)
            min_departure_time_return: Minimum departure time for return flights (HH:MM)
            max_destinations: Maximum number of destinations to check
            use_dynamic_destinations: Use Amadeus API to discover destinations dynamically
            max_flight_duration_hours: Maximum flight duration in hours (0 = no limit)
        
        Returns:
            List of matching flight pairs for different destinations
        """
        # Get common destinations from both origins
        # Note: Inspiration Search is optional - Flight Offers Search will validate actual availability
        if use_dynamic_destinations:
            logger.info("📋 Using dynamic destination discovery (Inspiration Search API)")
            logger.info("   Note: Inspiration Search uses cached data and may be incomplete")
            logger.info("   Flight Offers Search will validate which destinations are actually reachable")
            destinations = self.flight_search.get_common_destinations(
                origin1, origin2, departure_date, 
                use_dynamic=True, 
                max_duration_hours=max_flight_duration_hours,
                non_stop=(max_stops == 0)
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
                non_stop=(max_stops == 0)
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
                    max_stops=max_stops,
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
        
        # Sort all matches by total price
        all_matches.sort(key=lambda x: x['total_price'])
        
        logger.info(f"")
        logger.info(f"📊 Search Summary:")
        logger.info(f"   Destinations checked: {len(destinations_to_check)}")
        logger.info(f"   Destinations with matches: {destinations_with_matches}")
        logger.info(f"   Total matching flight pairs found: {len(all_matches)}")
        
        return all_matches

