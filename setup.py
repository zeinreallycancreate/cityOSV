#!/usr/bin/env python3
"""
Initial setup wizard for the Vehicle Tracking System
Collects user information to help AI make better predictions
"""

import json
import os
from datetime import datetime


class SetupWizard:
    """Handles initial setup and configuration of the tracking system"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = {}
    
    def run(self):
        """Run the setup wizard"""
        print("=" * 60)
        print("Vehicle Tracking System - Initial Setup")
        print("=" * 60)
        print("\nWelcome! This setup will help the AI better understand and")
        print("predict travel patterns by learning about you.\n")
        
        # Create directories
        self._create_directories()
        
        # Collect profile information
        self._collect_profile_info()
        
        # Collect known locations
        self._collect_known_locations()
        
        # Collect schedule patterns
        self._collect_schedule_info()
        
        # System settings
        self._collect_system_settings()
        
        # Save configuration
        self._save_config()
        
        print("\n" + "=" * 60)
        print("Setup complete! Your profile has been created.")
        print("=" * 60)
        print(f"\nConfiguration saved to: {self.config_path}")
        print("You can now start the tracking system.\n")
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = ['data', 'logs', 'profiles']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _collect_profile_info(self):
        """Collect demographic and personal information"""
        print("\n--- Personal Information ---")
        print("(This helps the AI understand your lifestyle and predict destinations)")
        print("You can skip any field by pressing Enter\n")
        
        profile = {}
        
        # Profile name
        profile['name'] = input("Profile name (e.g., Driver1, John): ").strip() or "DefaultProfile"
        
        # Age
        age_input = input("Age: ").strip()
        profile['age'] = int(age_input) if age_input.isdigit() else None
        
        # Gender
        profile['gender'] = input("Gender: ").strip() or None
        
        # Weight
        weight_input = input("Weight (kg): ").strip()
        profile['weight'] = float(weight_input) if weight_input else None
        
        # Job/Occupation
        profile['job'] = input("Job/Occupation: ").strip() or None
        
        # Work schedule
        profile['work_schedule'] = input("Typical work hours (e.g., 9am-5pm): ").strip() or None
        
        # Additional info
        print("\nAny additional information that might help predict travel patterns?")
        print("(e.g., 'gym member', 'has kids in school', 'night shift worker')")
        profile['additional_info'] = input("Additional info: ").strip() or None
        
        profile['created_date'] = datetime.now().isoformat()
        
        self.config['profile'] = profile
    
    def _collect_known_locations(self):
        """Collect known frequent locations"""
        print("\n--- Known Locations ---")
        print("Enter locations you frequently visit to help the AI recognize patterns")
        print("Press Enter on location name to finish\n")
        
        locations = []
        
        while True:
            name = input("Location name (e.g., Home, Work, Gym): ").strip()
            if not name:
                break
            
            address = input(f"  Address for {name}: ").strip()
            lat_input = input(f"  Latitude (optional): ").strip()
            lon_input = input(f"  Longitude (optional): ").strip()
            category = input(f"  Category (e.g., work, leisure, shopping): ").strip()
            
            location = {
                'name': name,
                'address': address,
                'latitude': float(lat_input) if lat_input else None,
                'longitude': float(lon_input) if lon_input else None,
                'category': category or 'general'
            }
            locations.append(location)
            print(f"  ✓ Added {name}\n")
        
        self.config['known_locations'] = locations
    
    def _collect_schedule_info(self):
        """Collect typical schedule patterns"""
        print("\n--- Schedule Patterns ---")
        print("Help the AI understand your routine\n")
        
        schedule = {}
        
        # Typical days
        schedule['work_days'] = input("Typical work days (e.g., Mon-Fri): ").strip() or "Mon-Fri"
        
        # Morning routine
        schedule['morning_routine'] = input("Morning routine time (e.g., leave home at 8am): ").strip() or None
        
        # Evening routine
        schedule['evening_routine'] = input("Evening routine time (e.g., return home at 6pm): ").strip() or None
        
        # Weekend patterns
        schedule['weekend_pattern'] = input("Weekend activity pattern: ").strip() or None
        
        self.config['schedule_patterns'] = schedule
    
    def _collect_system_settings(self):
        """Collect system configuration settings"""
        print("\n--- System Settings ---")
        
        settings = {}
        
        # GPS update interval
        interval_input = input("GPS update interval in seconds [default: 10]: ").strip()
        settings['gps_update_interval'] = int(interval_input) if interval_input.isdigit() else 10
        
        # Data retention
        retention_input = input("Data retention in days [default: 365]: ").strip()
        settings['data_retention_days'] = int(retention_input) if retention_input.isdigit() else 365
        
        # AI prediction frequency
        prediction_input = input("AI analysis interval in minutes [default: 5]: ").strip()
        settings['ai_prediction_interval'] = int(prediction_input) if prediction_input.isdigit() else 5
        
        settings['raspberry_pi_optimized'] = True
        settings['setup_completed'] = True
        settings['setup_date'] = datetime.now().isoformat()
        
        self.config['system_settings'] = settings
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, indent=2, fp=f)


def main():
    """Main entry point for setup wizard"""
    # Check if setup already completed
    if os.path.exists('config.json'):
        response = input("Configuration already exists. Run setup again? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Setup cancelled.")
            return
    
    wizard = SetupWizard()
    wizard.run()


if __name__ == '__main__':
    main()
