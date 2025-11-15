"""
Flight search module using Amadeus API
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from amadeus import Client, ResponseError
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Airport code to city name mapping - loaded from external file
_AIRPORT_NAMES = None

# Airport aliases mapping (non-airport codes -> nearest airport codes) - loaded from external file
_AIRPORT_ALIASES = None


def _load_airport_names():
    """Load airport names from external JSON file"""
    global _AIRPORT_NAMES
    if _AIRPORT_NAMES is not None:
        return _AIRPORT_NAMES
    
    # Try to load from data/airport_names.json
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Data folder is in the same directory as this file
    airport_names_file = os.path.join(current_dir, 'data', 'airport_names.json')
    
    # If not found, try relative to project root (if running from project root)
    if not os.path.exists(airport_names_file):
        airport_names_file = os.path.join(current_dir, '..', 'data', 'airport_names.json')
        airport_names_file = os.path.normpath(airport_names_file)
    
    try:
        if os.path.exists(airport_names_file):
            with open(airport_names_file, 'r', encoding='utf-8') as f:
                _AIRPORT_NAMES = json.load(f)
                logger.debug(f"Loaded {len(_AIRPORT_NAMES)} airport names from {airport_names_file}")
        else:
            logger.warning(f"Airport names file not found: {airport_names_file}, using empty mapping")
            _AIRPORT_NAMES = {}
    except Exception as e:
        logger.warning(f"Error loading airport names from {airport_names_file}: {e}, using empty mapping")
        _AIRPORT_NAMES = {}
    
    return _AIRPORT_NAMES


def format_airport_code(code: str) -> str:
    """Format airport code with city name in brackets if known"""
    airport_names = _load_airport_names()
    code_upper = code.upper()
    city_name = airport_names.get(code_upper)
    if city_name:
        return f"{code} ({city_name})"
    return code


def _load_airport_aliases():
    """Load airport aliases from external JSON file (maps non-airport codes to nearest airports)"""
    global _AIRPORT_ALIASES
    if _AIRPORT_ALIASES is not None:
        return _AIRPORT_ALIASES
    
    # Try to load from data/destinations_cache/airport_aliases.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    aliases_file = os.path.join(current_dir, 'data', 'destinations_cache', 'airport_aliases.json')
    
    # If not found, try relative to project root
    if not os.path.exists(aliases_file):
        aliases_file = os.path.join(current_dir, '..', 'data', 'destinations_cache', 'airport_aliases.json')
        aliases_file = os.path.normpath(aliases_file)
    
    try:
        if os.path.exists(aliases_file):
            with open(aliases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Remove comment keys
                _AIRPORT_ALIASES = {k: v for k, v in data.items() if not k.startswith('_')}
                logger.debug(f"Loaded {len(_AIRPORT_ALIASES)} airport aliases from {aliases_file}")
        else:
            logger.debug(f"Airport aliases file not found: {aliases_file}, using empty mapping")
            _AIRPORT_ALIASES = {}
    except Exception as e:
        logger.warning(f"Error loading airport aliases from {aliases_file}: {e}, using empty mapping")
        _AIRPORT_ALIASES = {}
    
    return _AIRPORT_ALIASES


def resolve_airport_code(code: str) -> str:
    """
    Resolve airport code - if it's a non-airport code (like railway station),
    return the nearest airport code from the aliases mapping.
    
    Args:
        code: Airport code or non-airport code (e.g., XTI for railway station)
    
    Returns:
        Actual airport code to use for flight search
    """
    aliases = _load_airport_aliases()
    code_upper = code.upper()
    
    # Check if this code has an alias (non-airport -> airport mapping)
    if code_upper in aliases:
        airport_code = aliases[code_upper]
        logger.debug(f"Resolved non-airport code {code_upper} to airport {airport_code}")
        return airport_code
    
    # No alias found, return original code (assume it's already an airport code)
    return code_upper


class FlightSearch:
    """Handles flight searches using Amadeus API"""
    
    def __init__(self, api_key: str, api_secret: str, environment: str = "test", cache_expiration_days: int = 30, use_flight_cache: bool = True):
        """
        Initialize Amadeus client
        
        Args:
            api_key: Amadeus API key
            api_secret: Amadeus API secret
            environment: "test" or "production" - determines which API host to use
            cache_expiration_days: Number of days before cached destination data expires
            use_flight_cache: Whether to cache flight search results (default: True)
        """
        # Set hostname based on environment (SDK accepts "test" or "production")
        # Handle "live" as an alias for "production"
        if environment == "test":
            hostname = "test"
            logger.info(f"Using Amadeus TEST environment (test.api.amadeus.com)")
        elif environment in ["production", "live"]:
            # Both "production" and "live" use the production API
            hostname = "production"
            logger.info(f"Using Amadeus PRODUCTION environment (api.amadeus.com)")
            if environment == "live":
                logger.info(f"Note: 'live' is treated as 'production' environment")
        else:
            logger.warning(f"Unknown environment '{environment}', defaulting to test")
            hostname = "test"
        
        self.amadeus = Client(
            client_id=api_key,
            client_secret=api_secret,
            hostname=hostname
        )
        
        # Store environment for later checks
        self.environment = environment
        self.hostname = hostname
        self.cache_expiration_days = cache_expiration_days
        self.use_flight_cache = use_flight_cache
        
        # Verify credentials are set
        if not api_key or not api_secret:
            raise ValueError("Amadeus API key and secret must be provided")
        
        # Pre-authenticate by making a simple call to ensure token is obtained
        # This ensures the client is authenticated before any API calls
        # The SDK handles authentication automatically, but we trigger it explicitly
        try:
            # Make a minimal authenticated call to trigger token acquisition
            # We use flight_offers_search as it's a reliable endpoint that requires auth
            # This ensures the access token is obtained and cached
            _ = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode='TLV',
                destinationLocationCode='PAR',
                departureDate='2025-11-20',
                adults=1,
                max=1
            )
            logger.debug("Pre-authentication successful - access token obtained")
        except Exception as e:
            # Even if this fails, it should have triggered authentication
            # The SDK will cache the token for subsequent calls
            logger.debug(f"Pre-authentication call completed: {type(e).__name__}")
            # Don't raise - authentication might still work for other endpoints
    
    def get_nearby_airports(self, airport_code: str, radius_km: int = 200) -> List[str]:
        """
        Get nearby airports within a specified radius using Amadeus Airport Nearest Relevant API
        
        Args:
            airport_code: IATA code of the origin airport
            radius_km: Search radius in kilometers (default: 200)
            
        Returns:
            List of IATA codes for nearby airports (including the original airport)
        """
        if radius_km <= 0:
            return [airport_code.upper()]
        
        nearby_airports = [airport_code.upper()]  # Always include the original airport
        
        try:
            logger.debug(f"Searching for airports within {radius_km} km of {airport_code}")
            
            # Use Amadeus Airport Nearest Relevant API
            # This API finds airports within a radius of a given location
            response = self.amadeus.reference_data.locations.airports.get(
                latitude=0,  # Will be determined from airport code
                longitude=0,  # Will be determined from airport code
                radius=radius_km
            )
            
            # Actually, the Airport Nearest Relevant API requires lat/lon, not airport code
            # We need to get coordinates first, or use a different approach
            # Let's use airportsdata to get coordinates, then use Amadeus API
            
            import airportsdata
            try:
                airports_db = airportsdata.load('IATA')
                airport_info = airports_db.get(airport_code.upper())
                
                if airport_info and 'lat' in airport_info and 'lon' in airport_info:
                    lat = airport_info['lat']
                    lon = airport_info['lon']
                    
                    logger.debug(f"Found coordinates for {format_airport_code(airport_code)}: {lat}, {lon}")
                    
                    # Now use Amadeus API to find nearby airports
                    response = self.amadeus.reference_data.locations.airports.get(
                        latitude=lat,
                        longitude=lon,
                        radius=radius_km
                    )
                    
                    if response.data:
                        for airport in response.data:
                            iata_code = airport.get('iataCode')
                            if iata_code and iata_code.upper() != airport_code.upper():
                                nearby_airports.append(iata_code.upper())
                        
                        logger.info(f"  → Found {len(nearby_airports)} airport(s) within {radius_km} km of {format_airport_code(airport_code)}: {', '.join([format_airport_code(ap) for ap in nearby_airports])}")
                    else:
                        logger.debug(f"  → No nearby airports found via API, using only {format_airport_code(airport_code)}")
                else:
                    logger.debug(f"  → Could not get coordinates for {format_airport_code(airport_code)}, using only specified airport")
            except Exception as e:
                logger.debug(f"  → Error getting coordinates: {e}, using only {format_airport_code(airport_code)}")
                
        except ResponseError as error:
            logger.debug(f"  → Airport Nearest Relevant API error: {error}, using only {format_airport_code(airport_code)}")
        except Exception as e:
            logger.debug(f"  → Error finding nearby airports: {e}, using only {format_airport_code(airport_code)}")
        
        return nearby_airports
    
    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """
        Parse ISO 8601 duration string (e.g., 'PT19H50M') to hours as float
        
        Args:
            duration_str: ISO 8601 duration string like 'PT19H50M' or 'PT2H30M'
            
        Returns:
            Duration in hours as float, or 0 if parsing fails
        """
        if not duration_str or not isinstance(duration_str, str):
            return 0.0
        
        try:
            # Remove 'PT' prefix if present
            duration = duration_str.replace('PT', '')
            
            hours = 0.0
            minutes = 0.0
            
            # Extract hours
            if 'H' in duration:
                hours_str = duration.split('H')[0]
                hours = float(hours_str)
                duration = duration.split('H', 1)[1]
            
            # Extract minutes
            if 'M' in duration:
                minutes_str = duration.split('M')[0]
                minutes = float(minutes_str)
            
            # Convert to total hours
            total_hours = hours + (minutes / 60.0)
            return total_hours
        except Exception as e:
            logger.debug(f"Error parsing duration '{duration_str}': {e}")
            return 0.0
    
    def _filter_by_duration(self, flights: List[Dict], max_duration_hours: float, flight_type: str = "both") -> List[Dict]:
        """
        Filter flights by maximum duration
        
        Args:
            flights: List of flight offers
            max_duration_hours: Maximum duration in hours (0 = no limit)
            flight_type: "both" (round trip), "outbound" (one-way), or "return" (one-way)
            
        Returns:
            Filtered list of flights
        """
        if max_duration_hours <= 0:
            return flights
        
        filtered = []
        is_round_trip = flight_type == "both"
        
        for flight in flights:
            try:
                itineraries = flight.get('itineraries', [])
                
                if is_round_trip:
                    # Round-trip: need both outbound and return
                    if len(itineraries) < 2:
                        continue
                    
                    outbound_duration_str = itineraries[0].get('duration', '')
                    return_duration_str = itineraries[1].get('duration', '')
                    
                    outbound_hours = self._parse_duration_to_hours(outbound_duration_str)
                    return_hours = self._parse_duration_to_hours(return_duration_str)
                    
                    # Check if both outbound and return are within limit
                    if outbound_hours <= max_duration_hours and return_hours <= max_duration_hours:
                        filtered.append(flight)
                    else:
                        logger.debug(f"  → Filtered out flight: outbound={outbound_hours:.1f}h, return={return_hours:.1f}h (max={max_duration_hours}h)")
                else:
                    # One-way: only check the single itinerary
                    if len(itineraries) < 1:
                        continue
                    
                    duration_str = itineraries[0].get('duration', '')
                    duration_hours = self._parse_duration_to_hours(duration_str)
                    
                    # Check if duration is within limit
                    if duration_hours <= max_duration_hours:
                        filtered.append(flight)
                    else:
                        logger.debug(f"  → Filtered out flight: duration={duration_hours:.1f}h (max={max_duration_hours}h)")
            except Exception as e:
                logger.debug(f"  → Error checking duration for flight: {e}")
                # If we can't check duration, include the flight (fail open)
                filtered.append(flight)
        
        return filtered
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        max_stops: int = 0,
        min_departure_time_outbound: Optional[str] = None,
        min_departure_time_return: Optional[str] = None,
        nearby_airports_radius_km: int = 0,
        max_duration_hours: float = 0,
        flight_type: str = "both"
    ) -> List[Dict]:
        """
        Search for flights (round-trip or one-way)
        
        Args:
            origin: IATA code of origin airport
            destination: IATA code of destination airport
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD) - Required for "both" or "return", ignored for "outbound"
            max_stops: Maximum number of stops
            min_departure_time_outbound: Minimum departure time for outbound flights (HH:MM)
            min_departure_time_return: Minimum departure time for return flights (HH:MM)
                This checks when the return flight departs FROM the destination (not arrival at origin)
            nearby_airports_radius_km: Search radius in km for nearby airports (0 = disabled)
            max_duration_hours: Maximum flight duration in hours (0 = no limit)
            flight_type: "both" (round trip), "outbound" (one-way to destination), or "return" (one-way from destination)
        
        Returns:
            List of flight offers
        """
        # Resolve non-airport codes (like railway stations) to nearest airports
        origin_resolved = resolve_airport_code(origin)
        destination_resolved = resolve_airport_code(destination)
        
        # Log if resolution happened
        if origin_resolved != origin.upper():
            logger.info(f"  → Resolved origin {format_airport_code(origin)} to airport {format_airport_code(origin_resolved)}")
        if destination_resolved != destination.upper():
            logger.info(f"  → Resolved destination {format_airport_code(destination)} to airport {format_airport_code(destination_resolved)}")
        
        # Determine if this is a round-trip or one-way search
        is_round_trip = flight_type == "both"
        is_return_only = flight_type == "return"
        
        if is_round_trip:
            if not return_date:
                raise ValueError("return_date is required for round-trip flights (flight_type='both')")
            logger.debug(f"Searching round-trip flights: {format_airport_code(origin_resolved)} → {format_airport_code(destination_resolved)} ({departure_date} to {return_date})")
        elif is_return_only:
            if not return_date:
                raise ValueError("return_date is required for return flights (flight_type='return')")
            logger.debug(f"Searching return flights: {format_airport_code(destination_resolved)} → {format_airport_code(origin_resolved)} ({return_date})")
        else:  # outbound
            logger.debug(f"Searching outbound flights: {format_airport_code(origin_resolved)} → {format_airport_code(destination_resolved)} ({departure_date})")
        
        # Use resolved codes for search
        origin = origin_resolved
        destination = destination_resolved
        
        # For return flights, swap origin and destination (we're searching FROM destination TO origin)
        if is_return_only:
            search_origin = destination
            search_destination = origin
            search_date = return_date
        else:
            search_origin = origin
            search_destination = destination
            search_date = departure_date
        
        # Check cache first (before any API calls)
        cache_return_date = return_date if is_round_trip else None
        cached_flights = self._get_cached_flights(
            origin=search_origin,
            destination=search_destination,
            departure_date=search_date,
            return_date=cache_return_date,
            max_stops=max_stops,
            nearby_airports_radius_km=nearby_airports_radius_km,
            max_duration_hours=max_duration_hours,
            flight_type=flight_type
        )
        
        if cached_flights is not None:
            # Return cached results (they're already filtered)
            return cached_flights
        
        # Get nearby airports if radius is specified
        origins_to_search = [search_origin.upper()]
        if nearby_airports_radius_km > 0:
            nearby_airports = self.get_nearby_airports(search_origin, nearby_airports_radius_km)
            origins_to_search = nearby_airports
            logger.info(f"  → Searching from {len(origins_to_search)} airport(s): {', '.join(origins_to_search)}")
        
        all_flights = []
        
        for airport_origin in origins_to_search:
            try:
                # Build API parameters
                api_params = {
                    'originLocationCode': airport_origin,
                    'destinationLocationCode': search_destination,
                    'departureDate': search_date,
                    'adults': 1,
                    'max': 250  # Maximum results
                }
                
                # Only include returnDate for round-trip flights
                if is_round_trip:
                    api_params['returnDate'] = return_date
                
                # Search for flight offers
                logger.debug(f"Calling Amadeus API for {format_airport_code(airport_origin)} → {format_airport_code(search_destination)} (flight_type={flight_type})")
                response = self.amadeus.shopping.flight_offers_search.get(**api_params)
            
                flights = response.data if response.data else []
                logger.info(f"  → Amadeus API returned {len(flights)} flight(s) for {format_airport_code(airport_origin)} → {format_airport_code(search_destination)}")
                
                # Add origin information to each flight for tracking
                for flight in flights:
                    flight['_search_origin'] = airport_origin
                    flight['_flight_type'] = flight_type  # Store flight type for later processing
                
                all_flights.extend(flights)
                
            except ResponseError as error:
                logger.debug(f"  → API error for {format_airport_code(airport_origin)} → {format_airport_code(search_destination)}: {error}")
                continue
            except Exception as e:
                logger.debug(f"  → Error searching {format_airport_code(airport_origin)} → {format_airport_code(search_destination)}: {e}")
                continue
        
        flights = all_flights
        logger.info(f"  → Total flights found from all airports: {len(flights)} for {format_airport_code(search_origin)} → {format_airport_code(search_destination)}")
        
        if not flights:
            # If no flights found, return empty list
            return []
        
        try:
            initial_count = len(flights)
            
            # Filter by stops
            if max_stops == 0:
                flights_before = len(flights)
                flights = [f for f in flights if self._is_direct_flight(f)]
                if len(flights) < flights_before:
                    logger.debug(f"  → Filtered to {len(flights)} direct flight(s) (removed {flights_before - len(flights)} with stops)")
            else:
                flights_before = len(flights)
                flights = [f for f in flights if self._get_stops(f) <= max_stops]
                if len(flights) < flights_before:
                    logger.debug(f"  → Filtered to {len(flights)} flight(s) with ≤{max_stops} stop(s) (removed {flights_before - len(flights)})")
            
            # Filter by departure time constraints (separate for outbound and return)
            # For one-way flights, only apply the relevant constraint
            if is_round_trip:
                # Round-trip: check both constraints
                if min_departure_time_outbound or min_departure_time_return:
                    flights_before = len(flights)
                    flights = self._filter_by_departure_times(flights, min_departure_time_outbound, min_departure_time_return)
                    if len(flights) < flights_before:
                        outbound_str = f"outbound ≥ {min_departure_time_outbound}" if min_departure_time_outbound else "outbound: no limit"
                        return_str = f"return ≥ {min_departure_time_return}" if min_departure_time_return else "return: no limit"
                        logger.debug(f"  → Filtered to {len(flights)} flight(s) with {outbound_str}, {return_str} (removed {flights_before - len(flights)})")
            elif is_return_only:
                # Return only: check return constraint (which is actually the outbound of the return flight)
                if min_departure_time_return:
                    flights_before = len(flights)
                    flights = self._filter_by_departure_times(flights, min_departure_time_return, None)
                    if len(flights) < flights_before:
                        logger.debug(f"  → Filtered to {len(flights)} flight(s) with departure ≥ {min_departure_time_return} (removed {flights_before - len(flights)})")
            else:  # outbound only
                # Outbound only: check outbound constraint
                if min_departure_time_outbound:
                    flights_before = len(flights)
                    flights = self._filter_by_departure_times(flights, min_departure_time_outbound, None)
                    if len(flights) < flights_before:
                        logger.debug(f"  → Filtered to {len(flights)} flight(s) with departure ≥ {min_departure_time_outbound} (removed {flights_before - len(flights)})")
            
            # Filter by maximum flight duration
            # For one-way flights, only check the single itinerary
            if max_duration_hours > 0:
                flights_before = len(flights)
                flights = self._filter_by_duration(flights, max_duration_hours, flight_type=flight_type)
                if len(flights) < flights_before:
                    logger.info(f"  → Filtered to {len(flights)} flight(s) with duration ≤ {max_duration_hours}h (removed {flights_before - len(flights)} flights exceeding duration limit)")
            
            logger.info(f"  → Final result: {len(flights)} flight(s) after filtering for {format_airport_code(search_origin)} → {format_airport_code(search_destination)}")
            
            # Save to cache after successful search and filtering
            self._save_cached_flights(
                origin=search_origin,
                destination=search_destination,
                departure_date=search_date,
                return_date=cache_return_date,
                max_stops=max_stops,
                nearby_airports_radius_km=nearby_airports_radius_km,
                max_duration_hours=max_duration_hours,
                flights=flights,
                flight_type=flight_type
            )
            
            return flights
            
        except ResponseError as error:
            # Extract detailed error information
            error_code = error.response.status_code if hasattr(error, 'response') else 'Unknown'
            error_description = error.description() if hasattr(error, 'description') and callable(error.description) else (error.description if hasattr(error, 'description') else str(error))
            error_body = error.response.body if hasattr(error, 'response') and hasattr(error.response, 'body') else None
            
            logger.error(f"  ❌ Amadeus API returned an error for {format_airport_code(origin)} → {format_airport_code(destination)}")
            logger.error(f"     Status Code: {error_code}")
            logger.error(f"     Error: {error_description}")
            if error_body:
                # Try to parse error details if it's JSON
                import json
                try:
                    if isinstance(error_body, str):
                        error_data = json.loads(error_body)
                    else:
                        error_data = error_body
                    if 'errors' in error_data and len(error_data['errors']) > 0:
                        first_error = error_data['errors'][0]
                        logger.error(f"     Error Code: {first_error.get('code', 'N/A')}")
                        logger.error(f"     Title: {first_error.get('title', 'N/A')}")
                        logger.error(f"     Detail: {first_error.get('detail', 'N/A')}")
                except:
                    logger.error(f"     Details: {error_body}")
            logger.error(f"     This is an error response from the Amadeus API service (not a connection issue)")
            return []
        except Exception as e:
            logger.error(f"  ❌ Unexpected error while searching flights {format_airport_code(origin)} → {format_airport_code(destination)}: {e}")
            logger.error(f"     This is a local error (not from Amadeus API)")
            return []
    
    def _is_direct_flight(self, flight_offer: Dict) -> bool:
        """Check if flight is direct (no stops)
        
        A direct flight has exactly 1 segment per itinerary.
        Multiple segments indicate connections (stops).
        """
        for itinerary in flight_offer.get('itineraries', []):
            segments = itinerary.get('segments', [])
            # Direct flight = 1 segment, any more = has stops
            if len(segments) > 1:
                return False
            # Also check if the single segment itself has stops
            if segments and segments[0].get('numberOfStops', 0) > 0:
                return False
        return True
    
    def _get_stops(self, flight_offer: Dict) -> int:
        """Get maximum number of stops in the flight
        
        Stops are calculated as: number of segments - 1
        Example: 2 segments (TLV → VIE → AMS) = 1 stop in VIE
        Direct flight: 1 segment = 0 stops
        """
        max_stops = 0
        for itinerary in flight_offer.get('itineraries', []):
            segments = itinerary.get('segments', [])
            if segments:
                # Count stops: segments - 1 (each connection is a stop)
                itinerary_stops = max(0, len(segments) - 1)
                # Also check if any segment itself has stops (rare case)
                segment_stops = max(seg.get('numberOfStops', 0) for seg in segments)
                # Take the maximum (either connection stops or segment stops)
                max_stops = max(max_stops, itinerary_stops, segment_stops)
        return max_stops
    
    def _filter_by_departure_times(
        self, 
        flights: List[Dict], 
        min_time_outbound: Optional[str] = None,
        min_time_return: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter flights by minimum departure times (separate for outbound and return)
        
        Args:
            flights: List of flight offers
            min_time_outbound: Minimum departure time for outbound flights (HH:MM) or None
                This checks when the flight departs FROM the origin airport
            min_time_return: Minimum departure time for return flights (HH:MM) or None
                This checks when the return flight departs FROM the destination airport
                (NOT when it arrives back at the origin)
        """
        filtered = []
        
        for flight in flights:
            valid = True
            
            # Check outbound departure time (departure FROM origin)
            if min_time_outbound:
                outbound = flight.get('itineraries', [{}])[0]
                if outbound.get('segments'):
                    first_segment = outbound['segments'][0]
                    dep_time = first_segment.get('departure', {}).get('at', '')
                    
                    if dep_time:
                        min_hour, min_minute = map(int, min_time_outbound.split(':'))
                        dep_datetime = datetime.fromisoformat(dep_time.replace('Z', '+00:00'))
                        if not (dep_datetime.hour > min_hour or (dep_datetime.hour == min_hour and dep_datetime.minute >= min_minute)):
                            valid = False
                            logger.debug(f"      Outbound departure {dep_time} is before {min_time_outbound}")
            
            # Check return departure time (departure FROM destination, not arrival at origin)
            # This is when the flight LEAVES the destination airport
            if valid and min_time_return and len(flight.get('itineraries', [])) > 1:
                return_trip = flight.get('itineraries', [{}])[1]
                if return_trip.get('segments'):
                    first_segment = return_trip['segments'][0]
                    dep_time = first_segment.get('departure', {}).get('at', '')
                    
                    if dep_time:
                        min_hour, min_minute = map(int, min_time_return.split(':'))
                        dep_datetime = datetime.fromisoformat(dep_time.replace('Z', '+00:00'))
                        if not (dep_datetime.hour > min_hour or (dep_datetime.hour == min_hour and dep_datetime.minute >= min_minute)):
                            valid = False
                            logger.debug(f"      Return departure FROM destination {dep_time} is before {min_time_return}")
            
            if valid:
                filtered.append(flight)
        
        return filtered
    
    def _filter_by_arrival_time(self, flights: List[Dict], min_time: str) -> List[Dict]:
        """
        Filter flights by minimum arrival time
        Applies to BOTH outbound AND return arrival times
        """
        min_hour, min_minute = map(int, min_time.split(':'))
        filtered = []
        
        for flight in flights:
            valid = True
            
            # Check outbound arrival time
            outbound = flight.get('itineraries', [{}])[0]
            if outbound.get('segments'):
                last_segment = outbound['segments'][-1]
                arr_time = last_segment.get('arrival', {}).get('at', '')
                
                if arr_time:
                    arr_datetime = datetime.fromisoformat(arr_time.replace('Z', '+00:00'))
                    if not (arr_datetime.hour > min_hour or (arr_datetime.hour == min_hour and arr_datetime.minute >= min_minute)):
                        valid = False
                        logger.debug(f"      Outbound arrival {arr_time} is before {min_time}")
            
            # Check return arrival time (if return flight exists)
            if valid and len(flight.get('itineraries', [])) > 1:
                return_trip = flight.get('itineraries', [{}])[1]
                if return_trip.get('segments'):
                    last_segment = return_trip['segments'][-1]
                    arr_time = last_segment.get('arrival', {}).get('at', '')
                    
                    if arr_time:
                        arr_datetime = datetime.fromisoformat(arr_time.replace('Z', '+00:00'))
                        if not (arr_datetime.hour > min_hour or (arr_datetime.hour == min_hour and arr_datetime.minute >= min_minute)):
                            valid = False
                            logger.debug(f"      Return arrival {arr_time} is before {min_time}")
            
            if valid:
                filtered.append(flight)
        
        return filtered
    
    def get_destination_suggestions(
        self, 
        origin: str, 
        departure_date: str,
        use_dynamic: bool = True,
        max_duration_hours: float = 0,
        non_stop: bool = False
    ) -> List[str]:
        """
        Get destination suggestions from an origin
        
        Args:
            origin: IATA code of origin airport
            departure_date: Departure date (YYYY-MM-DD)
            use_dynamic: If True, use Amadeus Flight Inspiration Search API
            max_duration_hours: Maximum flight duration in hours (0 = no limit)
        
        Returns:
            List of destination IATA codes
        """
        logger.info("📋 Determining which destinations to search...")
        
        # Known origins that don't work in test environment
        # TLV (Tel Aviv) and ALC (Alicante) are not reliably in Amadeus test cache
        # According to Amadeus docs, test environment only covers USA, Spain, UK, Germany, India
        # But even Spain (ALC) may not have complete Inspiration Search data
        TEST_ENV_UNSUPPORTED_ORIGINS = ['TLV', 'ALC']
        
        # Check if we're in test environment and origin is known to not work
        # Skip Inspiration Search for known unsupported origins in test environment
        if self.environment == "test" and origin.upper() in TEST_ENV_UNSUPPORTED_ORIGINS:
            logger.warning(f"   ⚠️  Origin {format_airport_code(origin)} is not reliably supported in test environment (not in Amadeus test cache)")
            logger.info(f"   Skipping Inspiration Search and using predefined list directly")
            logger.info(f"   Note: Flight Offers Search will validate which destinations are actually reachable")
            return self._get_predefined_destinations()
        
        if use_dynamic:
            logger.info("   Using Amadeus Flight Inspiration Search API to discover destinations dynamically")
            return self._get_destinations_from_inspiration_search(origin, departure_date, max_duration_hours, non_stop)
        else:
            logger.info("   Using predefined list of popular European destinations")
            return self._get_predefined_destinations()
    
    def _get_cached_destinations(self, origin: str) -> Optional[List[str]]:
        """
        Get cached destinations for an origin airport
        
        Args:
            origin: IATA code of origin airport
            
        Returns:
            List of destination codes if cache exists and is valid, None otherwise
        """
        cache_dir = "data/destinations_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{origin.upper()}_destinations.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cached_date = datetime.fromisoformat(cache_data.get('cached_date', ''))
            days_old = (datetime.now() - cached_date).days
            
            # Cache is valid for the configured number of days (default 30)
            # If cache_expiration_days is 0, caching is disabled
            if self.cache_expiration_days == 0:
                logger.debug(f"   Caching is disabled (cache_expiration_days=0)")
                return None
            
            if days_old < self.cache_expiration_days:
                cached_destinations = cache_data.get('destinations', [])
                # Deduplicate destinations when loading from cache (in case cache file has duplicates)
                unique_destinations = sorted(list(set(dest.upper() for dest in cached_destinations)))
                if len(unique_destinations) < len(cached_destinations):
                    logger.debug(f"   Deduplicated {len(cached_destinations)} → {len(unique_destinations)} destinations from cache")
                logger.info(f"   ✓ Using cached destinations for {format_airport_code(origin)} (cached {days_old} day(s) ago, {len(unique_destinations)} unique)")
                return unique_destinations
            else:
                logger.debug(f"   Cache for {format_airport_code(origin)} is expired ({days_old} days old), will refresh")
                return None
        except Exception as e:
            logger.debug(f"   Error reading cache for {format_airport_code(origin)}: {e}")
            return None
    
    def _save_cached_destinations(self, origin: str, destinations: List[str]):
        """
        Save destinations to cache for an origin airport
        
        Args:
            origin: IATA code of origin airport
            destinations: List of destination IATA codes (will be deduplicated before saving)
        """
        cache_dir = "data/destinations_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{origin.upper()}_destinations.json")
        
        try:
            # Deduplicate destinations before saving (convert to uppercase for consistency)
            unique_destinations = sorted(list(set(dest.upper() for dest in destinations)))
            
            cache_data = {
                'origin': origin.upper(),
                'destinations': unique_destinations,
                'cached_date': datetime.now().isoformat(),
                'count': len(unique_destinations)
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            if len(unique_destinations) < len(destinations):
                logger.debug(f"   Deduplicated {len(destinations)} → {len(unique_destinations)} destinations before caching")
            logger.debug(f"   Cached {len(unique_destinations)} unique destinations for {format_airport_code(origin)} to {cache_file}")
        except Exception as e:
            logger.debug(f"   Error saving cache for {format_airport_code(origin)}: {e}")
    
    def _get_cached_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str],
        max_stops: int,
        nearby_airports_radius_km: int,
        max_duration_hours: float,
        flight_type: str = "both"
    ) -> Optional[List[Dict]]:
        """
        Get cached flight search results
        
        Args:
            origin: IATA code of origin airport
            destination: IATA code of destination airport
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)
            max_stops: Maximum number of stops
            nearby_airports_radius_km: Search radius for nearby airports
            max_duration_hours: Maximum flight duration in hours
        
        Returns:
            List of cached flight offers if cache exists and is valid, None otherwise
        """
        if not self.use_flight_cache:
            logger.debug(f"   Flight caching is disabled (use_flight_cache=False)")
            return None
        
        # Create cache key from all search parameters
        # This ensures we cache correctly based on all search criteria
        return_date_str = return_date if return_date else "none"
        cache_key = f"{origin.upper()}_{destination.upper()}_{departure_date}_{return_date_str}_{max_stops}_{nearby_airports_radius_km}_{max_duration_hours}_{flight_type}"
        
        # Sanitize cache key for filename (replace invalid characters)
        cache_key_safe = cache_key.replace('/', '_').replace(':', '_')
        
        cache_dir = os.path.join(os.path.dirname(__file__), 'data', 'flights_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key_safe}.json")
        
        if not os.path.exists(cache_file):
            logger.debug(f"   Cache file not found for {format_airport_code(origin)} → {format_airport_code(destination)} ({departure_date} to {return_date})")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (same day - flights don't change for the same date)
            cached_date_str = cache_data.get('cached_date', '')
            if cached_date_str:
                try:
                    cached_date = datetime.fromisoformat(cached_date_str)
                    today = datetime.now()
                    
                    # Cache is valid if it was created today (same day)
                    # Flights for a specific date don't change during the same day
                    if cached_date.date() == today.date():
                        flights = cache_data.get('flights', [])
                        logger.info(f"   ✓ Using cached flight results for {format_airport_code(origin)} → {format_airport_code(destination)} ({departure_date} to {return_date}) - {len(flights)} flight(s)")
                        return flights
                    else:
                        logger.debug(f"   Cache expired (cached on {cached_date.date()}, today is {today.date()})")
                except Exception as e:
                    logger.debug(f"   Error parsing cache date: {e}")
            
            return None
        except Exception as e:
            logger.debug(f"   Error reading flight cache: {e}")
            return None
    
    def _save_cached_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str],
        max_stops: int,
        nearby_airports_radius_km: int,
        max_duration_hours: float,
        flights: List[Dict],
        flight_type: str = "both"
    ):
        """
        Save flight search results to cache
        
        Args:
            origin: IATA code of origin airport
            destination: IATA code of destination airport
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)
            max_stops: Maximum number of stops
            nearby_airports_radius_km: Search radius for nearby airports
            max_duration_hours: Maximum flight duration in hours
            flights: List of flight offers to cache
        """
        if not self.use_flight_cache:
            logger.debug(f"   Flight caching is disabled (use_flight_cache=False)")
            return
        
        # Create cache key from all search parameters
        return_date_str = return_date if return_date else "none"
        cache_key = f"{origin.upper()}_{destination.upper()}_{departure_date}_{return_date_str}_{max_stops}_{nearby_airports_radius_km}_{max_duration_hours}_{flight_type}"
        
        # Sanitize cache key for filename
        cache_key_safe = cache_key.replace('/', '_').replace(':', '_')
        
        cache_dir = os.path.join(os.path.dirname(__file__), 'data', 'flights_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key_safe}.json")
        
        try:
            cache_data = {
                'origin': origin.upper(),
                'destination': destination.upper(),
                'departure_date': departure_date,
                'return_date': return_date,
                'max_stops': max_stops,
                'nearby_airports_radius_km': nearby_airports_radius_km,
                'max_duration_hours': max_duration_hours,
                'flights': flights,
                'cached_date': datetime.now().isoformat(),
                'count': len(flights)
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"   Cached {len(flights)} flight(s) for {format_airport_code(origin)} → {format_airport_code(destination)} ({departure_date} to {return_date}) to {cache_file}")
        except Exception as e:
            logger.debug(f"   Error saving flight cache: {e}")
    
    def _get_destinations_from_inspiration_search(
        self, 
        origin: str, 
        departure_date: str,
        max_duration_hours: float = 0,
        non_stop: bool = False
    ) -> List[str]:
        """
        Get destinations dynamically using Amadeus Flight Inspiration Search API
        Uses caching to avoid redundant API calls for the same origin
        """
        # Check cache first
        cached_destinations = self._get_cached_destinations(origin)
        if cached_destinations is not None:
            return cached_destinations
        
        destinations = []
        
        try:
            logger.info(f"   Searching for destinations from {format_airport_code(origin)} using Flight Inspiration Search API...")
            
            # DEBUG: Log exact API call details
            logger.debug(f"   [DEBUG] API Call Details:")
            logger.debug(f"   [DEBUG]   - Endpoint: shopping.flight_destinations.get")
            logger.debug(f"   [DEBUG]   - Origin: {format_airport_code(origin)}")
            logger.debug(f"   [DEBUG]   - Hostname: {self.hostname}")
            
            # Ensure client is authenticated before making the call
            # The SDK should handle this automatically, but we verify it works
            try:
                # The SDK handles authentication automatically on first API call
                # We don't need to check access_token directly - just log that we're making the call
                logger.debug(f"   [DEBUG] Access token will be obtained automatically by SDK if needed")
            except:
                # SDK will handle authentication automatically
                logger.debug(f"   [DEBUG] Access token will be obtained on first API call")
            
            # Use Flight Destinations API (Flight Inspiration Search)
            # According to Swagger spec, we should provide departureDate range for better results
            # Parameters:
            # - origin: required (IATA code)
            # - departureDate: optional but recommended (range format: "YYYY-MM-DD,YYYY-MM-DD")
            # - viewBy: optional (DESTINATION, DATE, DURATION, WEEK, COUNTRY) - defaults to DESTINATION for round-trip
            # - duration: optional (range of days, e.g. "1,15")
            # - oneWay: optional (default false for round-trip)
            # - nonStop: optional (default false)
            # - maxPrice: optional (integer, no decimals)
            
            # According to Swagger spec:
            # - departureDate is optional but recommended
            # - Can be single date or range (format: "YYYY-MM-DD" or "YYYY-MM-DD,YYYY-MM-DD")
            # - Cannot be more than 180 days in the future
            # - viewBy defaults to DESTINATION for round-trip (oneWay=false)
            # - oneWay defaults to false (round-trip)
            
            from datetime import datetime, timedelta
            
            # Build API call parameters - start with required origin
            api_params = {
                'origin': origin,
            }
            
            # Add departureDate if provided (as single date or range)
            # The API works better with a date range, so create one from departure_date
            # Use the actual departure date from config as the start, not today's date
            if departure_date:
                try:
                    dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
                    today = datetime.now()
                    
                    # Check if date is in the future and within 180 days
                    days_ahead = (dep_date - today).days
                    if days_ahead >= 0:
                        # Create a range starting from the departure date from config
                        # Use the actual departure date from config as the start, not today's date
                        # This ensures we search for destinations around the user's specified departure date
                        # Use wider date range (90 days instead of 60) to get more destination options
                        # The API works better with wider ranges as it has more cached data to work with
                        range_start = dep_date  # Start from the departure date from config
                        range_end = dep_date + timedelta(days=90)  # End 90 days after departure date (increased from 60)
                        api_params['departureDate'] = f"{range_start.strftime('%Y-%m-%d')},{range_end.strftime('%Y-%m-%d')}"
                        logger.debug(f"   [DEBUG] Using departure date range: {range_start.strftime('%Y-%m-%d')} to {range_end.strftime('%Y-%m-%d')} (90 days, based on config date: {departure_date})")
                    else:
                        # Date is in the past, use just the date (API may still work)
                        api_params['departureDate'] = departure_date
                        logger.debug(f"   [DEBUG] Departure date is in the past, using single date: {departure_date}")
                except Exception as e:
                    logger.debug(f"   [DEBUG] Date parsing error: {e}, using departure_date as-is")
                    api_params['departureDate'] = departure_date
            
            # Explicitly set viewBy to DESTINATION to get unique destinations
            # Note: Other options are DATE, DURATION, WEEK, COUNTRY - but DESTINATION is best for our use case
            api_params['viewBy'] = 'DESTINATION'
            
            # Set oneWay to false for round-trip flights
            api_params['oneWay'] = False
            
            # If non_stop is True, only get destinations with direct flights
            # This is useful when max_stops=0 (user wants direct flights only)
            # IMPORTANT: When non_stop is False, we don't set the parameter at all
            # This allows the API to return destinations with connections, which should return MORE destinations
            if non_stop:
                api_params['nonStop'] = True
                logger.info(f"   🔍 Filtering for direct flights only (nonStop=True)")
                logger.debug(f"   [DEBUG] nonStop=True: Only searching for destinations with direct flights")
            else:
                # Don't set nonStop parameter - this allows destinations with connections
                # This should return MORE destinations than when nonStop=True
                logger.info(f"   🔍 Including destinations with connections (nonStop not set)")
                logger.debug(f"   [DEBUG] nonStop not set: Will return destinations with direct flights AND connections")
            
            logger.debug(f"   [DEBUG] API Parameters: {api_params}")
            logger.debug(f"   [DEBUG] Making authenticated API call...")
            
            # Make the API call - SDK will handle authentication automatically
            response = self.amadeus.shopping.flight_destinations.get(**api_params)
            
            # DEBUG: Log response details including pagination/metadata
            logger.debug(f"   [DEBUG] API Response:")
            logger.debug(f"   [DEBUG]   - Response type: {type(response)}")
            logger.debug(f"   [DEBUG]   - Has data attribute: {hasattr(response, 'data')}")
            
            # Check for pagination/metadata in response
            if hasattr(response, 'meta'):
                logger.debug(f"   [DEBUG]   - Response meta: {response.meta}")
            if hasattr(response, 'links'):
                logger.debug(f"   [DEBUG]   - Response links (pagination): {response.links}")
            if hasattr(response, 'dictionaries'):
                logger.debug(f"   [DEBUG]   - Response dictionaries: {response.dictionaries}")
            
            if hasattr(response, 'data'):
                logger.debug(f"   [DEBUG]   - Data type: {type(response.data)}")
                logger.debug(f"   [DEBUG]   - Data length: {len(response.data) if response.data else 0}")
                if response.data:
                    logger.debug(f"   [DEBUG]   - First item sample: {response.data[0] if len(response.data) > 0 else 'N/A'}")
            
            # Check if there are more results available (pagination)
            has_more_results = False
            if hasattr(response, 'meta') and response.meta:
                if isinstance(response.meta, dict):
                    count = response.meta.get('count', 0)
                    logger.debug(f"   [DEBUG]   - Total count from meta: {count}")
                    if count and count > len(response.data) if response.data else 0:
                        has_more_results = True
                        logger.warning(f"   ⚠️  API returned {len(response.data) if response.data else 0} results, but meta indicates {count} total results available")
                        logger.warning(f"   ⚠️  Some results may be missing (pagination not implemented)")
            
            if response.data:
                logger.info(f"   ✓ Found {len(response.data)} destination(s) from Amadeus API")
                
                # Use a set to automatically deduplicate destinations
                destinations_set = set()
                
                # According to official Amadeus API documentation:
                # FlightDestination object contains: type, origin, destination, departureDate, returnDate, price, links
                # Reference: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search/api-reference
                for destination_info in response.data:
                    # Extract destination IATA code from FlightDestination object
                    destination_code = destination_info.get('destination')
                    
                    if destination_code:
                        # Verify we have a valid FlightDestination object structure
                        # Log additional info for debugging if available
                        origin_code = destination_info.get('origin', origin)
                        departure_date_from_api = destination_info.get('departureDate', 'N/A')
                        return_date_from_api = destination_info.get('returnDate', 'N/A')
                        price_info = destination_info.get('price', {})
                        
                        logger.debug(f"   [DEBUG] FlightDestination: origin={origin_code}, destination={destination_code}, "
                                   f"departureDate={departure_date_from_api}, returnDate={return_date_from_api}, "
                                   f"price={price_info.get('total', 'N/A')} {price_info.get('currency', 'N/A')}")
                        
                        # Add destination to set (automatically deduplicates)
                        destinations_set.add(destination_code.upper())
                
                # Convert set to sorted list for consistent output
                destinations = sorted(list(destinations_set))
                
                logger.info(f"   ✓ Extracted {len(destinations)} unique destination IATA code(s)")
                logger.info(f"   Sample destinations: {', '.join(destinations[:10])}...")
                if non_stop:
                    logger.info(f"   Note: Results filtered to direct flights only (nonStop=True)")
                else:
                    logger.info(f"   Note: Results include destinations with direct flights AND connections (nonStop not set)")
                logger.info(f"   Note: These are from Inspiration Search cache - Flight Offers Search will validate actual availability")
                
                # Save to cache for future use and return destinations
                if destinations:
                    self._save_cached_destinations(origin, destinations)
                    return destinations  # Return immediately - first API succeeded
            else:
                logger.warning(f"   ⚠️  No destinations found from Flight Inspiration Search API")
                
                # If we got no results and nonStop was set, try again without nonStop to get destinations with connections
                if non_stop:
                    logger.info(f"   Retrying without nonStop filter to include destinations with connections...")
                    # Recursively call without nonStop parameter
                    return self._get_destinations_from_inspiration_search(
                        origin, departure_date, max_duration_hours, non_stop=False
                    )
                
                logger.info(f"   Trying Airport Routes API as fallback...")
                
                # Fallback to Airport Routes API if Inspiration Search returns no results
                destinations = self._get_destinations_from_airport_routes(origin, non_stop)
                if destinations:
                    # Save to cache for future use
                    self._save_cached_destinations(origin, destinations)
                    return destinations
                
                logger.warning(f"   This is expected in test environment - Inspiration Search uses cached data")
                logger.warning(f"   Test environment may not have data for origin {format_airport_code(origin)} (especially TLV (Tel Aviv))")
                logger.info(f"   Returning empty list - caller will handle fallback to predefined list")
                return []  # Return empty so caller can detect failure and use predefined list
                
        except ResponseError as error:
            # Extract error details with full debug information
            status_code = 'Unknown'
            error_code = 'Unknown'
            error_title = 'Unknown'
            error_detail = 'Unknown'
            error_body = None
            error_url = None
            
            if hasattr(error, 'response'):
                status_code = error.response.status_code if hasattr(error.response, 'status_code') else 'Unknown'
                error_body = error.response.body if hasattr(error.response, 'body') else None
                error_url = error.response.request.url if hasattr(error.response, 'request') and hasattr(error.response.request, 'url') else None
            
            # Extract error information from the error object
            error_code = error.code if hasattr(error, 'code') else 'Unknown'
            error_title = error.title if hasattr(error, 'title') else 'Unknown'
            error_detail = error.description() if hasattr(error, 'description') else str(error)
            
            logger.error(f"   ❌ Amadeus API returned an error for Flight Inspiration Search")
            logger.error(f"   Status Code: {status_code}")
            logger.error(f"   Error Code: {error_code}")
            logger.error(f"   Error Title: {error_title}")
            logger.error(f"   Error Detail: {error_detail}")
            logger.error(f"   This is an error response from the Amadeus API service (not a connection issue)")
            
            # Handle 401 authentication errors specifically
            if status_code == 401:
                logger.error(f"   ⚠️  AUTHENTICATION ERROR: Missing or invalid Authorization header")
                logger.error(f"   This usually means:")
                logger.error(f"   1. API credentials are incorrect or expired")
                logger.error(f"   2. The API key/secret don't have permission for this endpoint")
                logger.error(f"   3. The authentication token expired and wasn't refreshed")
                logger.error(f"   Please verify your API credentials in config.yaml")
                logger.error(f"   Get new credentials at: https://developers.amadeus.com/self-service")
                logger.error(f"   Make sure your API key has access to 'Flight Inspiration Search' API")
                logger.error(f"   Check your API key permissions in the Amadeus Developer Portal")
            
            # If it's a 404, it might be due to limited test data or no data available
            # First, try again without nonStop filter if it was set (might return more results)
            if status_code == 404:
                if non_stop:
                    logger.info(f"   404 error with nonStop=True, retrying without nonStop filter...")
                    # Recursively call without nonStop parameter
                    return self._get_destinations_from_inspiration_search(
                        origin, departure_date, max_duration_hours, non_stop=False
                    )
                
                logger.info(f"   Trying Airport Routes API as fallback for 404 error...")
                destinations = self._get_destinations_from_airport_routes(origin, non_stop)
                if destinations:
                    # Save to cache for future use
                    self._save_cached_destinations(origin, destinations)
                    return destinations
                
                if self.environment == "test":
                    logger.warning(f"   ⚠️  404 error: No data available for origin {format_airport_code(origin)} in test environment")
                    logger.warning(f"   This is expected - Amadeus test environment has limited cached data")
                    logger.warning(f"   TLV (Tel Aviv) is not in the test cache, which is why you see this error")
                    logger.info(f"   Returning empty list - caller will use fallback logic (other origin's destinations or predefined list)")
                    logger.info(f"   Flight Offers Search will validate which destinations are actually reachable")
                    logger.info(f"   For production use, switch to 'production' environment for complete data")
                else:
                    logger.warning(f"   ⚠️  404 error: No data available for origin {format_airport_code(origin)}")
                    logger.warning(f"   This may indicate that the Flight Inspiration Search API has no cached data for this origin")
                    logger.info(f"   Returning empty list - caller will use fallback logic (other origin's destinations or predefined list)")
                    logger.info(f"   Flight Offers Search will validate which destinations are actually reachable")
            
            # DEBUG: Log full error details
            logger.debug(f"   [DEBUG] Exception Type: ResponseError")
            logger.debug(f"   [DEBUG] Exception: {error}")
            if error_url:
                logger.debug(f"   [DEBUG]   - URL: {error_url}")
            if error_body:
                logger.debug(f"   [DEBUG]   - Body content: {error_body}")
            
            logger.error(f"   ERROR: API returned status {error_code}")
            logger.info(f"   Returning empty list - caller will handle fallback to predefined list")
            
            if error_body:
                import json
                try:
                    if isinstance(error_body, str):
                        error_data = json.loads(error_body)
                    else:
                        error_data = error_body
                    
                    logger.debug(f"   [DEBUG] Parsed error data: {error_data}")
                    
                    if 'errors' in error_data and len(error_data['errors']) > 0:
                        first_error = error_data['errors'][0]
                        error_title = first_error.get('title', 'N/A')
                        error_detail = first_error.get('detail', 'N/A')
                        error_code_detail = first_error.get('code', 'N/A')
                        logger.error(f"   ERROR: {error_title} - {error_detail}")
                        logger.debug(f"   [DEBUG] Error code: {error_code_detail}")
                        logger.debug(f"   [DEBUG] Full error object: {first_error}")
                    else:
                        logger.debug(f"   [DEBUG] Error data structure: {error_data}")
                except Exception as parse_error:
                    logger.debug(f"   [DEBUG] Failed to parse error body: {parse_error}")
                    logger.debug(f"   [DEBUG] Raw error body: {error_body}")
            
            # Return empty list so caller can detect failure and use predefined list
            logger.info(f"   Returning empty list - caller will handle fallback to predefined list")
            return []
        except Exception as e:
            logger.error(f"   ERROR: Unexpected error using Flight Inspiration Search API: {type(e).__name__}")
            logger.error(f"   ERROR: {str(e)}")
            logger.debug(f"   [DEBUG] Full exception: {e}")
            import traceback
            logger.debug(f"   [DEBUG] Traceback:\n{traceback.format_exc()}")
            
            # If nonStop was set, try again without it before falling back to Airport Routes API
            if non_stop:
                logger.info(f"   Retrying without nonStop filter after unexpected error...")
                try:
                    return self._get_destinations_from_inspiration_search(
                        origin, departure_date, max_duration_hours, non_stop=False
                    )
                except Exception as retry_error:
                    logger.warning(f"   Retry also failed: {retry_error}")
            
            # Try Airport Routes API as fallback for unexpected errors
            logger.info(f"   Trying Airport Routes API as fallback for unexpected error...")
            destinations = self._get_destinations_from_airport_routes(origin, non_stop)
            if destinations:
                # Save to cache for future use
                self._save_cached_destinations(origin, destinations)
                return destinations
            
            logger.info(f"   Returning empty list - caller will handle fallback to predefined list")
            return []
        
        # This code should never be reached - all paths above return
        # But keeping as safety fallback
        if not destinations:
            logger.warning(f"   ⚠️  No destinations extracted from API response")
            logger.info(f"   Returning empty list - caller will handle fallback to predefined list")
            return []
        
        logger.info(f"   Total destinations discovered: {len(destinations)}")
        logger.info(f"   Destination selection: Dynamically discovered from Amadeus API")
        
        return destinations
    
    def _get_destinations_from_airport_routes(
        self, 
        origin: str, 
        non_stop: bool = False
    ) -> List[str]:
        """
        Get destinations using Amadeus Airport Routes API (direct destinations)
        This API returns all direct destinations (non-stop flights) from a specific airport.
        Useful as a fallback when Flight Inspiration Search API returns no results.
        
        Reference: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-routes
        
        Args:
            origin: IATA code of origin airport
            non_stop: If True, only return destinations with direct flights (this API always returns direct destinations)
        
        Returns:
            List of destination IATA codes (direct destinations only)
        """
        destinations = []
        
        try:
            logger.info(f"   Searching for direct destinations from {format_airport_code(origin)} using Airport Routes API...")
            
            # Airport Routes API endpoint: GET /v1/airport/direct-destinations?departureAirportCode=XXX
            # This API returns all direct destinations (non-stop flights) from the specified airport
            # Note: This API always returns direct destinations, so non_stop parameter is always True
            api_params = {
                'departureAirportCode': origin.upper()
            }
            
            logger.debug(f"   [DEBUG] ===== Airport Routes API Call =====")
            logger.debug(f"   [DEBUG] Endpoint: airport.direct_destinations.get()")
            logger.debug(f"   [DEBUG] Parameters: {api_params}")
            logger.debug(f"   [DEBUG] Origin: {format_airport_code(origin)}")
            logger.debug(f"   [DEBUG] Non-stop only: {non_stop}")
            logger.debug(f"   [DEBUG] Environment: {self.environment}")
            logger.debug(f"   [DEBUG] Making authenticated API call...")
            
            # Make the API call - SDK will handle authentication automatically
            # The endpoint is: airport.direct_destinations.get()
            response = self.amadeus.airport.direct_destinations.get(**api_params)
            
            # DEBUG: Log comprehensive response details
            logger.debug(f"   [DEBUG] ===== API Response =====")
            logger.debug(f"   [DEBUG] Response type: {type(response)}")
            logger.debug(f"   [DEBUG] Response object: {response}")
            logger.debug(f"   [DEBUG] Has 'data' attribute: {hasattr(response, 'data')}")
            
            if hasattr(response, 'data'):
                logger.debug(f"   [DEBUG] Data type: {type(response.data)}")
                logger.debug(f"   [DEBUG] Data is None: {response.data is None}")
                logger.debug(f"   [DEBUG] Data length: {len(response.data) if response.data else 0}")
                
                if response.data:
                    logger.debug(f"   [DEBUG] Full response.data: {response.data}")
                    logger.debug(f"   [DEBUG] First item (full): {response.data[0] if len(response.data) > 0 else 'N/A'}")
                    logger.debug(f"   [DEBUG] First item type: {type(response.data[0]) if len(response.data) > 0 else 'N/A'}")
                    if len(response.data) > 0 and isinstance(response.data[0], dict):
                        logger.debug(f"   [DEBUG] First item keys: {list(response.data[0].keys())}")
                        logger.debug(f"   [DEBUG] First item full structure: {json.dumps(response.data[0], indent=2, ensure_ascii=False)}")
                    if len(response.data) > 1:
                        logger.debug(f"   [DEBUG] Second item (full): {response.data[1]}")
                else:
                    logger.debug(f"   [DEBUG] response.data is empty or None")
            else:
                logger.debug(f"   [DEBUG] Response does not have 'data' attribute")
                logger.debug(f"   [DEBUG] Available attributes: {dir(response)}")
            
            # Try to get raw response if available
            if hasattr(response, 'response'):
                logger.debug(f"   [DEBUG] Raw response object: {response.response}")
            if hasattr(response, 'result'):
                logger.debug(f"   [DEBUG] Response result: {response.result}")
            
            if response.data:
                logger.info(f"   ✓ Found {len(response.data)} direct destination(s) from Airport Routes API")
                
                # Use a set to automatically deduplicate destinations
                destinations_set = set()
                
                # According to Amadeus Airport Routes API documentation:
                # Reference: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-routes/api-reference
                # Response contains a list of destination objects
                # Each destination object may contain: 'destination' (IATA code) or 'iataCode' field
                logger.debug(f"   [DEBUG] ===== Processing {len(response.data)} destination(s) =====")
                for idx, destination_info in enumerate(response.data):
                    logger.debug(f"   [DEBUG] --- Processing item {idx + 1}/{len(response.data)} ---")
                    logger.debug(f"   [DEBUG] Item type: {type(destination_info)}")
                    logger.debug(f"   [DEBUG] Item value: {destination_info}")
                    
                    # Try multiple possible field names for destination code
                    destination_code = None
                    if isinstance(destination_info, dict):
                        logger.debug(f"   [DEBUG] Item is dict with keys: {list(destination_info.keys())}")
                        logger.debug(f"   [DEBUG] Full item JSON: {json.dumps(destination_info, indent=2, ensure_ascii=False)}")
                        
                        # Try 'destination' field first (most common)
                        destination_code = destination_info.get('destination')
                        logger.debug(f"   [DEBUG] Trying 'destination' field: {destination_code}")
                        
                        # If not found, try 'iataCode' (alternative field name)
                        if not destination_code:
                            destination_code = destination_info.get('iataCode')
                            logger.debug(f"   [DEBUG] Trying 'iataCode' field: {destination_code}")
                        
                        # If still not found, try 'destinationCode'
                        if not destination_code:
                            destination_code = destination_info.get('destinationCode')
                            logger.debug(f"   [DEBUG] Trying 'destinationCode' field: {destination_code}")
                        
                        # If still not found, try other common variations
                        if not destination_code:
                            destination_code = destination_info.get('code')
                            logger.debug(f"   [DEBUG] Trying 'code' field: {destination_code}")
                        
                        if not destination_code:
                            destination_code = destination_info.get('airportCode')
                            logger.debug(f"   [DEBUG] Trying 'airportCode' field: {destination_code}")
                        
                        # If still not found, log the structure for debugging
                        if not destination_code:
                            logger.debug(f"   [DEBUG] ⚠️  Could not find destination code in item!")
                            logger.debug(f"   [DEBUG] All available keys: {list(destination_info.keys())}")
                            logger.debug(f"   [DEBUG] Full item structure: {json.dumps(destination_info, indent=2, ensure_ascii=False)}")
                    elif isinstance(destination_info, str):
                        # If the response is a simple list of strings (IATA codes)
                        destination_code = destination_info
                        logger.debug(f"   [DEBUG] Item is string (IATA code): {destination_code}")
                    else:
                        logger.debug(f"   [DEBUG] ⚠️  Unexpected item type: {type(destination_info)}")
                        logger.debug(f"   [DEBUG] Item value: {destination_info}")
                    
                    if destination_code:
                        logger.debug(f"   [DEBUG] ✓ Extracted destination code: {destination_code}")
                        # Add destination to set (automatically deduplicates)
                        destinations_set.add(destination_code.upper())
                    else:
                        logger.debug(f"   [DEBUG] ✗ Skipping item - no destination code found")
                
                # Convert set to sorted list for consistent output
                destinations = sorted(list(destinations_set))
                
                logger.info(f"   ✓ Extracted {len(destinations)} unique direct destination IATA code(s)")
                logger.info(f"   Sample destinations: {', '.join(destinations[:10])}...")
                logger.info(f"   Note: Airport Routes API returns direct destinations only (non-stop flights)")
                logger.info(f"   Flight Offers Search will validate which destinations are actually reachable")
            else:
                logger.warning(f"   ⚠️  No destinations found from Airport Routes API")
                
        except ResponseError as error:
            # Extract error details with comprehensive debugging
            logger.debug(f"   [DEBUG] ===== Airport Routes API Error =====")
            logger.debug(f"   [DEBUG] Error type: {type(error)}")
            logger.debug(f"   [DEBUG] Error object: {error}")
            logger.debug(f"   [DEBUG] Error attributes: {dir(error)}")
            
            status_code = 'Unknown'
            error_code = 'Unknown'
            error_title = 'Unknown'
            error_detail = 'Unknown'
            error_body = None
            error_url = None
            
            if hasattr(error, 'response'):
                logger.debug(f"   [DEBUG] Error has 'response' attribute")
                logger.debug(f"   [DEBUG] Response type: {type(error.response)}")
                logger.debug(f"   [DEBUG] Response object: {error.response}")
                status_code = error.response.status_code if hasattr(error.response, 'status_code') else 'Unknown'
                error_body = error.response.body if hasattr(error.response, 'body') else None
                error_url = error.response.request.url if hasattr(error.response, 'request') and hasattr(error.response.request, 'url') else None
                logger.debug(f"   [DEBUG] Response status_code: {status_code}")
                logger.debug(f"   [DEBUG] Response body: {error_body}")
                logger.debug(f"   [DEBUG] Request URL: {error_url}")
            else:
                logger.debug(f"   [DEBUG] Error does not have 'response' attribute")
            
            error_code = error.code if hasattr(error, 'code') else 'Unknown'
            error_title = error.title if hasattr(error, 'title') else 'Unknown'
            error_detail = error.description() if hasattr(error, 'description') else str(error)
            
            logger.debug(f"   [DEBUG] Error code: {error_code}")
            logger.debug(f"   [DEBUG] Error title: {error_title}")
            logger.debug(f"   [DEBUG] Error detail: {error_detail}")
            
            logger.warning(f"   ⚠️  Airport Routes API returned an error")
            logger.warning(f"   Status Code: {status_code}")
            logger.warning(f"   Error Code: {error_code}")
            logger.warning(f"   Error Title: {error_title}")
            logger.warning(f"   Error Detail: {error_detail}")
            
            # Parse error body if available
            if error_body:
                try:
                    if isinstance(error_body, str):
                        error_data = json.loads(error_body)
                    else:
                        error_data = error_body
                    logger.debug(f"   [DEBUG] Parsed error body: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except Exception as parse_error:
                    logger.debug(f"   [DEBUG] Could not parse error body: {parse_error}")
                    logger.debug(f"   [DEBUG] Raw error body: {error_body}")
            
            # Handle 401 authentication errors
            if status_code == 401:
                logger.warning(f"   ⚠️  AUTHENTICATION ERROR: Missing or invalid Authorization header")
                logger.warning(f"   Please verify your API credentials in config.yaml")
                logger.warning(f"   Make sure your API key has access to 'Airport Routes' API")
            
            # If it's a 404, the airport might not have route data
            if status_code == 404:
                logger.warning(f"   ⚠️  404 error: No route data available for origin {format_airport_code(origin)}")
                logger.warning(f"   This may indicate that the Airport Routes API has no data for this airport")
            
            logger.debug(f"   [DEBUG] Airport Routes API error: {error}")
            
        except Exception as e:
            logger.warning(f"   ⚠️  Unexpected error using Airport Routes API: {type(e).__name__}")
            logger.warning(f"   Error: {str(e)}")
            logger.debug(f"   [DEBUG] Full exception: {e}")
            import traceback
            logger.debug(f"   [DEBUG] Traceback:\n{traceback.format_exc()}")
        
        return destinations
    
    def _get_predefined_destinations(self) -> List[str]:
        """
        Get predefined list of popular destinations (fallback)
        Returns deduplicated list sorted alphabetically
        """
        # Popular European destinations (IATA codes) - prioritized by likelihood
        # of having flights from both TLV and ALC
        popular_destinations = [
            # Major hubs (most likely to have flights)
            "LON", "PAR", "MAD", "BCN", "AMS", "BER", "ROM", "FCO",
            # Secondary popular destinations
            "VIE", "PRG", "ATH", "LIS", "DUB", "CPH", "STO", "OSL",
            # Mediterranean and nearby
            "MIL", "VEN", "NAP", "PMO", "AGP", "SEV", "ZUR", "BRU",
            # Eastern Europe
            "WAR", "BUD", "ZAG", "SPL", "DBV",
            # Northern Europe
            "HEL", "REK", "OPO"
        ]
        
        # Deduplicate and sort for consistency (convert to uppercase)
        unique_destinations = sorted(list(set(dest.upper() for dest in popular_destinations)))
        
        if len(unique_destinations) < len(popular_destinations):
            logger.debug(f"   Deduplicated predefined destinations: {len(popular_destinations)} → {len(unique_destinations)}")
        logger.info(f"   Using {len(unique_destinations)} predefined destinations")
        return unique_destinations
    
    def get_common_destinations(
        self,
        origin1: str,
        origin2: str,
        departure_date: str,
        use_dynamic: bool = True,
        max_duration_hours: float = 0,
        non_stop: bool = False
    ) -> List[str]:
        """
        Get destinations that are reachable from both origins
        
        Args:
            origin1: IATA code for first origin
            origin2: IATA code for second origin
            departure_date: Departure date (YYYY-MM-DD)
            use_dynamic: If True, use dynamic discovery
            max_duration_hours: Maximum flight duration in hours
            non_stop: If True, only get destinations with direct flights (when max_stops=0)
        
        Returns:
            List of common destination IATA codes
        """
        logger.info("🔍 Finding common destinations from both origins...")
        
        # In test environment, if both origins are known to be unsupported, skip Inspiration Search entirely
        TEST_ENV_UNSUPPORTED_ORIGINS = ['TLV', 'ALC']
        if self.environment == "test" and use_dynamic:
            origin1_unsupported = origin1.upper() in TEST_ENV_UNSUPPORTED_ORIGINS
            origin2_unsupported = origin2.upper() in TEST_ENV_UNSUPPORTED_ORIGINS
            
            if origin1_unsupported and origin2_unsupported:
                logger.warning(f"   ⚠️  Both origins ({format_airport_code(origin1)} and {format_airport_code(origin2)}) are not reliably supported in test environment")
                logger.info(f"   Skipping Inspiration Search for both origins and using predefined list directly")
                logger.info(f"   Note: Flight Offers Search will validate which destinations are actually reachable")
                predefined = self._get_predefined_destinations()
                return predefined
        
        # Try to get destinations from both origins in parallel
        dest1 = []
        dest2 = []
        
        def get_destinations_origin1():
            """Get destinations from origin1"""
            try:
                result = self.get_destination_suggestions(origin1, departure_date, use_dynamic, max_duration_hours, non_stop)
                logger.info(f"   Destinations from {format_airport_code(origin1)}: {len(result)}")
                if len(result) == 0:
                    logger.warning(f"   ⚠️  Inspiration search returned 0 destinations for origin {format_airport_code(origin1)}")
                    logger.warning(f"   This is common in test environment - TLV may not be in Amadeus test cache")
                return result
            except Exception as e:
                logger.warning(f"   ⚠️  Error getting destinations for {format_airport_code(origin1)}: {e}")
                logger.warning(f"   This is expected in test environment - falling back to predefined list")
                return []
        
        def get_destinations_origin2():
            """Get destinations from origin2"""
            try:
                result = self.get_destination_suggestions(origin2, departure_date, use_dynamic, max_duration_hours, non_stop)
                logger.info(f"   Destinations from {format_airport_code(origin2)}: {len(result)}")
                if len(result) == 0:
                    logger.warning(f"   ⚠️  Inspiration search returned 0 destinations for origin {format_airport_code(origin2)}")
                    logger.warning(f"   This is common in test environment - some origins may not be in Amadeus test cache")
                return result
            except Exception as e:
                logger.warning(f"   ⚠️  Error getting destinations for {format_airport_code(origin2)}: {e}")
                logger.warning(f"   This is expected in test environment - falling back to predefined list")
                return []
        
        # Execute both destination searches in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(get_destinations_origin1)
            future2 = executor.submit(get_destinations_origin2)
            
            try:
                dest1 = future1.result()
            except Exception as e:
                logger.error(f"   ❌ Error in parallel destination search for {format_airport_code(origin1)}: {e}")
                dest1 = []
            
            try:
                dest2 = future2.result()
            except Exception as e:
                logger.error(f"   ❌ Error in parallel destination search for {format_airport_code(origin2)}: {e}")
                dest2 = []
        
        # Fallback logic: if one origin has destinations but the other doesn't, use the first one's destinations for both
        if len(dest1) > 0 and len(dest2) == 0:
            logger.info(f"   ⚠️  Origin {format_airport_code(origin2)} returned no destinations, but {format_airport_code(origin1)} returned {len(dest1)} destinations")
            logger.info(f"   Using destinations from {format_airport_code(origin1)} for both origins (fallback mode)")
            logger.info(f"   Flight Offers Search will validate which destinations are actually reachable from {format_airport_code(origin2)}")
            return dest1
        elif len(dest1) == 0 and len(dest2) > 0:
            logger.info(f"   ⚠️  Origin {format_airport_code(origin1)} returned no destinations, but {format_airport_code(origin2)} returned {len(dest2)} destinations")
            logger.info(f"   Using destinations from {format_airport_code(origin2)} for both origins (fallback mode)")
            logger.info(f"   Flight Offers Search will validate which destinations are actually reachable from {format_airport_code(origin1)}")
            return dest2
        elif len(dest1) == 0 and len(dest2) == 0:
            # If both failed, use predefined list
            logger.warning(f"   ⚠️  Both origins returned empty results from Inspiration Search")
            logger.info(f"   Falling back to predefined European destinations list")
            logger.info(f"   Note: Flight Offers Search will validate which destinations are actually reachable")
            predefined = self._get_predefined_destinations()
            return predefined
        
        # Deduplicate destinations from both origins before finding intersection
        dest1_set = set(dest.upper() for dest in dest1)
        dest2_set = set(dest.upper() for dest in dest2)
        
        # Both origins returned results - find intersection
        common = sorted(list(dest1_set.intersection(dest2_set)))
        logger.info(f"   Common destinations (intersection): {len(common)}")
        
        if common:
            logger.info(f"   Common destinations: {', '.join(common[:20])}{'...' if len(common) > 20 else ''}")
            logger.info(f"   Note: Flight Offers Search will validate which destinations are actually reachable")
        else:
            logger.warning(f"   ⚠️  No common destinations found in intersection!")
            logger.warning(f"   This may indicate test environment limitations or incomplete Inspiration Search data")
            logger.info(f"   Using union of both lists as fallback...")
            common = sorted(list(dest1_set.union(dest2_set)))
            logger.info(f"   Using all destinations from both origins: {len(common)} unique")
            logger.info(f"   Note: Flight Offers Search will validate which destinations are actually reachable")
        
        return common
    
    def find_matching_flights(
        self,
        origin1: str,
        origin2: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        max_price: float = 600,
        max_stops_person1: int = 0,
        max_stops_person2: int = 0,
        arrival_tolerance_hours: int = 3,
        min_departure_time_outbound: Optional[str] = None,
        min_departure_time_return: Optional[str] = None,
        nearby_airports_radius_km: int = 0,
        max_duration_hours: float = 0,
        flight_type: str = "both"
    ) -> List[Dict]:
        """
        Find matching flights for a destination - this is the source of truth for route availability
        
        This method uses Flight Offers Search API to validate that:
        - The destination is actually reachable from both origins
        - Flights exist on the specified dates
        - Flights meet the specified criteria (price, stops, times)
        
        Note: This is more reliable than Inspiration Search, which uses cached data.
        Flight Offers Search uses live inventory and will return empty if no flights exist.
        This makes it the authoritative source for determining if a route is actually available.
        
        Args:
            origin1: IATA code for first origin
            origin2: IATA code for second origin
            destination: IATA code for destination
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD) - Required for "both" or "return", ignored for "outbound"
            max_price: Maximum price per person
            max_stops_person1: Maximum number of stops for Person 1 flights
            max_stops_person2: Maximum number of stops for Person 2 flights
            arrival_tolerance_hours: Hours tolerance for matching times (arrival for "outbound", departure for "return")
            min_departure_time_outbound: Minimum departure time for outbound (HH:MM)
            min_departure_time_return: Minimum departure time for return (HH:MM)
            nearby_airports_radius_km: Search radius for nearby airports (0 = disabled)
            max_duration_hours: Maximum flight duration in hours (0 = no limit)
            flight_type: "both" (round trip), "outbound" (one-way to destination), or "return" (one-way from destination)
        
        Returns:
            List of matching flight pairs with details
        """
        # Resolve non-airport codes (like railway stations) to nearest airports
        destination_resolved = resolve_airport_code(destination)
        origin1_resolved = resolve_airport_code(origin1)
        origin2_resolved = resolve_airport_code(origin2)
        
        # Log if resolution happened
        if destination_resolved != destination.upper():
            logger.info(f"  → Resolved destination {format_airport_code(destination)} to airport {format_airport_code(destination_resolved)}")
        if origin1_resolved != origin1.upper():
            logger.info(f"  → Resolved origin1 {format_airport_code(origin1)} to airport {format_airport_code(origin1_resolved)}")
        if origin2_resolved != origin2.upper():
            logger.info(f"  → Resolved origin2 {format_airport_code(origin2)} to airport {format_airport_code(origin2_resolved)}")
        
        logger.info(f"🔍 Searching for matching flights to {format_airport_code(destination_resolved)}...")
        logger.info(f"   Person 1: {format_airport_code(origin1_resolved)} → {format_airport_code(destination_resolved)}")
        logger.info(f"   Person 2: {format_airport_code(origin2_resolved)} → {format_airport_code(destination_resolved)}")
        
        # Search flights for both persons in parallel
        logger.debug(f"   Searching flights for Person 1 and Person 2 in parallel...")
        
        def search_person1():
            """Search flights for person 1"""
            logger.debug(f"   [Thread] Searching flights for Person 1 ({format_airport_code(origin1_resolved)} → {format_airport_code(destination_resolved)})...")
            return self.search_flights(
                origin1_resolved, destination_resolved, departure_date, return_date,
                max_stops_person1, min_departure_time_outbound, min_departure_time_return,
                nearby_airports_radius_km, max_duration_hours, flight_type
            )
        
        def search_person2():
            """Search flights for person 2"""
            logger.debug(f"   [Thread] Searching flights for Person 2 ({format_airport_code(origin2_resolved)} → {format_airport_code(destination_resolved)})...")
            return self.search_flights(
                origin2_resolved, destination_resolved, departure_date, return_date,
                max_stops_person2, min_departure_time_outbound, min_departure_time_return,
                nearby_airports_radius_km, max_duration_hours, flight_type
            )
        
        # Execute both searches in parallel using ThreadPoolExecutor
        flights1 = []
        flights2 = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            future1 = executor.submit(search_person1)
            future2 = executor.submit(search_person2)
            
            # Wait for both to complete and collect results
            try:
                flights1 = future1.result()
                logger.debug(f"   [Thread] Person 1 search completed: {len(flights1)} flight(s)")
            except Exception as e:
                logger.error(f"   ❌ Error searching flights for Person 1: {e}")
                flights1 = []
            
            try:
                flights2 = future2.result()
                logger.debug(f"   [Thread] Person 2 search completed: {len(flights2)} flight(s)")
            except Exception as e:
                logger.error(f"   ❌ Error searching flights for Person 2: {e}")
                flights2 = []
        
        logger.info(f"   Found {len(flights1)} flight(s) for Person 1, {len(flights2)} flight(s) for Person 2")
        
        matching_pairs = []
        price_filtered_count = 0
        time_filtered_count = 0
        
        logger.debug(f"   Comparing {len(flights1)} × {len(flights2)} = {len(flights1) * len(flights2)} possible flight combinations...")
        
        for f1 in flights1:
            # Get price and currency
            price_info1 = f1.get('price', {})
            price1 = float(price_info1.get('total', 0))
            currency1 = price_info1.get('currency', 'EUR')
            
            # Check price constraint for person 1 (must be <= max_price)
            if price1 > max_price:
                price_filtered_count += len(flights2)
                logger.debug(f"      Person 1 flight price {price1} {currency1} exceeds max {max_price} EUR")
                continue
            
            for f2 in flights2:
                # Get price and currency
                price_info2 = f2.get('price', {})
                price2 = float(price_info2.get('total', 0))
                currency2 = price_info2.get('currency', 'EUR')
                
                # Check price constraint for person 2 (must be <= max_price)
                if price2 > max_price:
                    price_filtered_count += 1
                    logger.debug(f"      Person 2 flight price {price2} {currency2} exceeds max {max_price} EUR")
                    continue
                
                total_price = price1 + price2
                
                # Check time matching based on flight type
                # For "outbound": match arrival times (when they arrive at destination)
                # For "return": match departure times (when they leave destination)
                # For "both": match arrival times (when they arrive at destination)
                if flight_type == "return":
                    # For return flights, match departure times (when leaving destination)
                    if self._departures_match(f1, f2, arrival_tolerance_hours):
                        matching_pairs.append({
                            'destination': destination,
                            'person1_flight': f1,
                            'person2_flight': f2,
                            'total_price': total_price,
                            'person1_price': price1,
                            'person2_price': price2
                        })
                    else:
                        time_filtered_count += 1
                else:
                    # For "both" or "outbound": match arrival times (when arriving at destination)
                    if self._arrivals_match(f1, f2, arrival_tolerance_hours):
                        matching_pairs.append({
                            'destination': destination,
                            'person1_flight': f1,
                            'person2_flight': f2,
                            'total_price': total_price,
                            'person1_price': price1,
                            'person2_price': price2
                        })
                    else:
                        time_filtered_count += 1
        
        if price_filtered_count > 0:
            logger.debug(f"   Filtered out {price_filtered_count} combination(s) due to price constraints")
        if time_filtered_count > 0:
            match_type = "departure" if flight_type == "return" else "arrival"
            logger.debug(f"   Filtered out {time_filtered_count} combination(s) due to {match_type} time mismatch")
        
        # Sort by total price
        matching_pairs.sort(key=lambda x: x['total_price'])
        
        if matching_pairs:
            logger.info(f"   ✓ Found {len(matching_pairs)} matching flight pair(s) for {format_airport_code(destination_resolved)}")
        else:
            logger.info(f"   ✗ No matching flight pairs found for {format_airport_code(destination_resolved)}")
        
        return matching_pairs
    
    def _arrivals_match(self, flight1: Dict, flight2: Dict, tolerance_hours: int) -> bool:
        """Check if two flights arrive within the tolerance window"""
        try:
            # Get outbound arrival times
            arr1 = self._get_outbound_arrival_time(flight1)
            arr2 = self._get_outbound_arrival_time(flight2)
            
            if not arr1 or not arr2:
                logger.debug(f"      Cannot compare arrivals: missing arrival time data")
                return False
            
            # Parse times
            time1 = datetime.fromisoformat(arr1.replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(arr2.replace('Z', '+00:00'))
            
            # Check if within tolerance
            time_diff = abs((time1 - time2).total_seconds() / 3600)
            matches = time_diff <= tolerance_hours
            
            if matches:
                logger.debug(f"      ✓ Arrivals match: {time_diff:.1f}h difference (within ±{tolerance_hours}h tolerance)")
            else:
                logger.debug(f"      ✗ Arrivals don't match: {time_diff:.1f}h difference (exceeds ±{tolerance_hours}h tolerance)")
            
            return matches
            
        except Exception as e:
            logger.debug(f"      Error checking arrival match: {e}")
            return False
    
    def _get_outbound_arrival_time(self, flight: Dict) -> Optional[str]:
        """Get outbound arrival time from flight offer"""
        try:
            outbound = flight.get('itineraries', [{}])[0]
            segments = outbound.get('segments', [])
            if segments:
                last_segment = segments[-1]
                return last_segment.get('arrival', {}).get('at')
        except Exception:
            pass
        return None
    
    def _departures_match(self, flight1: Dict, flight2: Dict, tolerance_hours: int) -> bool:
        """Check if two flights depart within the tolerance window"""
        try:
            # Get departure times from first itinerary (for one-way flights, this is the only itinerary)
            dep1 = self._get_departure_time(flight1)
            dep2 = self._get_departure_time(flight2)
            
            if not dep1 or not dep2:
                logger.debug(f"      Cannot compare departures: missing departure time data")
                return False
            
            # Parse times
            time1 = datetime.fromisoformat(dep1.replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(dep2.replace('Z', '+00:00'))
            
            # Check if within tolerance
            time_diff = abs((time1 - time2).total_seconds() / 3600)
            matches = time_diff <= tolerance_hours
            
            if matches:
                logger.debug(f"      ✓ Departures match: {time_diff:.1f}h difference (within ±{tolerance_hours}h tolerance)")
            else:
                logger.debug(f"      ✗ Departures don't match: {time_diff:.1f}h difference (exceeds ±{tolerance_hours}h tolerance)")
            
            return matches
            
        except Exception as e:
            logger.debug(f"      Error checking departure match: {e}")
            return False
    
    def _get_departure_time(self, flight: Dict) -> Optional[str]:
        """Get departure time from flight offer (first itinerary, first segment)"""
        try:
            itinerary = flight.get('itineraries', [{}])[0]
            segments = itinerary.get('segments', [])
            if segments:
                first_segment = segments[0]
                return first_segment.get('departure', {}).get('at')
        except Exception:
            pass
        return None

