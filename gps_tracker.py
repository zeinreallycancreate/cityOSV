#!/usr/bin/env python3
"""
GPS Tracker Module
Handles GPS data collection, location tracking, and Google Maps integration
"""

import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, List
import logging

try:
    from gps3 import gps3
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("Warning: GPS module not available. Using simulated mode.")

try:
    import googlemaps
    GMAPS_AVAILABLE = True
except ImportError:
    GMAPS_AVAILABLE = False
    print("Warning: Google Maps module not available.")

from network_manager import NetworkManager


class GPSTracker:
    """Handles GPS tracking and location data collection"""
    
    def __init__(self, config_path="config.json", data_dir="data"):
        self.config = self._load_config(config_path)
        self.data_dir = data_dir
        self.gmaps_client = None
        self.current_location = None
        self.logger = self._setup_logger()
        
        # Initialize network manager for offline operation
        self.network_manager = NetworkManager()
        
        # Initialize Google Maps client (only if online)
        self._init_google_maps()
        
        # Initialize GPS
        if GPS_AVAILABLE:
            self.gps_socket = gps3.GPSDSocket()
            self.data_stream = gps3.DataStream()
        else:
            self.gps_socket = None
            self.data_stream = None
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Offline cache
        self.offline_cache_file = os.path.join(self.data_dir, 'offline_cache.json')
        self.offline_cache = self._load_offline_cache()
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('GPSTracker')
        logger.setLevel(logging.INFO)
        
        # File handler
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/gps_tracker.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _load_config(self, config_path):
        """Load configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _init_google_maps(self):
        """Initialize Google Maps client (only if online)"""
        if not GMAPS_AVAILABLE:
            self.logger.warning("Google Maps module not available")
            return
        
        # Check if online
        if not self.network_manager.check_connectivity():
            self.logger.info("Offline mode - Google Maps will be initialized when online")
            return
        
        api_key = self.config.get('google_maps_api_key')
        if api_key:
            try:
                self.gmaps_client = googlemaps.Client(key=api_key)
                self.logger.info("Google Maps client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Google Maps: {e}")
        else:
            self.logger.warning("No Google Maps API key found in config - offline mode only")
    
    def get_current_location(self) -> Optional[Dict]:
        """Get current GPS location"""
        if not GPS_AVAILABLE or not self.gps_socket:
            # Simulated location for testing
            return self._get_simulated_location()
        
        try:
            self.gps_socket.watch()
            for new_data in self.gps_socket:
                if new_data:
                    self.data_stream.unpack(new_data)
                    
                    lat = self.data_stream.TPV['lat']
                    lon = self.data_stream.TPV['lon']
                    
                    if lat != 'n/a' and lon != 'n/a':
                        location = {
                            'latitude': float(lat),
                            'longitude': float(lon),
                            'altitude': self.data_stream.TPV['alt'],
                            'speed': self.data_stream.TPV['speed'],
                            'timestamp': datetime.now().isoformat()
                        }
                        self.current_location = location
                        return location
        except Exception as e:
            self.logger.error(f"Error reading GPS data: {e}")
            return None
        
        return None
    
    def _get_simulated_location(self) -> Dict:
        """Get simulated location for testing"""
        # Simulate movement by slightly changing coordinates
        if self.current_location:
            lat = self.current_location['latitude'] + 0.0001
            lon = self.current_location['longitude'] + 0.0001
        else:
            # Default starting location (example: San Francisco)
            lat = 37.7749
            lon = -122.4194
        
        location = {
            'latitude': lat,
            'longitude': lon,
            'altitude': 50.0,
            'speed': 15.0,
            'timestamp': datetime.now().isoformat(),
            'simulated': True
        }
        self.current_location = location
        return location
    
    def _load_offline_cache(self) -> Dict:
        """Load offline cache of previously fetched data"""
        if os.path.exists(self.offline_cache_file):
            try:
                with open(self.offline_cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load offline cache: {e}")
        return {'addresses': {}, 'places': {}}
    
    def _save_offline_cache(self):
        """Save offline cache to disk"""
        try:
            with open(self.offline_cache_file, 'w') as f:
                json.dump(self.offline_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save offline cache: {e}")
    
    def _get_cached_or_queue(self, operation_type: str, location: Dict, 
                            online_func, *args, **kwargs) -> Optional[Dict]:
        """
        Try to get cached data, or queue operation if offline
        
        Args:
            operation_type: Type of operation
            location: Location data
            online_func: Function to call when online
            *args, **kwargs: Arguments for the function
        
        Returns:
            Cached data or None if not available
        """
        # Create cache key
        cache_key = f"{location['latitude']:.4f},{location['longitude']:.4f}"
        
        # Check if we have cached data
        cache_section = operation_type.replace('_', 's')  # e.g., 'reverse_geocode' -> 'reverse_geocodes'
        if cache_section not in self.offline_cache:
            self.offline_cache[cache_section] = {}
        
        if cache_key in self.offline_cache[cache_section]:
            self.logger.debug(f"Using cached data for {operation_type}")
            return self.offline_cache[cache_section][cache_key]
        
        # Check if online
        if not self.network_manager.check_connectivity() or not self.gmaps_client:
            # Queue for later processing
            self.logger.info(f"Offline - queuing {operation_type} operation")
            self.network_manager.queue_operation(
                operation_type,
                {
                    'location': location,
                    'args': args,
                    'kwargs': kwargs
                }
            )
            return None
        
        # We're online, execute the operation
        try:
            result = online_func(*args, **kwargs)
            if result:
                # Cache the result
                self.offline_cache[cache_section][cache_key] = result
                self._save_offline_cache()
            return result
        except Exception as e:
            self.logger.error(f"Error in {operation_type}: {e}")
            # Queue for retry
            self.network_manager.queue_operation(operation_type, {
                'location': location,
                'args': args,
                'kwargs': kwargs
            })
            return None
    
    def get_nearby_places(self, location: Dict, radius: int = 500) -> List[Dict]:
        """
        Get nearby places using Google Maps API (with offline support)
        
        Args:
            location: Dictionary with latitude and longitude
            radius: Search radius in meters (default: 500m)
        
        Returns:
            List of nearby places with details
        """
        def _fetch_places():
            if not self.gmaps_client:
                return []
            
            lat = location['latitude']
            lon = location['longitude']
            
            places_result = self.gmaps_client.places_nearby(
                location=(lat, lon),
                radius=radius
            )
            
            places = []
            for place in places_result.get('results', []):
                place_info = {
                    'name': place.get('name'),
                    'place_id': place.get('place_id'),
                    'types': place.get('types', []),
                    'vicinity': place.get('vicinity'),
                    'rating': place.get('rating'),
                    'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                    'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
                    'timestamp': datetime.now().isoformat()
                }
                places.append(place_info)
            
            self.logger.info(f"Found {len(places)} nearby places")
            return places
        
        result = self._get_cached_or_queue('nearby_places', location, _fetch_places)
        return result if result else []
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place
        
        Args:
            place_id: Google Maps place ID
        
        Returns:
            Detailed place information
        """
        if not self.gmaps_client:
            return None
        
        try:
            place_details = self.gmaps_client.place(place_id)
            result = place_details.get('result', {})
            
            details = {
                'name': result.get('name'),
                'formatted_address': result.get('formatted_address'),
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website'),
                'types': result.get('types', []),
                'rating': result.get('rating'),
                'price_level': result.get('price_level'),
                'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'reviews_count': result.get('user_ratings_total'),
                'timestamp': datetime.now().isoformat()
            }
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error fetching place details: {e}")
            return None
    
    def reverse_geocode(self, location: Dict) -> Optional[Dict]:
        """
        Get address and area information from coordinates (with offline support)
        
        Args:
            location: Dictionary with latitude and longitude
        
        Returns:
            Address information and area context
        """
        def _fetch_address():
            if not self.gmaps_client:
                return None
            
            lat = location['latitude']
            lon = location['longitude']
            
            result = self.gmaps_client.reverse_geocode((lat, lon))
            
            if result:
                address_components = result[0]
                
                address_info = {
                    'formatted_address': address_components.get('formatted_address'),
                    'place_id': address_components.get('place_id'),
                    'types': address_components.get('types', []),
                    'components': {},
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract address components
                for component in address_components.get('address_components', []):
                    types = component.get('types', [])
                    name = component.get('long_name')
                    
                    if 'locality' in types:
                        address_info['components']['city'] = name
                    elif 'administrative_area_level_1' in types:
                        address_info['components']['state'] = name
                    elif 'country' in types:
                        address_info['components']['country'] = name
                    elif 'postal_code' in types:
                        address_info['components']['postal_code'] = name
                    elif 'route' in types:
                        address_info['components']['street'] = name
                    elif 'neighborhood' in types:
                        address_info['components']['neighborhood'] = name
                
                return address_info
            return None
        
        return self._get_cached_or_queue('reverse_geocode', location, _fetch_address)
    
    def analyze_current_context(self, location: Dict) -> Dict:
        """
        Analyze the current location context (works offline with cached data)
        
        Args:
            location: Current GPS location
        
        Returns:
            Comprehensive context about the current location
        """
        context = {
            'location': location,
            'address': None,
            'nearby_places': [],
            'area_type': None,
            'timestamp': datetime.now().isoformat(),
            'offline_mode': not self.network_manager.is_online
        }
        
        # Get address information (cached or queued)
        address_info = self.reverse_geocode(location)
        if address_info:
            context['address'] = address_info
        
        # Get nearby places (cached or queued)
        nearby = self.get_nearby_places(location, radius=500)
        context['nearby_places'] = nearby
        
        # Analyze area type based on nearby places
        if nearby:
            types_count = {}
            for place in nearby:
                for place_type in place.get('types', []):
                    types_count[place_type] = types_count.get(place_type, 0) + 1
            
            # Determine dominant area type
            if types_count:
                dominant_type = max(types_count.items(), key=lambda x: x[1])
                context['area_type'] = dominant_type[0]
                context['area_characteristics'] = types_count
        
        return context
    
    def process_queued_operations(self):
        """
        Process all queued operations when WiFi becomes available
        """
        if not self.network_manager.check_connectivity():
            self.logger.info("Still offline, cannot process queue")
            return
        
        # Re-initialize Google Maps client if needed
        if not self.gmaps_client:
            self._init_google_maps()
        
        if not self.gmaps_client:
            self.logger.warning("Cannot process queue without Google Maps client")
            return
        
        queued_ops = self.network_manager.get_queued_operations()
        
        if not queued_ops:
            self.logger.info("No queued operations to process")
            return
        
        self.logger.info(f"Processing {len(queued_ops)} queued operations...")
        
        processed = 0
        failed = 0
        
        for op in queued_ops:
            try:
                op_type = op['type']
                op_data = op['data']
                location = op_data.get('location')
                
                if op_type == 'reverse_geocode':
                    result = self.reverse_geocode(location)
                    if result:
                        self.logger.info(f"✓ Processed reverse_geocode for {location['latitude']:.4f},{location['longitude']:.4f}")
                        self.network_manager.mark_operation_complete(op['id'])
                        processed += 1
                    else:
                        raise Exception("Failed to reverse geocode")
                
                elif op_type == 'nearby_places':
                    result = self.get_nearby_places(location)
                    if result:
                        self.logger.info(f"✓ Processed nearby_places for {location['latitude']:.4f},{location['longitude']:.4f}")
                        self.network_manager.mark_operation_complete(op['id'])
                        processed += 1
                    else:
                        raise Exception("Failed to get nearby places")
                
                else:
                    self.logger.warning(f"Unknown operation type: {op_type}")
                    self.network_manager.mark_operation_complete(op['id'])
                
            except Exception as e:
                self.logger.error(f"Failed to process operation {op['id']}: {e}")
                self.network_manager.mark_operation_failed(op['id'], str(e))
                failed += 1
        
        self.logger.info(f"Queue processing complete: {processed} succeeded, {failed} failed")
        
        # Save updated cache
        self._save_offline_cache()
    
    def log_location(self, location: Dict, context: Dict = None):
        """
        Log location data to file
        
        Args:
            location: GPS location data
            context: Optional context information from Google Maps
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        
        log_file = os.path.join(self.data_dir, f"gps_log_{date_str}.json")
        
        log_entry = {
            'location': location,
            'context': context,
            'timestamp': timestamp.isoformat()
        }
        
        # Append to daily log file
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        self.logger.info(f"Logged location: {location['latitude']}, {location['longitude']}")
    
    def start_tracking(self, interval: int = None):
        """
        Start continuous GPS tracking (works offline)
        
        Args:
            interval: Update interval in seconds (uses config if not specified)
        """
        if interval is None:
            interval = self.config.get('system_settings', {}).get('gps_update_interval', 10)
        
        self.logger.info(f"Starting GPS tracking (interval: {interval}s)")
        self.logger.info("System operates in offline mode - WiFi not required for tracking")
        
        # Check connectivity status
        is_online = self.network_manager.check_connectivity()
        self.logger.info(f"Initial status: {'Online' if is_online else 'Offline'}")
        
        last_queue_process = datetime.now()
        queue_process_interval = 300  # Process queue every 5 minutes
        
        try:
            while True:
                # Check connectivity periodically
                is_online = self.network_manager.check_connectivity()
                
                # Get current location (GPS works offline)
                location = self.get_current_location()
                
                if location:
                    # Get context (uses cache if offline, queues if needed)
                    context = self.analyze_current_context(location)
                    
                    # Log location with context (always works offline)
                    self.log_location(location, context)
                    
                    # Log status
                    mode = "Online" if is_online else "Offline"
                    self.logger.info(
                        f"[{mode}] Location: {location['latitude']:.6f}, {location['longitude']:.6f}"
                    )
                    
                    if context.get('address'):
                        self.logger.info(
                            f"  Address: {context['address'].get('formatted_address', 'Cached/Queued')}"
                        )
                    
                    if context.get('nearby_places'):
                        self.logger.info(
                            f"  Nearby: {len(context['nearby_places'])} places"
                        )
                    elif is_online:
                        self.logger.info("  No nearby places found")
                
                # Process queued operations if online and enough time has passed
                if is_online:
                    time_since_last = (datetime.now() - last_queue_process).total_seconds()
                    if time_since_last >= queue_process_interval:
                        queue_size = self.network_manager.get_queue_size()
                        if queue_size > 0:
                            self.logger.info(f"Processing {queue_size} queued operations...")
                            self.process_queued_operations()
                        last_queue_process = datetime.now()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("GPS tracking stopped by user")
            
            # Process remaining queue before exiting
            if self.network_manager.check_connectivity():
                queue_size = self.network_manager.get_queue_size()
                if queue_size > 0:
                    self.logger.info(f"Processing {queue_size} remaining queued operations before exit...")
                    self.process_queued_operations()
            
        except Exception as e:
            self.logger.error(f"Error in tracking loop: {e}")


def main():
    """Main entry point for GPS tracker"""
    tracker = GPSTracker()
    tracker.start_tracking()


if __name__ == '__main__':
    main()
