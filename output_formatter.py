"""
Output formatting module for flight results
"""
from typing import List, Dict, Optional
from datetime import datetime
import csv
import os
import pytz


class OutputFormatter:
    """Formats and outputs flight search results"""
    
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
    
    # Class variable to store custom timezones from config
    _custom_timezones = {}
    
    @classmethod
    def set_custom_timezones(cls, timezone_config: Dict[str, str]):
        """Set custom timezones from config file"""
        cls._custom_timezones = timezone_config or {}
    
    @staticmethod
    def get_timezone_for_airport(airport_code: str) -> Optional[pytz.BaseTzInfo]:
        """Get timezone for an airport code"""
        # First check custom timezones from config, then defaults
        timezone_name = OutputFormatter._custom_timezones.get(airport_code.upper()) or \
                       OutputFormatter._AIRPORT_TIMEZONES.get(airport_code.upper())
        if timezone_name:
            try:
                return pytz.timezone(timezone_name)
            except:
                return None
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
                ))
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
            print(f"   Outbound: {p1_info.get('outbound_departure', 'N/A')} → {p1_info.get('outbound_arrival', 'N/A')} "
                  f"({p1_info.get('outbound_duration', 'N/A')}, {p1_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p1_info.get('return_departure', 'N/A')} → {p1_info.get('return_arrival', 'N/A')} "
                  f"({p1_info.get('return_duration', 'N/A')}, {p1_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p1_info.get('airlines', 'N/A')}")
            print(f"   Price: {p1_price:.2f} {p1_info.get('currency', 'EUR')}")
            
            # Person 2 details
            p2_origin_code = p2_info.get('origin', 'ALC')
            print(f"\n👤 Person 2 ({p2_origin_code} → {dest}):")
            print(f"   Outbound: {p2_info.get('outbound_departure', 'N/A')} → {p2_info.get('outbound_arrival', 'N/A')} "
                  f"({p2_info.get('outbound_duration', 'N/A')}, {p2_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p2_info.get('return_departure', 'N/A')} → {p2_info.get('return_arrival', 'N/A')} "
                  f"({p2_info.get('return_duration', 'N/A')}, {p2_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p2_info.get('airlines', 'N/A')}")
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
                    'destination',
                    'total_price_eur',
                    'price_person1_eur',
                    'price_person2_eur',
                    'currency',
                    
                    # Person 1 details - with UTC and local times
                    'person1_route',
                    'person1_price_eur',
                    'person1_outbound_departure_utc',
                    'person1_outbound_departure_local_tlv',
                    'person1_outbound_arrival_utc',
                    'person1_outbound_arrival_local_dest',
                    'person1_outbound_duration',
                    'person1_return_departure_utc',
                    'person1_return_departure_local_dest',
                    'person1_return_arrival_utc',
                    'person1_return_arrival_local_tlv',
                    'person1_return_duration',
                    'person1_airlines',
                    
                    # Person 2 details - with UTC and local times
                    'person2_route',
                    'person2_price_eur',
                    'person2_outbound_departure_utc',
                    'person2_outbound_departure_local_alc',
                    'person2_outbound_arrival_utc',
                    'person2_outbound_arrival_local_dest',
                    'person2_outbound_duration',
                    'person2_return_departure_utc',
                    'person2_return_departure_local_dest',
                    'person2_return_arrival_utc',
                    'person2_return_arrival_local_alc',
                    'person2_return_duration',
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
                    
                    row = {
                        # First column: Clear route description
                        'route': main_route,
                        'destination': dest,
                        'total_price_eur': f"{match['total_price']:.2f}",
                        'price_person1_eur': f"{match['person1_price']:.2f}",
                        'price_person2_eur': f"{match['person2_price']:.2f}",
                        'currency': p1_info.get('currency', 'EUR'),
                        
                        # Person 1 - with local times
                        'person1_route': f"{p1_origin} → {dest} (outbound), {p1_return_origin} → {p1_return_dest} (return)",
                        'person1_price_eur': f"{match['person1_price']:.2f}",
                        'person1_outbound_departure_utc': p1_outbound_dep_utc,
                        'person1_outbound_departure_local_tlv': p1_outbound_dep_local,
                        'person1_outbound_arrival_utc': p1_outbound_arr_utc,
                        'person1_outbound_arrival_local_dest': p1_outbound_arr_local,
                        'person1_outbound_duration': p1_info.get('outbound_duration', ''),
                        'person1_return_departure_utc': p1_return_dep_utc,
                        'person1_return_departure_local_dest': p1_return_dep_local,
                        'person1_return_arrival_utc': p1_return_arr_utc,
                        'person1_return_arrival_local_tlv': p1_return_arr_local,
                        'person1_return_duration': p1_info.get('return_duration', ''),
                        'person1_airlines': p1_info.get('airlines', ''),
                        
                        # Person 2 - with local times
                        'person2_route': f"{p2_origin} → {dest} (outbound), {p2_return_origin} → {p2_return_dest} (return)",
                        'person2_price_eur': f"{match['person2_price']:.2f}",
                        'person2_outbound_departure_utc': p2_outbound_dep_utc,
                        'person2_outbound_departure_local_alc': p2_outbound_dep_local,
                        'person2_outbound_arrival_utc': p2_outbound_arr_utc,
                        'person2_outbound_arrival_local_dest': p2_outbound_arr_local,
                        'person2_outbound_duration': p2_info.get('outbound_duration', ''),
                        'person2_return_departure_utc': p2_return_dep_utc,
                        'person2_return_departure_local_dest': p2_return_dep_local,
                        'person2_return_arrival_utc': p2_return_arr_utc,
                        'person2_return_arrival_local_alc': p2_return_arr_local,
                        'person2_return_duration': p2_info.get('return_duration', ''),
                        'person2_airlines': p2_info.get('airlines', '')
                    }
                    
                    writer.writerow(row)
            
            print(f"\n✅ Results exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            import traceback
            traceback.print_exc()

