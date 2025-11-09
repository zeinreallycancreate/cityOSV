#!/usr/bin/env python3
"""
AI Processing System
Analyzes GPS data, travel patterns, and context to predict destinations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict, Counter
import math


class AIProcessor:
    """AI system for analyzing travel patterns and predicting destinations"""
    
    def __init__(self, config_path="config.json", data_dir="data"):
        self.config = self._load_config(config_path)
        self.data_dir = data_dir
        self.logger = self._setup_logger()
        self.profile = self.config.get('profile', {})
        self.known_locations = self.config.get('known_locations', [])
        self.schedule_patterns = self.config.get('schedule_patterns', {})
        
        # AI state
        self.learned_patterns = self._load_learned_patterns()
        self.location_clusters = []
        self.frequent_routes = []
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('AIProcessor')
        logger.setLevel(logging.INFO)
        
        # File handler
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/ai_processor.log')
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
    
    def _load_learned_patterns(self) -> Dict:
        """Load previously learned patterns"""
        patterns_file = os.path.join(self.data_dir, 'learned_patterns.json')
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return {
            'frequent_locations': [],
            'time_patterns': {},
            'day_patterns': {},
            'route_patterns': []
        }
    
    def _save_learned_patterns(self):
        """Save learned patterns"""
        patterns_file = os.path.join(self.data_dir, 'learned_patterns.json')
        with open(patterns_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """
        Calculate distance between two locations using Haversine formula
        
        Args:
            loc1: First location with latitude and longitude
            loc2: Second location with latitude and longitude
        
        Returns:
            Distance in kilometers
        """
        lat1 = loc1['latitude']
        lon1 = loc1['longitude']
        lat2 = loc2['latitude']
        lon2 = loc2['longitude']
        
        # Radius of Earth in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def identify_stop_points(self, locations: List[Dict], 
                            min_duration: int = 300,
                            max_distance: float = 0.1) -> List[Dict]:
        """
        Identify locations where the vehicle stopped
        
        Args:
            locations: List of GPS locations
            min_duration: Minimum stop duration in seconds
            max_distance: Maximum movement distance in km to consider as stopped
        
        Returns:
            List of stop points with duration
        """
        if not locations:
            return []
        
        stops = []
        current_stop = None
        
        for i, loc in enumerate(locations):
            if current_stop is None:
                current_stop = {
                    'location': loc,
                    'start_time': datetime.fromisoformat(loc['timestamp']),
                    'locations': [loc]
                }
            else:
                # Check if still at the same location
                distance = self.calculate_distance(current_stop['location'], loc)
                
                if distance <= max_distance:
                    current_stop['locations'].append(loc)
                else:
                    # Calculate stop duration
                    end_time = datetime.fromisoformat(current_stop['locations'][-1]['timestamp'])
                    duration = (end_time - current_stop['start_time']).total_seconds()
                    
                    if duration >= min_duration:
                        # Calculate average location
                        avg_lat = sum(l['latitude'] for l in current_stop['locations']) / len(current_stop['locations'])
                        avg_lon = sum(l['longitude'] for l in current_stop['locations']) / len(current_stop['locations'])
                        
                        stops.append({
                            'latitude': avg_lat,
                            'longitude': avg_lon,
                            'start_time': current_stop['start_time'].isoformat(),
                            'end_time': end_time.isoformat(),
                            'duration_seconds': duration
                        })
                    
                    # Start new stop
                    current_stop = {
                        'location': loc,
                        'start_time': datetime.fromisoformat(loc['timestamp']),
                        'locations': [loc]
                    }
        
        return stops
    
    def analyze_time_patterns(self, stops: List[Dict]) -> Dict:
        """
        Analyze temporal patterns in stops
        
        Args:
            stops: List of stop points
        
        Returns:
            Time-based pattern analysis
        """
        patterns = {
            'hour_distribution': defaultdict(int),
            'day_distribution': defaultdict(int),
            'weekday_patterns': defaultdict(list),
            'time_of_day_patterns': defaultdict(list)
        }
        
        for stop in stops:
            dt = datetime.fromisoformat(stop['start_time'])
            
            # Hour distribution
            patterns['hour_distribution'][dt.hour] += 1
            
            # Day of week
            day_name = dt.strftime('%A')
            patterns['day_distribution'][day_name] += 1
            
            # Weekday vs weekend
            is_weekday = dt.weekday() < 5
            patterns['weekday_patterns']['weekday' if is_weekday else 'weekend'].append(stop)
            
            # Time of day
            if 5 <= dt.hour < 12:
                time_period = 'morning'
            elif 12 <= dt.hour < 17:
                time_period = 'afternoon'
            elif 17 <= dt.hour < 21:
                time_period = 'evening'
            else:
                time_period = 'night'
            
            patterns['time_of_day_patterns'][time_period].append(stop)
        
        return patterns
    
    def match_known_location(self, location: Dict, threshold: float = 0.5) -> Optional[Dict]:
        """
        Match a location to known locations
        
        Args:
            location: Location to match
            threshold: Distance threshold in km
        
        Returns:
            Matched known location or None
        """
        for known_loc in self.known_locations:
            if known_loc.get('latitude') and known_loc.get('longitude'):
                distance = self.calculate_distance(location, known_loc)
                if distance <= threshold:
                    return known_loc
        
        return None
    
    def predict_destination(self, current_location: Dict, context: Dict = None) -> Dict:
        """
        Predict where the person is likely going based on all available information
        
        Args:
            current_location: Current GPS location
            context: Optional context from Google Maps
        
        Returns:
            Prediction with confidence score and reasoning
        """
        prediction = {
            'timestamp': datetime.now().isoformat(),
            'current_location': current_location,
            'predictions': [],
            'reasoning': []
        }
        
        now = datetime.now()
        hour = now.hour
        day_name = now.strftime('%A')
        is_weekday = now.weekday() < 5
        
        # Factor 1: Profile-based prediction
        profile_score = self._predict_from_profile(hour, day_name, is_weekday)
        if profile_score:
            prediction['predictions'].extend(profile_score)
            prediction['reasoning'].append("Based on profile information (job, schedule)")
        
        # Factor 2: Time-based patterns
        time_score = self._predict_from_time_patterns(hour, day_name)
        if time_score:
            prediction['predictions'].extend(time_score)
            prediction['reasoning'].append("Based on historical time patterns")
        
        # Factor 3: Current context from Google Maps
        if context:
            context_score = self._predict_from_context(context)
            if context_score:
                prediction['predictions'].extend(context_score)
                prediction['reasoning'].append("Based on nearby places and area type")
        
        # Factor 4: Known locations proximity
        proximity_score = self._predict_from_proximity(current_location)
        if proximity_score:
            prediction['predictions'].extend(proximity_score)
            prediction['reasoning'].append("Based on proximity to known locations")
        
        # Factor 5: Historical frequency
        frequency_score = self._predict_from_frequency()
        if frequency_score:
            prediction['predictions'].extend(frequency_score)
            prediction['reasoning'].append("Based on visit frequency")
        
        # Aggregate and rank predictions
        prediction['predictions'] = self._aggregate_predictions(prediction['predictions'])
        
        return prediction
    
    def _predict_from_profile(self, hour: int, day_name: str, is_weekday: bool) -> List[Dict]:
        """Predict based on profile information"""
        predictions = []
        
        job = self.profile.get('job')
        work_schedule = self.profile.get('work_schedule', '')
        
        # Check if work hours
        if job and is_weekday:
            # Parse work schedule (e.g., "9am-5pm")
            if '-' in work_schedule:
                try:
                    start, end = work_schedule.lower().split('-')
                    start_hour = int(start.replace('am', '').replace('pm', '').strip())
                    end_hour = int(end.replace('am', '').replace('pm', '').strip())
                    
                    # Adjust for PM
                    if 'pm' in end and end_hour != 12:
                        end_hour += 12
                    if 'pm' in start and start_hour != 12:
                        start_hour += 12
                    
                    # Morning commute
                    if start_hour - 1 <= hour <= start_hour + 1:
                        for loc in self.known_locations:
                            if loc.get('category') == 'work':
                                predictions.append({
                                    'location': loc,
                                    'confidence': 0.8,
                                    'reason': f'Morning commute to work ({job})'
                                })
                    
                    # Evening commute
                    if end_hour - 1 <= hour <= end_hour + 1:
                        for loc in self.known_locations:
                            if loc.get('name', '').lower() == 'home':
                                predictions.append({
                                    'location': loc,
                                    'confidence': 0.8,
                                    'reason': f'Evening commute from work'
                                })
                except:
                    pass
        
        # Age-based predictions
        age = self.profile.get('age')
        if age and 18 <= age <= 30:
            # Younger demographic might go out more in evenings
            if 18 <= hour <= 23 and not is_weekday:
                predictions.append({
                    'location': {'category': 'leisure', 'types': ['restaurant', 'bar', 'entertainment']},
                    'confidence': 0.5,
                    'reason': 'Age-based evening leisure activity pattern'
                })
        
        return predictions
    
    def _predict_from_time_patterns(self, hour: int, day_name: str) -> List[Dict]:
        """Predict based on learned time patterns"""
        predictions = []
        
        time_patterns = self.learned_patterns.get('time_patterns', {})
        hour_key = str(hour)
        
        if hour_key in time_patterns:
            for pattern in time_patterns[hour_key]:
                predictions.append({
                    'location': pattern['location'],
                    'confidence': pattern.get('frequency', 0) / 100.0,
                    'reason': f'Frequently visits this location at {hour}:00'
                })
        
        return predictions
    
    def _predict_from_context(self, context: Dict) -> List[Dict]:
        """Predict based on current context from Google Maps"""
        predictions = []
        
        area_type = context.get('area_type')
        nearby_places = context.get('nearby_places', [])
        
        if area_type:
            # Analyze what the area suggests
            if area_type in ['shopping_mall', 'store', 'supermarket']:
                predictions.append({
                    'location': {'category': 'shopping', 'area_type': area_type},
                    'confidence': 0.6,
                    'reason': f'Currently in shopping area ({area_type})'
                })
            elif area_type in ['gym', 'stadium', 'park']:
                predictions.append({
                    'location': {'category': 'fitness', 'area_type': area_type},
                    'confidence': 0.7,
                    'reason': f'Currently in fitness/recreation area'
                })
        
        # Check for specific high-value places nearby
        for place in nearby_places[:5]:  # Top 5 nearest
            place_types = place.get('types', [])
            
            # Match to known locations
            for known_loc in self.known_locations:
                if any(t in place.get('name', '').lower() for t in [known_loc.get('name', '').lower()]):
                    predictions.append({
                        'location': known_loc,
                        'confidence': 0.85,
                        'reason': f'Near known location: {known_loc.get("name")}'
                    })
        
        return predictions
    
    def _predict_from_proximity(self, current_location: Dict) -> List[Dict]:
        """Predict based on proximity to known locations"""
        predictions = []
        
        for known_loc in self.known_locations:
            if known_loc.get('latitude') and known_loc.get('longitude'):
                distance = self.calculate_distance(current_location, known_loc)
                
                # If within 2km, likely heading there
                if distance <= 2.0:
                    confidence = max(0.3, 1.0 - (distance / 2.0))
                    predictions.append({
                        'location': known_loc,
                        'confidence': confidence,
                        'reason': f'Within {distance:.2f}km of {known_loc.get("name")}'
                    })
        
        return predictions
    
    def _predict_from_frequency(self) -> List[Dict]:
        """Predict based on visit frequency and recognized locations"""
        predictions = []
        
        # Check recognized locations first (higher priority)
        recognized_locs = self.learned_patterns.get('recognized_locations', [])
        for loc in recognized_locs[:5]:  # Top 5 recognized
            base_confidence = loc.get('confidence', 0.5)
            visit_count = loc.get('visit_count', 0)
            
            # Boost confidence for recognized locations
            confidence = min(0.9, base_confidence + (visit_count / 100.0) * 0.1)
            
            predictions.append({
                'location': {
                    **loc['location'],
                    'name': loc['type'],
                    'recognized': True
                },
                'confidence': confidence,
                'reason': f'Recognized as {loc["type"]} (visited {visit_count} times)'
            })
        
        # Add other frequent locations
        frequent_locs = self.learned_patterns.get('frequent_locations', [])
        
        for loc in frequent_locs[:5]:  # Top 5 most frequent
            # Skip if already in recognized locations
            loc_lat = loc['location']['latitude']
            loc_lon = loc['location']['longitude']
            
            is_recognized = any(
                abs(r['location']['latitude'] - loc_lat) < 0.001 and 
                abs(r['location']['longitude'] - loc_lon) < 0.001
                for r in recognized_locs
            )
            
            if not is_recognized:
                predictions.append({
                    'location': loc['location'],
                    'confidence': loc.get('frequency', 0) / 200.0,  # Scale down
                    'reason': f'Frequently visited location (visited {loc.get("visit_count", 0)} times)'
                })
        
        return predictions
    
    def _aggregate_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Aggregate and rank predictions"""
        if not predictions:
            return []
        
        # Group by location
        location_scores = defaultdict(lambda: {'total_confidence': 0, 'reasons': [], 'location': None})
        
        for pred in predictions:
            loc = pred.get('location', {})
            loc_key = loc.get('name', str(loc))
            
            location_scores[loc_key]['total_confidence'] += pred['confidence']
            location_scores[loc_key]['reasons'].append(pred['reason'])
            location_scores[loc_key]['location'] = loc
        
        # Sort by confidence
        ranked = []
        for loc_key, data in location_scores.items():
            ranked.append({
                'location': data['location'],
                'confidence': min(1.0, data['total_confidence']),
                'reasons': data['reasons']
            })
        
        ranked.sort(key=lambda x: x['confidence'], reverse=True)
        
        return ranked[:5]  # Top 5 predictions
    
    def learn_from_data(self, days: int = 30):
        """
        Analyze historical data and learn patterns
        
        Args:
            days: Number of days of history to analyze
        """
        self.logger.info(f"Learning from past {days} days of data...")
        
        # Load historical data
        all_locations = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = cutoff_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            log_file = os.path.join(self.data_dir, f"gps_log_{date_str}.json")
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    day_logs = json.load(f)
                    for log in day_logs:
                        all_locations.append(log['location'])
        
        if not all_locations:
            self.logger.warning("No historical data found to learn from")
            return
        
        self.logger.info(f"Analyzing {len(all_locations)} location records...")
        
        # Identify stop points
        stops = self.identify_stop_points(all_locations)
        self.logger.info(f"Identified {len(stops)} stop points")
        
        # Analyze time patterns
        time_patterns = self.analyze_time_patterns(stops)
        
        # Find frequent locations
        location_frequency = defaultdict(lambda: {
            'count': 0, 
            'durations': [], 
            'times': [],
            'hours': [],
            'days': []
        })
        
        for stop in stops:
            # Round coordinates to cluster nearby stops
            lat_rounded = round(stop['latitude'], 3)
            lon_rounded = round(stop['longitude'], 3)
            loc_key = f"{lat_rounded},{lon_rounded}"
            
            dt = datetime.fromisoformat(stop['start_time'])
            
            location_frequency[loc_key]['count'] += 1
            location_frequency[loc_key]['durations'].append(stop['duration_seconds'])
            location_frequency[loc_key]['times'].append(stop['start_time'])
            location_frequency[loc_key]['hours'].append(dt.hour)
            location_frequency[loc_key]['days'].append(dt.strftime('%A'))
            location_frequency[loc_key]['location'] = {
                'latitude': lat_rounded,
                'longitude': lon_rounded
            }
        
        # Recognize points of interest
        self.logger.info("Recognizing points of interest...")
        recognized_locations = self._recognize_points_of_interest(
            location_frequency, 
            stops,
            days
        )
        
        # Sort by frequency
        frequent_locations = sorted(
            [{'location': v['location'], 'visit_count': v['count'], 'frequency': v['count']} 
             for v in location_frequency.values()],
            key=lambda x: x['visit_count'],
            reverse=True
        )
        
        # Update learned patterns
        self.learned_patterns['frequent_locations'] = frequent_locations[:20]
        self.learned_patterns['recognized_locations'] = recognized_locations
        self.learned_patterns['time_patterns'] = {}
        
        for hour, count in time_patterns['hour_distribution'].items():
            self.learned_patterns['time_patterns'][str(hour)] = [{
                'frequency': count,
                'location': {'hour': hour}
            }]
        
        # Save learned patterns
        self._save_learned_patterns()
        
        self.logger.info(f"Learning complete. Found {len(frequent_locations)} frequent locations")
        self.logger.info(f"Recognized {len(recognized_locations)} points of interest")
    
    def _recognize_points_of_interest(self, location_frequency: Dict, 
                                     stops: List[Dict], days: int) -> List[Dict]:
        """
        Recognize and label points of interest like Home, Work, etc.
        
        Args:
            location_frequency: Dictionary of location visit statistics
            stops: List of all stop points
            days: Number of days analyzed
        
        Returns:
            List of recognized locations with labels
        """
        recognized = []
        
        # Sort locations by visit count
        sorted_locations = sorted(
            location_frequency.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        for loc_key, data in sorted_locations[:10]:  # Top 10 locations
            location = data['location']
            visit_count = data['count']
            avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0
            hours = data['hours']
            days_visited = data['days']
            
            # Calculate statistics
            night_visits = sum(1 for h in hours if 22 <= h or h <= 6)
            morning_visits = sum(1 for h in hours if 6 < h <= 9)
            work_hours_visits = sum(1 for h in hours if 9 < h <= 17)
            evening_visits = sum(1 for h in hours if 17 < h <= 22)
            
            weekday_visits = sum(1 for d in days_visited if d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
            weekend_visits = sum(1 for d in days_visited if d in ['Saturday', 'Sunday'])
            
            # Recognition logic
            recognized_type = None
            confidence = 0.0
            reasoning = []
            
            # Home detection
            # Criteria: Most frequent location, long durations, many night/evening visits
            if visit_count >= days * 0.5:  # Visited at least 50% of days
                if night_visits > visit_count * 0.3:  # At least 30% night visits
                    if avg_duration > 3600 * 6:  # Average stay > 6 hours
                        recognized_type = 'Home'
                        confidence = min(0.95, 0.7 + (night_visits / visit_count) * 0.25)
                        reasoning.append(f"Visited {visit_count}/{days} days")
                        reasoning.append(f"{night_visits} night-time visits")
                        reasoning.append(f"Average stay: {avg_duration/3600:.1f} hours")
            
            # Work detection
            # Criteria: Regular weekday visits during work hours, medium-long duration
            if not recognized_type and weekday_visits >= days * 0.3:  # At least 30% of weekdays
                if work_hours_visits > visit_count * 0.6:  # At least 60% during work hours
                    if 3600 * 3 < avg_duration < 3600 * 12:  # 3-12 hours average
                        recognized_type = 'Work'
                        confidence = min(0.9, 0.6 + (work_hours_visits / visit_count) * 0.3)
                        reasoning.append(f"Frequent weekday visits: {weekday_visits}")
                        reasoning.append(f"{work_hours_visits} visits during work hours")
                        reasoning.append(f"Average stay: {avg_duration/3600:.1f} hours")
            
            # Gym/Fitness detection
            # Criteria: Regular visits, morning or evening, short-medium duration
            if not recognized_type and visit_count >= days * 0.2:  # At least 20% of days
                if (morning_visits + evening_visits) > visit_count * 0.7:
                    if 1800 < avg_duration < 7200:  # 30 min - 2 hours
                        recognized_type = 'Gym/Fitness'
                        confidence = 0.7
                        reasoning.append(f"Regular visits: {visit_count} times")
                        reasoning.append(f"Morning/evening pattern")
                        reasoning.append(f"Typical duration: {avg_duration/60:.0f} minutes")
            
            # Shopping/Errands detection
            # Criteria: Multiple visits, short duration, varied times
            if not recognized_type and visit_count >= days * 0.15:  # At least 15% of days
                if avg_duration < 3600 * 2:  # Less than 2 hours
                    if len(set(hours)) > 5:  # Visited at various times
                        recognized_type = 'Shopping/Errands'
                        confidence = 0.65
                        reasoning.append(f"{visit_count} visits")
                        reasoning.append(f"Short stays: {avg_duration/60:.0f} minutes")
                        reasoning.append(f"Various times of day")
            
            # Friend/Family location detection
            # Criteria: Regular weekend or evening visits, long duration
            if not recognized_type and visit_count >= days * 0.1:  # At least 10% of days
                if weekend_visits > weekday_visits or evening_visits > visit_count * 0.5:
                    if avg_duration > 3600 * 2:  # More than 2 hours
                        recognized_type = 'Friend/Family'
                        confidence = 0.6
                        reasoning.append(f"{visit_count} visits")
                        reasoning.append(f"Weekend/evening pattern")
                        reasoning.append(f"Social duration: {avg_duration/3600:.1f} hours")
            
            # Restaurant/Dining detection
            # Criteria: Multiple short visits during meal times
            if not recognized_type and visit_count >= 5:
                meal_times = sum(1 for h in hours if h in [7,8,12,13,18,19,20])
                if meal_times > visit_count * 0.6:
                    if 1800 < avg_duration < 5400:  # 30 min - 1.5 hours
                        recognized_type = 'Restaurant/Dining'
                        confidence = 0.65
                        reasoning.append(f"{visit_count} visits")
                        reasoning.append(f"Meal time pattern")
                        reasoning.append(f"Dining duration: {avg_duration/60:.0f} minutes")
            
            # Generic frequent location if no specific type identified
            if not recognized_type and visit_count >= days * 0.1:
                recognized_type = 'Frequent Location'
                confidence = 0.5
                reasoning.append(f"Visited {visit_count} times")
            
            # Add to recognized locations
            if recognized_type:
                recognized.append({
                    'type': recognized_type,
                    'location': location,
                    'confidence': confidence,
                    'visit_count': visit_count,
                    'average_duration_hours': avg_duration / 3600,
                    'reasoning': reasoning,
                    'statistics': {
                        'night_visits': night_visits,
                        'morning_visits': morning_visits,
                        'work_hours_visits': work_hours_visits,
                        'evening_visits': evening_visits,
                        'weekday_visits': weekday_visits,
                        'weekend_visits': weekend_visits
                    }
                })
                
                self.logger.info(
                    f"Recognized {recognized_type} at ({location['latitude']:.4f}, {location['longitude']:.4f}) "
                    f"- Confidence: {confidence:.1%}"
                )
        
        return recognized


def main():
    """Main entry point for AI processor"""
    processor = AIProcessor()
    processor.learn_from_data(days=30)


if __name__ == '__main__':
    main()
