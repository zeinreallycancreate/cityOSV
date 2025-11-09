#!/usr/bin/env python3
"""
Profile Manager
Creates and updates user profiles with all tracked information
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import logging


class ProfileManager:
    """Manages user profiles stored as readable text files"""
    
    def __init__(self, config_path="config.json", profiles_dir="profiles"):
        self.config = self._load_config(config_path)
        self.profiles_dir = profiles_dir
        self.logger = self._setup_logger()
        
        # Ensure profiles directory exists
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Get profile name from config
        self.profile_name = self.config.get('profile', {}).get('name', 'DefaultProfile')
        self.profile_file = os.path.join(self.profiles_dir, f"{self.profile_name}.txt")
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('ProfileManager')
        logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/profile_manager.log')
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
    
    def create_profile(self, predictions: Dict = None, learned_patterns: Dict = None):
        """
        Create or update the profile text file with all information
        
        Args:
            predictions: Latest AI predictions
            learned_patterns: Learned travel patterns
        """
        self.logger.info(f"Creating/updating profile: {self.profile_name}")
        
        profile_data = self._compile_profile_data(predictions, learned_patterns)
        
        # Write profile as readable text
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            f.write(self._format_profile(profile_data))
        
        self.logger.info(f"Profile saved to: {self.profile_file}")
    
    def _compile_profile_data(self, predictions: Dict = None, 
                             learned_patterns: Dict = None) -> Dict:
        """Compile all profile information"""
        data = {
            'basic_info': self.config.get('profile', {}),
            'known_locations': self.config.get('known_locations', []),
            'schedule_patterns': self.config.get('schedule_patterns', {}),
            'learned_patterns': learned_patterns or {},
            'latest_predictions': predictions or {},
            'last_updated': datetime.now().isoformat()
        }
        
        return data
    
    def _format_profile(self, data: Dict) -> str:
        """Format profile data as readable text"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"PROFILE: {self.profile_name}")
        lines.append("=" * 80)
        lines.append(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Basic Information
        lines.append("-" * 80)
        lines.append("PERSONAL INFORMATION")
        lines.append("-" * 80)
        basic_info = data.get('basic_info', {})
        
        if basic_info.get('age'):
            lines.append(f"Age: {basic_info['age']}")
        if basic_info.get('gender'):
            lines.append(f"Gender: {basic_info['gender']}")
        if basic_info.get('weight'):
            lines.append(f"Weight: {basic_info['weight']} kg")
        if basic_info.get('job'):
            lines.append(f"Occupation: {basic_info['job']}")
        if basic_info.get('work_schedule'):
            lines.append(f"Work Hours: {basic_info['work_schedule']}")
        if basic_info.get('additional_info'):
            lines.append(f"Additional Info: {basic_info['additional_info']}")
        if basic_info.get('created_date'):
            created = datetime.fromisoformat(basic_info['created_date'])
            lines.append(f"Profile Created: {created.strftime('%Y-%m-%d')}")
        
        lines.append("")
        
        # Known Locations
        lines.append("-" * 80)
        lines.append("KNOWN LOCATIONS")
        lines.append("-" * 80)
        known_locs = data.get('known_locations', [])
        
        if known_locs:
            for i, loc in enumerate(known_locs, 1):
                lines.append(f"\n{i}. {loc.get('name', 'Unknown')}")
                if loc.get('address'):
                    lines.append(f"   Address: {loc['address']}")
                if loc.get('category'):
                    lines.append(f"   Category: {loc['category']}")
                if loc.get('latitude') and loc.get('longitude'):
                    lines.append(f"   Coordinates: {loc['latitude']}, {loc['longitude']}")
        else:
            lines.append("No known locations configured.")
        
        lines.append("")
        
        # Schedule Patterns
        lines.append("-" * 80)
        lines.append("SCHEDULE PATTERNS")
        lines.append("-" * 80)
        schedule = data.get('schedule_patterns', {})
        
        if schedule:
            if schedule.get('work_days'):
                lines.append(f"Work Days: {schedule['work_days']}")
            if schedule.get('morning_routine'):
                lines.append(f"Morning Routine: {schedule['morning_routine']}")
            if schedule.get('evening_routine'):
                lines.append(f"Evening Routine: {schedule['evening_routine']}")
            if schedule.get('weekend_pattern'):
                lines.append(f"Weekend Pattern: {schedule['weekend_pattern']}")
        else:
            lines.append("No schedule patterns configured.")
        
        lines.append("")
        
        # Learned Patterns
        lines.append("-" * 80)
        lines.append("AI LEARNED PATTERNS")
        lines.append("-" * 80)
        learned = data.get('learned_patterns', {})
        
        if learned:
            # Recognized locations (Home, Work, etc.)
            recognized_locs = learned.get('recognized_locations', [])
            if recognized_locs:
                lines.append("\nRECOGNIZED LOCATIONS:")
                lines.append("")
                for i, loc in enumerate(recognized_locs, 1):
                    loc_type = loc.get('type', 'Unknown')
                    confidence = loc.get('confidence', 0) * 100
                    location = loc.get('location', {})
                    lat = location.get('latitude', 0)
                    lon = location.get('longitude', 0)
                    visits = loc.get('visit_count', 0)
                    avg_duration = loc.get('average_duration_hours', 0)
                    
                    lines.append(f"{i}. {loc_type} (Confidence: {confidence:.1f}%)")
                    lines.append(f"   Location: {lat:.4f}, {lon:.4f}")
                    lines.append(f"   Visited: {visits} times")
                    lines.append(f"   Average stay: {avg_duration:.1f} hours")
                    
                    # Add reasoning
                    reasoning = loc.get('reasoning', [])
                    if reasoning:
                        lines.append(f"   Why this is {loc_type}:")
                        for reason in reasoning:
                            lines.append(f"     • {reason}")
                    
                    # Statistics
                    stats = loc.get('statistics', {})
                    if stats:
                        lines.append(f"   Visit patterns:")
                        if stats.get('night_visits'):
                            lines.append(f"     • Night visits: {stats['night_visits']}")
                        if stats.get('morning_visits'):
                            lines.append(f"     • Morning visits: {stats['morning_visits']}")
                        if stats.get('work_hours_visits'):
                            lines.append(f"     • Work hours: {stats['work_hours_visits']}")
                        if stats.get('evening_visits'):
                            lines.append(f"     • Evening visits: {stats['evening_visits']}")
                        if stats.get('weekday_visits'):
                            lines.append(f"     • Weekday visits: {stats['weekday_visits']}")
                        if stats.get('weekend_visits'):
                            lines.append(f"     • Weekend visits: {stats['weekend_visits']}")
                    
                    lines.append("")
            
            # Frequent locations
            frequent_locs = learned.get('frequent_locations', [])
            if frequent_locs:
                lines.append("Other Frequently Visited Locations:")
                for i, loc in enumerate(frequent_locs[:10], 1):
                    lat = loc.get('location', {}).get('latitude', 0)
                    lon = loc.get('location', {}).get('longitude', 0)
                    visits = loc.get('visit_count', 0)
                    lines.append(f"  {i}. Location ({lat:.4f}, {lon:.4f}) - {visits} visits")
            
            # Time patterns
            time_patterns = learned.get('time_patterns', {})
            if time_patterns:
                lines.append("\nTime-Based Patterns:")
                hours = sorted([(int(h), data) for h, data in time_patterns.items()])
                for hour, _ in hours[:5]:
                    lines.append(f"  Frequently active at {hour:02d}:00")
        else:
            lines.append("No patterns learned yet. More data needed for analysis.")
        
        lines.append("")
        
        # Latest Predictions
        lines.append("-" * 80)
        lines.append("LATEST AI PREDICTIONS")
        lines.append("-" * 80)
        predictions = data.get('latest_predictions', {})
        
        if predictions and predictions.get('predictions'):
            pred_time = predictions.get('timestamp', '')
            if pred_time:
                pred_dt = datetime.fromisoformat(pred_time)
                lines.append(f"Prediction Time: {pred_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            lines.append("\nPredicted Destinations:")
            for i, pred in enumerate(predictions['predictions'][:5], 1):
                loc = pred.get('location', {})
                confidence = pred.get('confidence', 0) * 100
                
                lines.append(f"\n{i}. Confidence: {confidence:.1f}%")
                
                if loc.get('name'):
                    lines.append(f"   Destination: {loc['name']}")
                if loc.get('address'):
                    lines.append(f"   Address: {loc['address']}")
                if loc.get('category'):
                    lines.append(f"   Category: {loc['category']}")
                
                reasons = pred.get('reasons', [])
                if reasons:
                    lines.append(f"   Reasoning:")
                    for reason in reasons:
                        lines.append(f"     - {reason}")
            
            # Reasoning summary
            reasoning = predictions.get('reasoning', [])
            if reasoning:
                lines.append("\nAnalysis Factors Used:")
                for reason in reasoning:
                    lines.append(f"  • {reason}")
        else:
            lines.append("No predictions available yet.")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF PROFILE")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_profile_path(self) -> str:
        """Get path to the profile file"""
        return self.profile_file
    
    def profile_exists(self) -> bool:
        """Check if profile file exists"""
        return os.path.exists(self.profile_file)


def main():
    """Test profile manager"""
    manager = ProfileManager()
    
    # Create sample profile
    sample_predictions = {
        'timestamp': datetime.now().isoformat(),
        'predictions': [
            {
                'location': {'name': 'Work', 'category': 'work'},
                'confidence': 0.85,
                'reasons': ['Morning commute time', 'Weekday pattern']
            }
        ],
        'reasoning': ['Based on time patterns', 'Based on profile information']
    }
    
    manager.create_profile(predictions=sample_predictions)
    print(f"Profile created at: {manager.get_profile_path()}")


if __name__ == '__main__':
    main()
