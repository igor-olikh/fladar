"""
Output formatting module for flight results
"""
from typing import List, Dict, Optional
from datetime import datetime
import csv
import os
import json
import pytz
import airportsdata
from timezonefinder import TimezoneFinder
import logging

logger = logging.getLogger(__name__)

# Load airport database for automatic timezone detection
try:
    airports = airportsdata.load('IATA')  # Load IATA code database
    tf = TimezoneFinder()  # Initialize timezone finder
except Exception as e:
    logger.warning(f"Could not load airports database: {e}. Will use fallback timezone mapping.")
    airports = None
    tf = None

# Airline code to name mapping - loaded from external file
_AIRLINE_NAMES = None


def _load_airline_names():
    """Load airline names from external JSON file"""
    global _AIRLINE_NAMES
    if _AIRLINE_NAMES is not None:
        return _AIRLINE_NAMES
    
    # Try to load from data/airline_names.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    airline_names_file = os.path.join(current_dir, 'data', 'airline_names.json')
    
    # If not found, try relative to project root
    if not os.path.exists(airline_names_file):
        airline_names_file = os.path.join(current_dir, '..', 'data', 'airline_names.json')
        airline_names_file = os.path.normpath(airline_names_file)
    
    try:
        if os.path.exists(airline_names_file):
            with open(airline_names_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Remove comment keys
                _AIRLINE_NAMES = {k: v for k, v in data.items() if not k.startswith('_')}
                logger.debug(f"Loaded {len(_AIRLINE_NAMES)} airline names from {airline_names_file}")
        else:
            logger.warning(f"Airline names file not found: {airline_names_file}, using empty mapping")
            _AIRLINE_NAMES = {}
    except Exception as e:
        logger.warning(f"Error loading airline names from {airline_names_file}: {e}, using empty mapping")
        _AIRLINE_NAMES = {}
    
    return _AIRLINE_NAMES


def format_airline_codes(codes_str: str) -> str:
    """
    Format airline codes to include names
    
    Args:
        codes_str: Comma-separated airline codes (e.g., "LX, OS" or "LXOS")
    
    Returns:
        Formatted string with codes and names (e.g., "LX (Swiss), OS (Austrian)")
    """
    if not codes_str:
        return ""
    
    airline_names = _load_airline_names()
    
    # Handle concatenated codes like "LXOS" - split into individual 2-letter codes
    # First try to split by comma, then try to split concatenated codes
    if ',' in codes_str:
        codes = [c.strip() for c in codes_str.split(',') if c.strip()]
    else:
        # Try to split concatenated codes (e.g., "LXOS" -> ["LX", "OS"])
        # IATA codes are typically 2 letters, so split every 2 characters
        codes = []
        code_str_clean = codes_str.strip().upper()
        i = 0
        while i < len(code_str_clean):
            if i + 2 <= len(code_str_clean):
                codes.append(code_str_clean[i:i+2])
                i += 2
            else:
                # If odd number of characters, take the rest
                codes.append(code_str_clean[i:])
                break
    
    formatted = []
    for code in codes:
        code_upper = code.upper().strip()
        if not code_upper:
            continue
        
        # Check if it's a known airline code
        airline_name = airline_names.get(code_upper)
        if airline_name:
            formatted.append(f"{code_upper} ({airline_name})")
        else:
            # If not found, just show the code
            formatted.append(code_upper)
    
    return ", ".join(formatted)


class OutputFormatter:
    """Formats and outputs flight search results"""
    
    @staticmethod
    def create_flight_description(match: Dict, p1_info: Dict, p2_info: Dict) -> str:
        """
        Create a human-readable description of the flight option
        
        Args:
            match: Match dictionary with total_price, person1_price, person2_price, destination
            p1_info: Person 1 flight info dictionary
            p2_info: Person 2 flight info dictionary
        
        Returns:
            Human-readable description sentence
        """
        dest = match.get('destination', 'destination')
        total_price = match.get('total_price', 0)
        p1_price = match.get('person1_price', 0)
        p2_price = match.get('person2_price', 0)
        currency = p1_info.get('currency', 'EUR')
        
        p1_origin = p1_info.get('origin', '')
        p2_origin = p2_info.get('origin', '')
        
        # Format durations
        p1_outbound_duration = OutputFormatter.format_duration_human(p1_info.get('outbound_duration', ''))
        p1_return_duration = OutputFormatter.format_duration_human(p1_info.get('return_duration', ''))
        p2_outbound_duration = OutputFormatter.format_duration_human(p2_info.get('outbound_duration', ''))
        p2_return_duration = OutputFormatter.format_duration_human(p2_info.get('return_duration', ''))
        
        # Get stops info
        p1_outbound_stops = p1_info.get('outbound_stops', 0)
        p1_return_stops = p1_info.get('return_stops', 0)
        p2_outbound_stops = p2_info.get('outbound_stops', 0)
        p2_return_stops = p2_info.get('return_stops', 0)
        
        # Format stops as "No stops", "1 stop", "2 stops", etc.
        def format_stops(stops: int) -> str:
            if stops == 0:
                return "No stops"
            elif stops == 1:
                return "1 stop"
            else:
                return f"{stops} stops"
        
        p1_outbound_stops_str = format_stops(p1_outbound_stops)
        p1_return_stops_str = format_stops(p1_return_stops)
        p2_outbound_stops_str = format_stops(p2_outbound_stops)
        p2_return_stops_str = format_stops(p2_return_stops)
        
        # Build description
        description = f"Both people meet in {dest}. "
        description += f"Person 1 ({p1_origin}): {p1_outbound_duration} outbound ({p1_outbound_stops_str}), {p1_return_duration} return ({p1_return_stops_str}) - {p1_price:.2f} {currency}. "
        description += f"Person 2 ({p2_origin}): {p2_outbound_duration} outbound ({p2_outbound_stops_str}), {p2_return_duration} return ({p2_return_stops_str}) - {p2_price:.2f} {currency}. "
        description += f"Total: {total_price:.2f} {currency}."
        
        return description
    
    @staticmethod
    def create_skyscanner_url(origin: str, destination: str, departure_date_str: str, return_date_str: str, prefer_direct: bool = True) -> str:
        """
        Create a Skyscanner URL for a flight search
        
        Args:
            origin: IATA code of origin airport (e.g., 'TLV')
            destination: IATA code of destination airport (e.g., 'MAD')
            departure_date_str: Departure date in ISO format (e.g., '2025-11-20T17:25:00' or '2025-11-20')
            return_date_str: Return date in ISO format (e.g., '2025-11-25T12:15:00' or '2025-11-25')
            prefer_direct: Whether to prefer direct flights (default: True)
        
        Returns:
            Skyscanner URL string
        """
        try:
            # Extract date from ISO format string (handle both with and without time)
            if 'T' in departure_date_str:
                dep_date = datetime.fromisoformat(departure_date_str.replace('Z', '+00:00'))
            else:
                dep_date = datetime.strptime(departure_date_str, "%Y-%m-%d")
            
            if 'T' in return_date_str:
                ret_date = datetime.fromisoformat(return_date_str.replace('Z', '+00:00'))
            else:
                ret_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            
            # Format dates as DDMMYY (e.g., 251120 for 20 Nov 2025)
            dep_date_str = dep_date.strftime("%d%m%y")
            ret_date_str = ret_date.strftime("%d%m%y")
            
            # Convert airport codes to lowercase
            origin_lower = origin.lower()
            dest_lower = destination.lower()
            
            # Build URL
            base_url = "https://www.skyscanner.de/transport/flights"
            url = f"{base_url}/{origin_lower}/{dest_lower}/{dep_date_str}/{ret_date_str}/"
            
            # Add query parameters
            params = {
                'adultsv2': '1',
                'cabinclass': 'economy',
                'rtn': '1',
                'preferdirects': 'true' if prefer_direct else 'false'
            }
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
            
            return url
        except Exception as e:
            logger.debug(f"Error creating Skyscanner URL: {e}")
            return ""
    
    @staticmethod
    def format_duration_human(duration_str: str) -> str:
        """
        Convert ISO 8601 duration string (e.g., 'PT5H30M') to human-readable format (e.g., '5h 30m')
        
        Args:
            duration_str: ISO 8601 duration string like 'PT5H30M' or 'PT2H30M'
        
        Returns:
            Human-readable duration string like '5h 30m' or '2h 30m' or '45m'
        """
        if not duration_str or not isinstance(duration_str, str):
            return duration_str
        
        try:
            # Remove 'PT' prefix if present
            duration = duration_str.replace('PT', '')
            
            hours = 0
            minutes = 0
            
            # Extract hours
            if 'H' in duration:
                hours_str = duration.split('H')[0]
                hours = int(hours_str)
                duration = duration.split('H', 1)[1]
            
            # Extract minutes
            if 'M' in duration:
                minutes_str = duration.split('M')[0]
                minutes = int(minutes_str)
            
            # Format as human-readable
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            
            if not parts:
                return "0m"
            
            return " ".join(parts)
        except Exception as e:
            logger.debug(f"Error formatting duration '{duration_str}': {e}")
            return duration_str
    
    # Airport timezone mapping (IATA code -> timezone name)
    # Common airports and their timezones
    # Can be overridden by config file
    _AIRPORT_TIMEZONES = {
        # Person 1 origin
        'TLV': 'Asia/Jerusalem',  # Tel Aviv
        
        # Person 2 origin
        'ALC': 'Europe/Madrid',  # Alicante
        
        # Common European destinations
        'PAR': 'Europe/Paris',  # Paris
        'CDG': 'Europe/Paris',  # Paris CDG
        'ORY': 'Europe/Paris',  # Paris Orly
        'LON': 'Europe/London',  # London
        'LHR': 'Europe/London',  # London Heathrow
        'LGW': 'Europe/London',  # London Gatwick
        'MAD': 'Europe/Madrid',  # Madrid
        'BCN': 'Europe/Madrid',  # Barcelona
        'ROM': 'Europe/Rome',  # Rome
        'FCO': 'Europe/Rome',  # Rome Fiumicino
        'AMS': 'Europe/Amsterdam',  # Amsterdam
        'BER': 'Europe/Berlin',  # Berlin
        'MUC': 'Europe/Berlin',  # Munich
        'VIE': 'Europe/Vienna',  # Vienna
        'PRG': 'Europe/Prague',  # Prague
        'ATH': 'Europe/Athens',  # Athens
        'LIS': 'Europe/Lisbon',  # Lisbon
        'DUB': 'Europe/Dublin',  # Dublin
        'CPH': 'Europe/Copenhagen',  # Copenhagen
        'STO': 'Europe/Stockholm',  # Stockholm
        'OSL': 'Europe/Oslo',  # Oslo
        'MIL': 'Europe/Rome',  # Milan
        'VEN': 'Europe/Rome',  # Venice
        'NAP': 'Europe/Rome',  # Naples
        'PMO': 'Europe/Rome',  # Palermo
        'AGP': 'Europe/Madrid',  # Malaga
        'SEV': 'Europe/Madrid',  # Seville
        'ZUR': 'Europe/Zurich',  # Zurich
        'BRU': 'Europe/Brussels',  # Brussels
        'WAR': 'Europe/Warsaw',  # Warsaw
        'BUD': 'Europe/Budapest',  # Budapest
        'ZAG': 'Europe/Zagreb',  # Zagreb
        'SPL': 'Europe/Zagreb',  # Split
        'DBV': 'Europe/Zagreb',  # Dubrovnik
        'HEL': 'Europe/Helsinki',  # Helsinki
        'REK': 'Atlantic/Reykjavik',  # Reykjavik
        'OPO': 'Europe/Lisbon',  # Porto
    }
    
    @staticmethod
    def get_timezone_for_airport(airport_code: str) -> Optional[pytz.BaseTzInfo]:
        """
        Get timezone for an airport code automatically using airportsdata library.
        Falls back to hardcoded mapping if library lookup fails.
        
        Args:
            airport_code: IATA airport code (e.g., 'TLV', 'ALC')
            
        Returns:
            pytz timezone object or None if not found
        """
        airport_code_upper = airport_code.upper()
        
        # Try automatic detection using airportsdata library + timezonefinder
        if airports is not None and tf is not None:
            try:
                airport_info = airports.get(airport_code_upper)
                if airport_info:
                    # Get coordinates from airport data
                    lat = airport_info.get('lat')
                    lon = airport_info.get('lon')
                    
                    if lat is not None and lon is not None:
                        # Use timezonefinder to get timezone from coordinates
                        timezone_name = tf.timezone_at(lat=lat, lng=lon)
                        if timezone_name:
                            try:
                                tz = pytz.timezone(timezone_name)
                                logger.debug(f"Auto-detected timezone for {airport_code_upper}: {timezone_name}")
                                return tz
                            except pytz.exceptions.UnknownTimeZoneError:
                                logger.debug(f"Unknown timezone '{timezone_name}' for {airport_code_upper}, trying fallback")
                        else:
                            logger.debug(f"Could not determine timezone from coordinates for {airport_code_upper}")
                    else:
                        logger.debug(f"Airport {airport_code_upper} missing coordinates")
            except (KeyError, AttributeError, TypeError) as e:
                logger.debug(f"Airport {airport_code_upper} not found in airports database: {e}")
        
        # Fallback to hardcoded mapping if automatic detection fails
        timezone_name = OutputFormatter._AIRPORT_TIMEZONES.get(airport_code_upper)
        if timezone_name:
            try:
                tz = pytz.timezone(timezone_name)
                logger.debug(f"Using fallback timezone for {airport_code_upper}: {timezone_name}")
                return tz
            except pytz.exceptions.UnknownTimeZoneError:
                logger.warning(f"Invalid timezone '{timezone_name}' in fallback mapping for {airport_code_upper}")
                return None
        
        logger.warning(f"Could not determine timezone for airport {airport_code_upper}")
        return None
    
    @staticmethod
    def convert_to_local_time(utc_time_str: str, airport_code: str) -> str:
        """
        Convert UTC time string to local time for a given airport
        
        Args:
            utc_time_str: UTC time in ISO 8601 format (e.g., "2025-11-20T14:35:00")
            airport_code: IATA airport code
            
        Returns:
            Local time string in format "YYYY-MM-DD HH:MM (Timezone)" or original if conversion fails
        """
        if not utc_time_str or utc_time_str == 'N/A':
            return utc_time_str
        
        try:
            # Parse UTC time (Amadeus API returns times in ISO 8601 format)
            # Handle both with and without timezone info
            if 'T' in utc_time_str:
                if '+' in utc_time_str or utc_time_str.endswith('Z'):
                    # Has timezone info
                    dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
                else:
                    # No timezone info, assume UTC
                    dt = datetime.fromisoformat(utc_time_str)
                    dt = pytz.UTC.localize(dt)
            else:
                return utc_time_str
            
            # Get timezone for airport
            tz = OutputFormatter.get_timezone_for_airport(airport_code)
            if tz:
                # Convert to local time
                local_dt = dt.astimezone(tz)
                # Format: "2025-11-20 16:35 (Asia/Jerusalem)"
                timezone_name = str(tz).split('/')[-1]  # Get city name from timezone
                return f"{local_dt.strftime('%Y-%m-%d %H:%M')} ({timezone_name})"
            else:
                # No timezone found, return UTC time
                return f"{dt.strftime('%Y-%m-%d %H:%M')} (UTC)"
        except Exception as e:
            # If conversion fails, return original
            return utc_time_str
    
    @staticmethod
    def format_flight_info(flight: Dict) -> Dict:
        """Extract key information from a flight offer"""
        try:
            outbound = flight.get('itineraries', [{}])[0]
            return_trip = flight.get('itineraries', [{}])[1] if len(flight.get('itineraries', [])) > 1 else {}
            
            # Outbound info
            outbound_segments = outbound.get('segments', [])
            outbound_dep = outbound_segments[0].get('departure', {}) if outbound_segments else {}
            outbound_arr = outbound_segments[-1].get('arrival', {}) if outbound_segments else {}
            
            # Get origin and destination codes
            origin_code = outbound_dep.get('iataCode', '') if outbound_dep else ''
            destination_code = outbound_arr.get('iataCode', '') if outbound_arr else ''
            
            # Return info
            return_segments = return_trip.get('segments', [])
            return_dep = return_segments[0].get('departure', {}) if return_segments else {}
            return_arr = return_segments[-1].get('arrival', {}) if return_segments else {}
            
            # Calculate duration
            outbound_duration = outbound.get('duration', '')
            return_duration = return_trip.get('duration', '')
            
            # Get stops
            outbound_stops = sum(seg.get('numberOfStops', 0) for seg in outbound_segments)
            return_stops = sum(seg.get('numberOfStops', 0) for seg in return_segments)
            
            return {
                'price': flight.get('price', {}).get('total', 'N/A'),
                'currency': flight.get('price', {}).get('currency', 'EUR'),
                'origin': origin_code,
                'destination': destination_code,
                'route': f"{origin_code} → {destination_code}" if origin_code and destination_code else 'N/A',
                'outbound_departure': outbound_dep.get('at', 'N/A'),
                'outbound_arrival': outbound_arr.get('at', 'N/A'),
                'outbound_duration': outbound_duration,
                'outbound_stops': outbound_stops,
                'return_departure': return_dep.get('at', 'N/A'),
                'return_arrival': return_arr.get('at', 'N/A'),
                'return_duration': return_duration,
                'return_stops': return_stops,
                'airlines': ', '.join(set(
                    seg.get('carrierCode', '') for seg in outbound_segments + return_segments
                )),
                'airlines_formatted': format_airline_codes(', '.join(set(
                    seg.get('carrierCode', '') for seg in outbound_segments + return_segments
                )))
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def print_console(results: List[Dict]):
        """Print results to console"""
        if not results:
            print("\n❌ No matching flights found.")
            return
        
        print(f"\n✅ Found {len(results)} matching flight option(s):\n")
        print("=" * 100)
        
        for i, match in enumerate(results, 1):
            dest = match['destination']
            total_price = match['total_price']
            p1_price = match['person1_price']
            p2_price = match['person2_price']
            
            p1_info = OutputFormatter.format_flight_info(match['person1_flight'])
            p2_info = OutputFormatter.format_flight_info(match['person2_flight'])
            
            print(f"\n📍 Option {i}: Destination {dest}")
            print(f"💰 Total Price: {total_price:.2f} {p1_info.get('currency', 'EUR')} "
                  f"(Person 1: {p1_price:.2f}, Person 2: {p2_price:.2f})")
            print("-" * 100)
            
            # Person 1 details
            p1_origin_code = p1_info.get('origin', 'TLV')
            print(f"\n👤 Person 1 ({p1_origin_code} → {dest}):")
            p1_outbound_duration_human = OutputFormatter.format_duration_human(p1_info.get('outbound_duration', ''))
            p1_return_duration_human = OutputFormatter.format_duration_human(p1_info.get('return_duration', ''))
            print(f"   Outbound: {p1_info.get('outbound_departure', 'N/A')} → {p1_info.get('outbound_arrival', 'N/A')} "
                  f"({p1_outbound_duration_human}, {p1_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p1_info.get('return_departure', 'N/A')} → {p1_info.get('return_arrival', 'N/A')} "
                  f"({p1_return_duration_human}, {p1_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p1_info.get('airlines_formatted', p1_info.get('airlines', 'N/A'))}")
            print(f"   Price: {p1_price:.2f} {p1_info.get('currency', 'EUR')}")
            
            # Person 2 details
            p2_origin_code = p2_info.get('origin', 'ALC')
            print(f"\n👤 Person 2 ({p2_origin_code} → {dest}):")
            p2_outbound_duration_human = OutputFormatter.format_duration_human(p2_info.get('outbound_duration', ''))
            p2_return_duration_human = OutputFormatter.format_duration_human(p2_info.get('return_duration', ''))
            print(f"   Outbound: {p2_info.get('outbound_departure', 'N/A')} → {p2_info.get('outbound_arrival', 'N/A')} "
                  f"({p2_outbound_duration_human}, {p2_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p2_info.get('return_departure', 'N/A')} → {p2_info.get('return_arrival', 'N/A')} "
                  f"({p2_return_duration_human}, {p2_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p2_info.get('airlines_formatted', p2_info.get('airlines', 'N/A'))}")
            print(f"   Price: {p2_price:.2f} {p2_info.get('currency', 'EUR')}")
            
            print("=" * 100)
    
    @staticmethod
    def export_csv(results: List[Dict], filename: str):
        """Export results to CSV file with clear route and price information"""
        if not results:
            print("No results to export.")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Simplified, clear fieldnames with route and price first
                fieldnames = [
                    # First column: Route (From → To) - MOST IMPORTANT
                    'route',
                    # Second column: Human-readable description
                    'description',
                    'destination',
                    'total_price_eur',
                    'price_person1_eur',
                    'price_person2_eur',
                    'currency',
                    
                    # Person 1 details - with UTC and local times
                    'person1_route',
                    'person1_price_eur',
                    'person1_outbound_departure_utc',
                    'person1_outbound_departure_local',
                    'person1_outbound_arrival_utc',
                    'person1_outbound_arrival_local',
                    'person1_outbound_duration',
                    'person1_outbound_stops',
                    'person1_return_departure_utc',
                    'person1_return_departure_local',
                    'person1_return_arrival_utc',
                    'person1_return_arrival_local',
                    'person1_return_duration',
                    'person1_return_stops',
                    'person1_airlines',
                    
                    # Person 2 details - with UTC and local times
                    'person2_route',
                    'person2_price_eur',
                    'person2_outbound_departure_utc',
                    'person2_outbound_departure_local',
                    'person2_outbound_arrival_utc',
                    'person2_outbound_arrival_local',
                    'person2_outbound_duration',
                    'person2_outbound_stops',
                    'person2_return_departure_utc',
                    'person2_return_departure_local',
                    'person2_return_arrival_utc',
                    'person2_return_arrival_local',
                    'person2_return_duration',
                    'person2_return_stops',
                    'person2_airlines'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, match in enumerate(results, 1):
                    p1_info = OutputFormatter.format_flight_info(match['person1_flight'])
                    p2_info = OutputFormatter.format_flight_info(match['person2_flight'])
                    
                    dest = match['destination']
                    p1_origin = p1_info.get('origin', 'TLV')
                    p2_origin = p2_info.get('origin', 'ALC')
                    
                    # Get return routes from flight segments
                    p1_return_origin = dest
                    p1_return_dest = p1_origin
                    p2_return_origin = dest
                    p2_return_dest = p2_origin
                    
                    try:
                        p1_return_segments = match['person1_flight'].get('itineraries', [{}])[1].get('segments', [])
                        if p1_return_segments:
                            p1_return_origin = p1_return_segments[0].get('departure', {}).get('iataCode', dest)
                            p1_return_dest = p1_return_segments[-1].get('arrival', {}).get('iataCode', p1_origin)
                    except:
                        pass
                    
                    try:
                        p2_return_segments = match['person2_flight'].get('itineraries', [{}])[1].get('segments', [])
                        if p2_return_segments:
                            p2_return_origin = p2_return_segments[0].get('departure', {}).get('iataCode', dest)
                            p2_return_dest = p2_return_segments[-1].get('arrival', {}).get('iataCode', p2_origin)
                    except:
                        pass
                    
                    # Main route: both people going to same destination
                    main_route = f"{p1_origin} & {p2_origin} → {dest}"
                    
                    # Convert times to local timezones
                    # Person 1: TLV (Tel Aviv) timezone
                    p1_outbound_dep_utc = p1_info.get('outbound_departure', '')
                    p1_outbound_dep_local = OutputFormatter.convert_to_local_time(p1_outbound_dep_utc, p1_origin)
                    p1_outbound_arr_utc = p1_info.get('outbound_arrival', '')
                    p1_outbound_arr_local = OutputFormatter.convert_to_local_time(p1_outbound_arr_utc, dest)
                    p1_return_dep_utc = p1_info.get('return_departure', '')
                    p1_return_dep_local = OutputFormatter.convert_to_local_time(p1_return_dep_utc, dest)
                    p1_return_arr_utc = p1_info.get('return_arrival', '')
                    p1_return_arr_local = OutputFormatter.convert_to_local_time(p1_return_arr_utc, p1_origin)
                    
                    # Person 2: ALC (Alicante) timezone
                    p2_outbound_dep_utc = p2_info.get('outbound_departure', '')
                    p2_outbound_dep_local = OutputFormatter.convert_to_local_time(p2_outbound_dep_utc, p2_origin)
                    p2_outbound_arr_utc = p2_info.get('outbound_arrival', '')
                    p2_outbound_arr_local = OutputFormatter.convert_to_local_time(p2_outbound_arr_utc, dest)
                    p2_return_dep_utc = p2_info.get('return_departure', '')
                    p2_return_dep_local = OutputFormatter.convert_to_local_time(p2_return_dep_utc, dest)
                    p2_return_arr_utc = p2_info.get('return_arrival', '')
                    p2_return_arr_local = OutputFormatter.convert_to_local_time(p2_return_arr_utc, p2_origin)
                    
                    # Format durations to human-readable format
                    p1_outbound_duration_human = OutputFormatter.format_duration_human(p1_info.get('outbound_duration', ''))
                    p1_return_duration_human = OutputFormatter.format_duration_human(p1_info.get('return_duration', ''))
                    p2_outbound_duration_human = OutputFormatter.format_duration_human(p2_info.get('outbound_duration', ''))
                    p2_return_duration_human = OutputFormatter.format_duration_human(p2_info.get('return_duration', ''))
                    
                    # Format stops as "No stops", "1 stop", "2 stops", etc.
                    def format_stops(stops: int) -> str:
                        if stops == 0:
                            return "No stops"
                        elif stops == 1:
                            return "1 stop"
                        else:
                            return f"{stops} stops"
                    
                    p1_outbound_stops = p1_info.get('outbound_stops', 0)
                    p1_return_stops = p1_info.get('return_stops', 0)
                    p2_outbound_stops = p2_info.get('outbound_stops', 0)
                    p2_return_stops = p2_info.get('return_stops', 0)
                    
                    p1_outbound_stops_str = format_stops(p1_outbound_stops)
                    p1_return_stops_str = format_stops(p1_return_stops)
                    p2_outbound_stops_str = format_stops(p2_outbound_stops)
                    p2_return_stops_str = format_stops(p2_return_stops)
                    
                    # Create human-readable description
                    description = OutputFormatter.create_flight_description(match, p1_info, p2_info)
                    
                    row = {
                        # First column: Clear route description
                        'route': main_route,
                        # Second column: Human-readable description
                        'description': description,
                        'destination': dest,
                        'total_price_eur': f"{match['total_price']:.2f}",
                        'price_person1_eur': f"{match['person1_price']:.2f}",
                        'price_person2_eur': f"{match['person2_price']:.2f}",
                        'currency': p1_info.get('currency', 'EUR'),
                        
                        # Person 1 - with local times (using correct airport timezones)
                        'person1_route': f"{p1_origin} → {dest} (outbound), {p1_return_origin} → {p1_return_dest} (return)",
                        'person1_price_eur': f"{match['person1_price']:.2f}",
                        'person1_outbound_departure_utc': p1_outbound_dep_utc,
                        'person1_outbound_departure_local': p1_outbound_dep_local,  # Local time at origin airport
                        'person1_outbound_arrival_utc': p1_outbound_arr_utc,
                        'person1_outbound_arrival_local': p1_outbound_arr_local,  # Local time at destination airport
                        'person1_outbound_duration': p1_outbound_duration_human,
                        'person1_outbound_stops': p1_outbound_stops_str,
                        'person1_return_departure_utc': p1_return_dep_utc,
                        'person1_return_departure_local': p1_return_dep_local,  # Local time at destination airport
                        'person1_return_arrival_utc': p1_return_arr_utc,
                        'person1_return_arrival_local': p1_return_arr_local,  # Local time at origin airport
                        'person1_return_duration': p1_return_duration_human,
                        'person1_return_stops': p1_return_stops_str,
                        'person1_airlines': p1_info.get('airlines_formatted', p1_info.get('airlines', '')),
                        
                        # Person 2 - with local times (using correct airport timezones)
                        'person2_route': f"{p2_origin} → {dest} (outbound), {p2_return_origin} → {p2_return_dest} (return)",
                        'person2_price_eur': f"{match['person2_price']:.2f}",
                        'person2_outbound_departure_utc': p2_outbound_dep_utc,
                        'person2_outbound_departure_local': p2_outbound_dep_local,  # Local time at origin airport
                        'person2_outbound_arrival_utc': p2_outbound_arr_utc,
                        'person2_outbound_arrival_local': p2_outbound_arr_local,  # Local time at destination airport
                        'person2_outbound_duration': p2_outbound_duration_human,
                        'person2_outbound_stops': p2_outbound_stops_str,
                        'person2_return_departure_utc': p2_return_dep_utc,
                        'person2_return_departure_local': p2_return_dep_local,  # Local time at destination airport
                        'person2_return_arrival_utc': p2_return_arr_utc,
                        'person2_return_arrival_local': p2_return_arr_local,  # Local time at origin airport
                        'person2_return_duration': p2_return_duration_human,
                        'person2_return_stops': p2_return_stops_str,
                        'person2_airlines': p2_info.get('airlines_formatted', p2_info.get('airlines', ''))
                    }
                    
                    writer.writerow(row)
            
            print(f"\n✅ Results exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            import traceback
            traceback.print_exc()

