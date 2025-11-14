"""
Output formatting module for flight results
"""
from typing import List, Dict
from datetime import datetime
import csv
import os


class OutputFormatter:
    """Formats and outputs flight search results"""
    
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
            print(f"\n👤 Person 1 (Tel Aviv → {dest}):")
            print(f"   Outbound: {p1_info.get('outbound_departure', 'N/A')} → {p1_info.get('outbound_arrival', 'N/A')} "
                  f"({p1_info.get('outbound_duration', 'N/A')}, {p1_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p1_info.get('return_departure', 'N/A')} → {p1_info.get('return_arrival', 'N/A')} "
                  f"({p1_info.get('return_duration', 'N/A')}, {p1_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p1_info.get('airlines', 'N/A')}")
            print(f"   Price: {p1_price:.2f} {p1_info.get('currency', 'EUR')}")
            
            # Person 2 details
            print(f"\n👤 Person 2 (Alicante → {dest}):")
            print(f"   Outbound: {p2_info.get('outbound_departure', 'N/A')} → {p2_info.get('outbound_arrival', 'N/A')} "
                  f"({p2_info.get('outbound_duration', 'N/A')}, {p2_info.get('outbound_stops', 0)} stops)")
            print(f"   Return:   {p2_info.get('return_departure', 'N/A')} → {p2_info.get('return_arrival', 'N/A')} "
                  f"({p2_info.get('return_duration', 'N/A')}, {p2_info.get('return_stops', 0)} stops)")
            print(f"   Airlines: {p2_info.get('airlines', 'N/A')}")
            print(f"   Price: {p2_price:.2f} {p2_info.get('currency', 'EUR')}")
            
            print("=" * 100)
    
    @staticmethod
    def export_csv(results: List[Dict], filename: str):
        """Export results to CSV file"""
        if not results:
            print("No results to export.")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'option', 'destination', 'total_price', 'currency',
                    'person1_price', 'person1_outbound_dep', 'person1_outbound_arr',
                    'person1_outbound_duration', 'person1_outbound_stops',
                    'person1_return_dep', 'person1_return_arr',
                    'person1_return_duration', 'person1_return_stops',
                    'person1_airlines',
                    'person2_price', 'person2_outbound_dep', 'person2_outbound_arr',
                    'person2_outbound_duration', 'person2_outbound_stops',
                    'person2_return_dep', 'person2_return_arr',
                    'person2_return_duration', 'person2_return_stops',
                    'person2_airlines'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, match in enumerate(results, 1):
                    p1_info = OutputFormatter.format_flight_info(match['person1_flight'])
                    p2_info = OutputFormatter.format_flight_info(match['person2_flight'])
                    
                    row = {
                        'option': i,
                        'destination': match['destination'],
                        'total_price': match['total_price'],
                        'currency': p1_info.get('currency', 'EUR'),
                        'person1_price': match['person1_price'],
                        'person1_outbound_dep': p1_info.get('outbound_departure', ''),
                        'person1_outbound_arr': p1_info.get('outbound_arrival', ''),
                        'person1_outbound_duration': p1_info.get('outbound_duration', ''),
                        'person1_outbound_stops': p1_info.get('outbound_stops', 0),
                        'person1_return_dep': p1_info.get('return_departure', ''),
                        'person1_return_arr': p1_info.get('return_arrival', ''),
                        'person1_return_duration': p1_info.get('return_duration', ''),
                        'person1_return_stops': p1_info.get('return_stops', 0),
                        'person1_airlines': p1_info.get('airlines', ''),
                        'person2_price': match['person2_price'],
                        'person2_outbound_dep': p2_info.get('outbound_departure', ''),
                        'person2_outbound_arr': p2_info.get('outbound_arrival', ''),
                        'person2_outbound_duration': p2_info.get('outbound_duration', ''),
                        'person2_outbound_stops': p2_info.get('outbound_stops', 0),
                        'person2_return_dep': p2_info.get('return_departure', ''),
                        'person2_return_arr': p2_info.get('return_arrival', ''),
                        'person2_return_duration': p2_info.get('return_duration', ''),
                        'person2_return_stops': p2_info.get('return_stops', 0),
                        'person2_airlines': p2_info.get('airlines', '')
                    }
                    
                    writer.writerow(row)
            
            print(f"\n✅ Results exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")

