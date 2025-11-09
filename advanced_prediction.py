#!/usr/bin/env python3
"""
Advanced Outcome Prediction Engine
INSANE level prediction algorithm that factors in EVERYTHING
Predicts outcomes, purposes, behavioral patterns, and destinations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict, Counter
import math
import statistics


class AdvancedOutcomePredictionEngine:
    """
    Advanced prediction engine that factors in EVERYTHING to predict outcomes
    """
    
    def __init__(self, config_path="config.json", data_dir="data"):
        self.config = self._load_config(config_path)
        self.data_dir = data_dir
        self.logger = self._setup_logger()
        
        # Load all available data
        self.profile = self.config.get('profile', {})
        self.known_locations = self.config.get('known_locations', [])
        self.schedule_patterns = self.config.get('schedule_patterns', {})
        
        # Load learned patterns
        self.learned_patterns = self._load_learned_patterns()
        
        # Advanced analysis caches
        self.behavioral_patterns = {}
        self.temporal_patterns = {}
        self.psychological_profile = {}
        self.routine_deviations = []
        
        # Initialize advanced models
        self._initialize_advanced_models()
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('AdvancedPredictionEngine')
        logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/advanced_prediction.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
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
        """Load learned patterns"""
        patterns_file = os.path.join(self.data_dir, 'learned_patterns.json')
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _initialize_advanced_models(self):
        """Initialize advanced prediction models"""
        self.logger.info("Initializing ADVANCED outcome prediction models...")
        
        # Build psychological profile from demographics
        self._build_psychological_profile()
        
        # Analyze behavioral patterns
        self._analyze_behavioral_patterns()
        
        # Detect routine patterns
        self._detect_routine_patterns()
        
        self.logger.info("Advanced models initialized")
    
    def _build_psychological_profile(self):
        """
        Build psychological profile from demographics and patterns
        This factors in age, gender, job, and inferred personality traits
        """
        age = self.profile.get('age')
        gender = self.profile.get('gender')
        job = self.profile.get('job', '').lower()
        
        profile = {
            'risk_tolerance': 0.5,
            'spontaneity': 0.5,
            'social_tendency': 0.5,
            'routine_adherence': 0.5,
            'health_consciousness': 0.5,
            'work_dedication': 0.5,
            'leisure_preference': 0.5
        }
        
        # Age-based adjustments
        if age:
            if age < 25:
                profile['spontaneity'] = 0.7
                profile['social_tendency'] = 0.8
                profile['risk_tolerance'] = 0.6
            elif 25 <= age < 35:
                profile['work_dedication'] = 0.8
                profile['routine_adherence'] = 0.7
            elif 35 <= age < 50:
                profile['routine_adherence'] = 0.8
                profile['health_consciousness'] = 0.6
                profile['work_dedication'] = 0.7
            elif age >= 50:
                profile['routine_adherence'] = 0.9
                profile['health_consciousness'] = 0.8
                profile['spontaneity'] = 0.3
        
        # Gender-based statistical adjustments (based on general patterns)
        if gender:
            if gender.lower() in ['female', 'f']:
                profile['social_tendency'] += 0.1
                profile['health_consciousness'] += 0.1
            elif gender.lower() in ['male', 'm']:
                profile['risk_tolerance'] += 0.1
        
        # Job-based adjustments
        if 'engineer' in job or 'developer' in job or 'programmer' in job:
            profile['routine_adherence'] = 0.8
            profile['social_tendency'] = 0.4
        elif 'teacher' in job or 'professor' in job:
            profile['routine_adherence'] = 0.9
            profile['social_tendency'] = 0.6
        elif 'sales' in job or 'marketing' in job:
            profile['social_tendency'] = 0.9
            profile['spontaneity'] = 0.7
        elif 'doctor' in job or 'nurse' in job or 'health' in job:
            profile['work_dedication'] = 0.9
            profile['health_consciousness'] = 0.9
        elif 'artist' in job or 'designer' in job or 'creative' in job:
            profile['spontaneity'] = 0.8
            profile['routine_adherence'] = 0.4
        
        # Normalize values
        for key in profile:
            profile[key] = max(0.0, min(1.0, profile[key]))
        
        self.psychological_profile = profile
        self.logger.info(f"Psychological profile: {profile}")
    
    def _analyze_behavioral_patterns(self):
        """
        Deep analysis of behavioral patterns from historical data
        """
        # Load all historical location data
        all_data = self._load_all_historical_data()
        
        if not all_data:
            self.logger.warning("No historical data for behavioral analysis")
            return
        
        patterns = {
            'travel_frequency': {},
            'time_preferences': {},
            'location_diversity': 0,
            'average_trip_duration': 0,
            'movement_patterns': {},
            'consistency_score': 0,
            'exploration_tendency': 0
        }
        
        # Analyze travel frequency by day of week
        day_counts = defaultdict(int)
        for data in all_data:
            dt = datetime.fromisoformat(data['location']['timestamp'])
            day_counts[dt.strftime('%A')] += 1
        
        patterns['travel_frequency'] = dict(day_counts)
        
        # Calculate location diversity (how many unique places)
        unique_locations = set()
        for data in all_data:
            loc = data['location']
            unique_locations.add(f"{loc['latitude']:.3f},{loc['longitude']:.3f}")
        
        patterns['location_diversity'] = len(unique_locations)
        
        # Calculate exploration tendency (new places vs known places)
        if len(all_data) > 0:
            patterns['exploration_tendency'] = min(1.0, len(unique_locations) / (len(all_data) / 100))
        
        # Analyze consistency (how predictable the person is)
        patterns['consistency_score'] = self._calculate_consistency_score(all_data)
        
        self.behavioral_patterns = patterns
        self.logger.info(f"Behavioral patterns analyzed: {patterns['location_diversity']} unique locations")
    
    def _detect_routine_patterns(self):
        """
        Detect routine patterns and identify deviations
        """
        all_data = self._load_all_historical_data()
        
        if len(all_data) < 100:  # Need sufficient data
            return
        
        # Group by day of week and hour
        hourly_patterns = defaultdict(lambda: defaultdict(list))
        
        for data in all_data:
            dt = datetime.fromisoformat(data['location']['timestamp'])
            day = dt.strftime('%A')
            hour = dt.hour
            loc = data['location']
            
            hourly_patterns[day][hour].append({
                'lat': loc['latitude'],
                'lon': loc['longitude'],
                'timestamp': dt
            })
        
        # Detect routine (most common location for each day/hour)
        routines = {}
        for day, hours in hourly_patterns.items():
            routines[day] = {}
            for hour, locations in hours.items():
                if len(locations) >= 2:  # At least 2 occurrences
                    # Find most common location
                    loc_counter = Counter()
                    for loc in locations:
                        key = f"{loc['lat']:.3f},{loc['lon']:.3f}"
                        loc_counter[key] += 1
                    
                    most_common = loc_counter.most_common(1)[0]
                    if most_common[1] >= 2:  # Occurred at least twice
                        routines[day][hour] = {
                            'location': most_common[0],
                            'frequency': most_common[1] / len(locations)
                        }
        
        self.temporal_patterns = routines
    
    def _load_all_historical_data(self) -> List[Dict]:
        """Load all historical GPS data"""
        all_data = []
        
        if not os.path.exists(self.data_dir):
            return all_data
        
        import glob
        log_files = glob.glob(os.path.join(self.data_dir, 'gps_log_*.json'))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    all_data.extend(logs)
            except Exception as e:
                self.logger.error(f"Error loading {log_file}: {e}")
        
        return all_data
    
    def _calculate_consistency_score(self, all_data: List[Dict]) -> float:
        """
        Calculate how consistent/predictable the person is
        1.0 = extremely consistent, 0.0 = completely random
        """
        if len(all_data) < 10:
            return 0.5
        
        # Group by day and hour
        patterns = defaultdict(list)
        
        for data in all_data:
            dt = datetime.fromisoformat(data['location']['timestamp'])
            key = f"{dt.strftime('%A')}_{dt.hour}"
            loc = data['location']
            patterns[key].append(f"{loc['latitude']:.3f},{loc['longitude']:.3f}")
        
        # Calculate consistency for each time slot
        consistencies = []
        for key, locations in patterns.items():
            if len(locations) >= 2:
                counter = Counter(locations)
                most_common_freq = counter.most_common(1)[0][1]
                consistency = most_common_freq / len(locations)
                consistencies.append(consistency)
        
        if consistencies:
            return statistics.mean(consistencies)
        
        return 0.5
    
    def predict_insane_outcome(self, current_location: Dict, context: Dict = None) -> Dict:
        """
        INSANE LEVEL outcome prediction that factors in EVERYTHING
        
        This predicts not just destination but:
        - Why they're going there
        - What they'll do
        - How long they'll stay
        - What might happen
        - Emotional state
        - Decision factors
        - Alternative scenarios
        
        Args:
            current_location: Current GPS location
            context: Context from Google Maps (nearby places, etc.)
        
        Returns:
            Comprehensive outcome prediction
        """
        self.logger.info("🔮 Running INSANE outcome prediction algorithm...")
        
        now = datetime.now()
        
        # Initialize prediction structure
        prediction = {
            'timestamp': now.isoformat(),
            'current_location': current_location,
            'current_context': context,
            'confidence': 0.0,
            
            # Multi-layered predictions
            'destination_predictions': [],
            'purpose_predictions': [],
            'behavioral_predictions': [],
            'outcome_scenarios': [],
            'emotional_state': {},
            'decision_factors': [],
            'timeline_predictions': {},
            'risk_assessment': {},
            
            # Meta-analysis
            'prediction_reasoning': [],
            'confidence_factors': {},
            'alternative_scenarios': []
        }
        
        # === LAYER 1: Temporal Analysis ===
        temporal_factors = self._analyze_temporal_factors(now)
        prediction['confidence_factors']['temporal'] = temporal_factors['confidence']
        prediction['prediction_reasoning'].extend(temporal_factors['reasoning'])
        
        # === LAYER 2: Psychological State ===
        psychological_state = self._predict_psychological_state(now, current_location)
        prediction['emotional_state'] = psychological_state
        prediction['confidence_factors']['psychological'] = psychological_state.get('confidence', 0.5)
        
        # === LAYER 3: Contextual Analysis ===
        if context:
            contextual_analysis = self._analyze_context_deeply(context, now)
            prediction['confidence_factors']['contextual'] = contextual_analysis['confidence']
            prediction['prediction_reasoning'].extend(contextual_analysis['reasoning'])
        
        # === LAYER 4: Behavioral Pattern Matching ===
        behavioral_match = self._match_behavioral_patterns(current_location, now)
        prediction['behavioral_predictions'] = behavioral_match['predictions']
        prediction['confidence_factors']['behavioral'] = behavioral_match['confidence']
        
        # === LAYER 5: Historical Pattern Analysis ===
        historical_analysis = self._analyze_historical_patterns(current_location, now)
        prediction['destination_predictions'].extend(historical_analysis['destinations'])
        prediction['confidence_factors']['historical'] = historical_analysis['confidence']
        
        # === LAYER 6: Purpose Inference ===
        purpose_analysis = self._infer_purpose(
            current_location, now, context,
            temporal_factors, psychological_state, behavioral_match
        )
        prediction['purpose_predictions'] = purpose_analysis
        
        # === LAYER 7: Timeline Prediction ===
        timeline = self._predict_timeline(
            current_location, now,
            prediction['destination_predictions'],
            purpose_analysis
        )
        prediction['timeline_predictions'] = timeline
        
        # === LAYER 8: Outcome Scenarios ===
        scenarios = self._generate_outcome_scenarios(
            prediction['destination_predictions'],
            purpose_analysis,
            psychological_state,
            timeline
        )
        prediction['outcome_scenarios'] = scenarios
        
        # === LAYER 9: Risk Assessment ===
        risk = self._assess_risks(
            current_location, now,
            prediction['destination_predictions'],
            psychological_state,
            temporal_factors
        )
        prediction['risk_assessment'] = risk
        
        # === LAYER 10: Decision Factor Analysis ===
        decision_factors = self._analyze_decision_factors(
            now, current_location, context,
            temporal_factors, psychological_state
        )
        prediction['decision_factors'] = decision_factors
        
        # === LAYER 11: Alternative Scenarios ===
        alternatives = self._generate_alternative_scenarios(
            prediction['destination_predictions'],
            decision_factors,
            psychological_state
        )
        prediction['alternative_scenarios'] = alternatives
        
        # === Calculate Overall Confidence ===
        confidence_scores = list(prediction['confidence_factors'].values())
        if confidence_scores:
            prediction['confidence'] = statistics.mean(confidence_scores)
        
        # === Meta-reasoning ===
        prediction['meta_analysis'] = self._generate_meta_analysis(prediction)
        
        self.logger.info(f"Prediction complete with confidence: {prediction['confidence']:.1%}")
        
        return prediction
    
    def _analyze_temporal_factors(self, now: datetime) -> Dict:
        """Analyze temporal factors (time, day, season, etc.)"""
        hour = now.hour
        day = now.strftime('%A')
        month = now.month
        is_weekend = now.weekday() >= 5
        
        factors = {
            'hour': hour,
            'day': day,
            'is_weekend': is_weekend,
            'time_period': self._get_time_period(hour),
            'season': self._get_season(month),
            'confidence': 0.9,  # Temporal data is highly reliable
            'reasoning': []
        }
        
        # Add reasoning based on time
        if 6 <= hour <= 9 and not is_weekend:
            factors['reasoning'].append("Morning weekday - likely commute to work")
            factors['typical_activity'] = 'work_commute'
        elif 9 <= hour <= 17 and not is_weekend:
            factors['reasoning'].append("Work hours on weekday")
            factors['typical_activity'] = 'at_work'
        elif 17 <= hour <= 19 and not is_weekend:
            factors['reasoning'].append("Evening weekday - likely commute home or errands")
            factors['typical_activity'] = 'evening_commute'
        elif 19 <= hour <= 22:
            factors['reasoning'].append("Evening hours - leisure or social activities")
            factors['typical_activity'] = 'evening_leisure'
        elif 22 <= hour or hour <= 6:
            factors['reasoning'].append("Late night/early morning - unusual activity")
            factors['typical_activity'] = 'unusual_hours'
        elif is_weekend:
            factors['reasoning'].append("Weekend - leisure, errands, or social activities")
            factors['typical_activity'] = 'weekend_activities'
        
        return factors
    
    def _get_time_period(self, hour: int) -> str:
        """Get time period name"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _get_season(self, month: int) -> str:
        """Get season"""
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'fall'
        else:
            return 'winter'
    
    def _predict_psychological_state(self, now: datetime, location: Dict) -> Dict:
        """Predict psychological/emotional state"""
        state = {
            'stress_level': 0.5,
            'energy_level': 0.5,
            'social_desire': 0.5,
            'decision_clarity': 0.5,
            'mood': 'neutral',
            'confidence': 0.6
        }
        
        hour = now.hour
        day = now.strftime('%A')
        
        # Time-based adjustments
        if 6 <= hour <= 9:
            state['energy_level'] = 0.6
            state['stress_level'] = 0.6  # Morning rush
        elif 9 <= hour <= 12:
            state['energy_level'] = 0.8  # Peak energy
            state['decision_clarity'] = 0.8
        elif 12 <= hour <= 14:
            state['energy_level'] = 0.5  # Post-lunch dip
        elif 14 <= hour <= 17:
            state['energy_level'] = 0.7
            state['stress_level'] = 0.7  # Afternoon push
        elif 17 <= hour <= 20:
            state['energy_level'] = 0.6
            state['social_desire'] = 0.7  # Social hours
        elif 20 <= hour <= 23:
            state['energy_level'] = 0.4
            state['social_desire'] = 0.5
        else:
            state['energy_level'] = 0.2
            state['stress_level'] = 0.7  # Unusual hours = stress
        
        # Day-based adjustments
        if day == 'Monday':
            state['stress_level'] += 0.2
            state['mood'] = 'motivated_stressed'
        elif day == 'Friday':
            state['mood'] = 'relieved_excited'
            state['social_desire'] += 0.2
        elif day in ['Saturday', 'Sunday']:
            state['stress_level'] -= 0.3
            state['mood'] = 'relaxed'
            state['social_desire'] += 0.1
        
        # Apply psychological profile
        state['stress_level'] *= (1.0 - self.psychological_profile.get('routine_adherence', 0.5))
        state['social_desire'] *= self.psychological_profile.get('social_tendency', 0.5)
        
        # Normalize
        for key in ['stress_level', 'energy_level', 'social_desire', 'decision_clarity']:
            state[key] = max(0.0, min(1.0, state[key]))
        
        return state
    
    def _analyze_context_deeply(self, context: Dict, now: datetime) -> Dict:
        """Deep analysis of current context"""
        analysis = {
            'confidence': 0.5,
            'reasoning': [],
            'implications': []
        }
        
        area_type = context.get('area_type')
        nearby_places = context.get('nearby_places', [])
        address = context.get('address', {})
        
        if area_type:
            analysis['reasoning'].append(f"Currently in {area_type} area")
            analysis['confidence'] += 0.1
            
            # Infer purpose from area type
            if 'shopping' in area_type:
                analysis['implications'].append("Shopping or errands activity likely")
            elif 'residential' in area_type:
                analysis['implications'].append("Home or visiting someone")
            elif 'commercial' in area_type or 'office' in area_type:
                analysis['implications'].append("Work or business-related")
        
        if nearby_places:
            analysis['reasoning'].append(f"{len(nearby_places)} places nearby")
            analysis['confidence'] += 0.15
            
            # Analyze place types
            place_types = []
            for place in nearby_places:
                place_types.extend(place.get('types', []))
            
            type_counter = Counter(place_types)
            top_types = type_counter.most_common(3)
            
            for place_type, count in top_types:
                analysis['implications'].append(f"Near {count} {place_type} locations")
        
        return analysis
    
    def _match_behavioral_patterns(self, location: Dict, now: datetime) -> Dict:
        """Match current situation to behavioral patterns"""
        match = {
            'predictions': [],
            'confidence': 0.5
        }
        
        # Check routine adherence
        day = now.strftime('%A')
        hour = now.hour
        
        if day in self.temporal_patterns and hour in self.temporal_patterns[day]:
            routine = self.temporal_patterns[day][hour]
            match['predictions'].append({
                'type': 'routine_following',
                'confidence': routine['frequency'],
                'description': f"Following typical {day} {hour}:00 routine"
            })
            match['confidence'] = routine['frequency']
        
        # Check exploration vs routine tendency
        exploration = self.behavioral_patterns.get('exploration_tendency', 0.5)
        
        if exploration > 0.7:
            match['predictions'].append({
                'type': 'exploration',
                'confidence': 0.6,
                'description': "High exploration tendency - may visit new places"
            })
        elif exploration < 0.3:
            match['predictions'].append({
                'type': 'routine_adherence',
                'confidence': 0.7,
                'description': "Strong routine adherence - likely going to known location"
            })
        
        return match
    
    def _analyze_historical_patterns(self, location: Dict, now: datetime) -> Dict:
        """Analyze historical patterns for this time"""
        analysis = {
            'destinations': [],
            'confidence': 0.5
        }
        
        # Get recognized locations
        recognized = self.learned_patterns.get('recognized_locations', [])
        
        for loc in recognized:
            # Check if this matches the typical time for this location
            stats = loc.get('statistics', {})
            hour = now.hour
            
            # Calculate time match score
            time_match = 0.0
            
            if 6 <= hour <= 9 and stats.get('morning_visits', 0) > 0:
                time_match = 0.7
            elif 9 <= hour <= 17 and stats.get('work_hours_visits', 0) > 0:
                time_match = 0.8
            elif 17 <= hour <= 22 and stats.get('evening_visits', 0) > 0:
                time_match = 0.7
            
            if time_match > 0:
                analysis['destinations'].append({
                    'location': loc['location'],
                    'type': loc['type'],
                    'confidence': time_match * loc['confidence'],
                    'reason': f"Historical {loc['type']} visit pattern"
                })
        
        if analysis['destinations']:
            analysis['confidence'] = max(d['confidence'] for d in analysis['destinations'])
        
        return analysis
    
    def _infer_purpose(self, location: Dict, now: datetime, context: Dict,
                      temporal: Dict, psychological: Dict, behavioral: Dict) -> List[Dict]:
        """Infer the PURPOSE of the trip/activity"""
        purposes = []
        
        hour = now.hour
        is_weekend = now.weekday() >= 5
        
        # Work-related purposes
        if 7 <= hour <= 9 and not is_weekend:
            purposes.append({
                'purpose': 'Commuting to work',
                'confidence': 0.8,
                'expected_duration': '8-9 hours',
                'expected_outcome': 'Arrive at workplace, complete work tasks'
            })
        elif 17 <= hour <= 19 and not is_weekend:
            purposes.append({
                'purpose': 'Commuting from work',
                'confidence': 0.8,
                'expected_duration': '30-60 minutes',
                'expected_outcome': 'Arrive home, transition to evening activities'
            })
        
        # Social purposes
        if psychological.get('social_desire', 0) > 0.6:
            if 18 <= hour <= 23:
                purposes.append({
                    'purpose': 'Social activity or entertainment',
                    'confidence': 0.7,
                    'expected_duration': '2-4 hours',
                    'expected_outcome': 'Social interaction, leisure, relaxation'
                })
        
        # Health/fitness purposes
        if self.psychological_profile.get('health_consciousness', 0) > 0.6:
            if hour in [6, 7, 8, 17, 18, 19]:
                purposes.append({
                    'purpose': 'Exercise or fitness activity',
                    'confidence': 0.6,
                    'expected_duration': '1-2 hours',
                    'expected_outcome': 'Physical activity, health improvement'
                })
        
        # Errands/shopping purposes
        if 10 <= hour <= 20:
            purposes.append({
                'purpose': 'Shopping or running errands',
                'confidence': 0.5,
                'expected_duration': '1-3 hours',
                'expected_outcome': 'Acquire goods/services, complete tasks'
            })
        
        # Exploration/spontaneous
        if self.behavioral_patterns.get('exploration_tendency', 0) > 0.7:
            purposes.append({
                'purpose': 'Spontaneous exploration or new experience',
                'confidence': 0.4,
                'expected_duration': 'Variable',
                'expected_outcome': 'Discovery, new experiences'
            })
        
        return purposes
    
    def _predict_timeline(self, location: Dict, now: datetime,
                         destinations: List[Dict], purposes: List[Dict]) -> Dict:
        """Predict timeline of events"""
        timeline = {
            'estimated_arrival_time': None,
            'estimated_duration': None,
            'estimated_return_time': None,
            'milestones': []
        }
        
        if not destinations:
            return timeline
        
        # Estimate travel time (simplified - would use distance in real scenario)
        estimated_travel_minutes = 20  # Default estimate
        
        arrival = now + timedelta(minutes=estimated_travel_minutes)
        timeline['estimated_arrival_time'] = arrival.isoformat()
        
        # Estimate duration based on destination type and purpose
        if destinations:
            dest_type = destinations[0].get('type', '')
            
            if dest_type == 'Work':
                duration_hours = 8
            elif dest_type == 'Home':
                duration_hours = 12
            elif dest_type == 'Gym/Fitness':
                duration_hours = 1.5
            elif dest_type == 'Shopping/Errands':
                duration_hours = 1
            else:
                duration_hours = 2
            
            timeline['estimated_duration'] = f"{duration_hours} hours"
            
            return_time = arrival + timedelta(hours=duration_hours)
            timeline['estimated_return_time'] = return_time.isoformat()
            
            # Add milestones
            timeline['milestones'] = [
                {'time': arrival.isoformat(), 'event': 'Arrival at destination'},
                {'time': (arrival + timedelta(hours=duration_hours/2)).isoformat(), 
                 'event': 'Mid-activity'},
                {'time': return_time.isoformat(), 'event': 'Departure/Return'}
            ]
        
        return timeline
    
    def _generate_outcome_scenarios(self, destinations: List[Dict],
                                    purposes: List[Dict],
                                    psychological: Dict,
                                    timeline: Dict) -> List[Dict]:
        """Generate possible outcome scenarios"""
        scenarios = []
        
        # Scenario 1: Expected outcome (highest probability)
        if destinations and purposes:
            expected = {
                'scenario': 'Expected Outcome',
                'probability': 0.7,
                'description': f"Travels to {destinations[0].get('type', 'destination')}, "
                              f"completes {purposes[0].get('purpose', 'activity')}, returns as planned",
                'outcome': 'Successful completion of planned activity',
                'satisfaction_level': 0.7 + psychological.get('decision_clarity', 0.5) * 0.3
            }
            scenarios.append(expected)
        
        # Scenario 2: Extended duration
        extended = {
            'scenario': 'Extended Duration',
            'probability': 0.2,
            'description': 'Activity takes longer than expected due to unforeseen circumstances',
            'outcome': 'Completion with delay',
            'satisfaction_level': 0.6
        }
        scenarios.append(extended)
        
        # Scenario 3: Change of plans
        if self.psychological_profile.get('spontaneity', 0) > 0.5:
            change = {
                'scenario': 'Spontaneous Change',
                'probability': 0.15 * self.psychological_profile['spontaneity'],
                'description': 'Plans change spontaneously, goes to different location',
                'outcome': 'Alternative activity',
                'satisfaction_level': 0.6
            }
            scenarios.append(change)
        
        # Scenario 4: Early return
        early = {
            'scenario': 'Early Return',
            'probability': 0.1,
            'description': 'Activity completes faster than expected or gets cancelled',
            'outcome': 'Quick completion or cancellation',
            'satisfaction_level': 0.5
        }
        scenarios.append(early)
        
        return sorted(scenarios, key=lambda x: x['probability'], reverse=True)
    
    def _assess_risks(self, location: Dict, now: datetime,
                     destinations: List[Dict], psychological: Dict,
                     temporal: Dict) -> Dict:
        """Assess risks and unusual factors"""
        risks = {
            'overall_risk_level': 0.0,
            'risk_factors': [],
            'unusual_patterns': [],
            'safety_concerns': []
        }
        
        hour = now.hour
        
        # Time-based risks
        if hour >= 23 or hour <= 5:
            risks['risk_factors'].append({
                'factor': 'Unusual hours',
                'risk_level': 0.6,
                'description': 'Activity during late night/early morning'
            })
            risks['overall_risk_level'] += 0.3
        
        # Stress-based risks
        if psychological.get('stress_level', 0) > 0.7:
            risks['risk_factors'].append({
                'factor': 'High stress level',
                'risk_level': 0.4,
                'description': 'Elevated stress may affect decision making'
            })
            risks['overall_risk_level'] += 0.2
        
        # Routine deviation
        consistency = self.behavioral_patterns.get('consistency_score', 0.5)
        if consistency > 0.7:  # Usually consistent
            # Current activity might be unusual
            risks['unusual_patterns'].append({
                'pattern': 'Deviation from routine',
                'severity': 0.5,
                'description': 'Activity differs from typical pattern'
            })
        
        # Energy level concerns
        if psychological.get('energy_level', 0.5) < 0.3:
            risks['safety_concerns'].append({
                'concern': 'Low energy level',
                'severity': 0.4,
                'description': 'Fatigue may impact alertness'
            })
            risks['overall_risk_level'] += 0.15
        
        # Normalize overall risk
        risks['overall_risk_level'] = min(1.0, risks['overall_risk_level'])
        
        return risks
    
    def _analyze_decision_factors(self, now: datetime, location: Dict,
                                  context: Dict, temporal: Dict,
                                  psychological: Dict) -> List[Dict]:
        """Analyze what factors are influencing decisions"""
        factors = []
        
        # Time pressure
        if temporal.get('typical_activity') in ['work_commute', 'evening_commute']:
            factors.append({
                'factor': 'Time pressure',
                'influence': 0.8,
                'description': 'Commute time creates urgency'
            })
        
        # Social influence
        if psychological.get('social_desire', 0) > 0.6:
            factors.append({
                'factor': 'Social motivation',
                'influence': psychological['social_desire'],
                'description': 'Desire for social interaction'
            })
        
        # Routine adherence
        routine_score = self.psychological_profile.get('routine_adherence', 0.5)
        if routine_score > 0.6:
            factors.append({
                'factor': 'Routine adherence',
                'influence': routine_score,
                'description': 'Strong tendency to follow established patterns'
            })
        
        # Energy level
        energy = psychological.get('energy_level', 0.5)
        factors.append({
            'factor': 'Energy level',
            'influence': energy,
            'description': f'{"High" if energy > 0.7 else "Medium" if energy > 0.4 else "Low"} energy influences activity choice'
        })
        
        # Work obligations
        if self.profile.get('job'):
            if temporal.get('typical_activity') == 'at_work':
                factors.append({
                    'factor': 'Work obligation',
                    'influence': 0.9,
                    'description': 'Work schedule dictates location'
                })
        
        return sorted(factors, key=lambda x: x['influence'], reverse=True)
    
    def _generate_alternative_scenarios(self, destinations: List[Dict],
                                       decision_factors: List[Dict],
                                       psychological: Dict) -> List[Dict]:
        """Generate alternative scenarios based on decision factors"""
        alternatives = []
        
        # Alternative based on spontaneity
        if self.psychological_profile.get('spontaneity', 0) > 0.5:
            alternatives.append({
                'scenario': 'Spontaneous detour',
                'probability': 0.2 * self.psychological_profile['spontaneity'],
                'trigger': 'Sees interesting place or opportunity',
                'outcome': 'Unplanned stop or activity'
            })
        
        # Alternative based on social tendency
        if psychological.get('social_desire', 0) > 0.7:
            alternatives.append({
                'scenario': 'Social meetup',
                'probability': 0.3,
                'trigger': 'Friend/family invitation or opportunity',
                'outcome': 'Change plans to socialize'
            })
        
        # Alternative based on fatigue
        if psychological.get('energy_level', 0.5) < 0.3:
            alternatives.append({
                'scenario': 'Early return home',
                'probability': 0.4,
                'trigger': 'Fatigue or low energy',
                'outcome': 'Shortened activity, return to rest'
            })
        
        # Alternative based on stress
        if psychological.get('stress_level', 0) > 0.7:
            alternatives.append({
                'scenario': 'Stress relief detour',
                'probability': 0.25,
                'trigger': 'High stress level',
                'outcome': 'Stop for stress relief activity (park, cafe, etc.)'
            })
        
        return alternatives
    
    def _generate_meta_analysis(self, prediction: Dict) -> Dict:
        """Generate meta-analysis of the prediction itself"""
        meta = {
            'prediction_quality': 'medium',
            'data_sufficiency': 'medium',
            'factors_considered': 0,
            'confidence_assessment': '',
            'improvements_needed': []
        }
        
        # Count factors
        meta['factors_considered'] = (
            len(prediction.get('decision_factors', [])) +
            len(prediction.get('purpose_predictions', [])) +
            len(prediction.get('destination_predictions', [])) +
            len(prediction.get('behavioral_predictions', []))
        )
        
        # Assess confidence
        conf = prediction.get('confidence', 0.5)
        if conf > 0.8:
            meta['prediction_quality'] = 'high'
            meta['confidence_assessment'] = 'High confidence prediction based on strong patterns'
        elif conf > 0.6:
            meta['prediction_quality'] = 'good'
            meta['confidence_assessment'] = 'Good confidence with multiple supporting factors'
        elif conf > 0.4:
            meta['prediction_quality'] = 'medium'
            meta['confidence_assessment'] = 'Moderate confidence, some uncertainty'
        else:
            meta['prediction_quality'] = 'low'
            meta['confidence_assessment'] = 'Low confidence, limited data or unclear patterns'
        
        # Suggest improvements
        if len(self._load_all_historical_data()) < 100:
            meta['improvements_needed'].append('More historical data needed for better patterns')
        
        if not prediction.get('current_context'):
            meta['improvements_needed'].append('Google Maps context would improve accuracy')
        
        return meta


def main():
    """Test the advanced prediction engine"""
    engine = AdvancedOutcomePredictionEngine()
    
    # Test prediction
    test_location = {
        'latitude': 37.7749,
        'longitude': -122.4194,
        'timestamp': datetime.now().isoformat()
    }
    
    test_context = {
        'area_type': 'residential',
        'nearby_places': []
    }
    
    print("\n" + "="*80)
    print("RUNNING INSANE OUTCOME PREDICTION ALGORITHM")
    print("="*80 + "\n")
    
    prediction = engine.predict_insane_outcome(test_location, test_context)
    
    print(f"Overall Confidence: {prediction['confidence']:.1%}\n")
    
    print("EMOTIONAL STATE:")
    for key, value in prediction['emotional_state'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.1%}")
        else:
            print(f"  {key}: {value}")
    
    print("\nTOP DECISION FACTORS:")
    for factor in prediction['decision_factors'][:3]:
        print(f"  • {factor['factor']}: {factor['influence']:.1%} - {factor['description']}")
    
    print("\nOUTCOME SCENARIOS:")
    for scenario in prediction['outcome_scenarios']:
        print(f"  {scenario['scenario']} ({scenario['probability']:.1%})")
        print(f"    {scenario['description']}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
