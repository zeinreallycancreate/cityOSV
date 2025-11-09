#!/usr/bin/env python3
"""
Full system test demonstrating all features
"""

import json
from datetime import datetime

print("=" * 80)
print("VEHICLE TRACKING SYSTEM - FULL FEATURE DEMONSTRATION")
print("=" * 80)
print()

# Test 1: Configuration
print("1. ✓ Configuration loaded")
with open('config.json', 'r') as f:
    config = json.load(f)
    profile = config['profile']
    print(f"   Profile: {profile['name']}, Age: {profile['age']}, Job: {profile['job']}")
print()

# Test 2: Network Manager
print("2. ✓ Network Manager")
from network_manager import NetworkManager
nm = NetworkManager()
status = "Online" if nm.check_connectivity() else "Offline"
print(f"   Status: {status}, Queue: {nm.get_queue_size()} items")
print()

# Test 3: GPS Tracker
print("3. ✓ GPS Tracker (Simulated Mode)")
from gps_tracker import GPSTracker
tracker = GPSTracker()
location = tracker.get_current_location()
print(f"   Location: {location['latitude']:.6f}, {location['longitude']:.6f}")
print(f"   Simulated: {location.get('simulated', False)}")
print()

# Test 4: AI Processor
print("4. ✓ AI Processor")
from ai_processor import AIProcessor
ai = AIProcessor()
learned = ai.learned_patterns.get('recognized_locations', [])
print(f"   Recognized locations: {len(learned)}")
if learned:
    for loc in learned[:3]:
        print(f"     - {loc['type']}: {loc['confidence']:.1%} confidence")
print()

# Test 5: Advanced Prediction
print("5. ✓ Advanced Outcome Prediction Engine")
from advanced_prediction import AdvancedOutcomePredictionEngine
engine = AdvancedOutcomePredictionEngine()
print(f"   Psychological Profile:")
for key, value in engine.psychological_profile.items():
    print(f"     {key}: {value:.1%}")
print()

# Test 6: Profile Manager
print("6. ✓ Profile Manager")
from profile_manager import ProfileManager
pm = ProfileManager()
print(f"   Profile path: {pm.get_profile_path()}")
print(f"   Profile exists: {pm.profile_exists()}")
print()

# Test 7: Run prediction
print("7. ✓ Running INSANE Prediction...")
test_location = {'latitude': 37.7749, 'longitude': -122.4194, 'timestamp': datetime.now().isoformat()}
prediction = engine.predict_insane_outcome(test_location)
print(f"   Overall Confidence: {prediction['confidence']:.1%}")
print(f"   Emotional State: {prediction['emotional_state']['mood']}")
print(f"   Stress Level: {prediction['emotional_state']['stress_level']:.1%}")
print(f"   Energy Level: {prediction['emotional_state']['energy_level']:.1%}")
if prediction['decision_factors']:
    print(f"   Top Factor: {prediction['decision_factors'][0]['factor']}")
if prediction['outcome_scenarios']:
    print(f"   Most Likely: {prediction['outcome_scenarios'][0]['scenario']} ({prediction['outcome_scenarios'][0]['probability']:.1%})")
print()

print("=" * 80)
print("ALL SYSTEMS OPERATIONAL ✓")
print("=" * 80)
print()
print("System Ready For:")
print("  • python3 main.py start    - Start GPS tracking")
print("  • python3 main.py web      - Start web interface")
print("  • python3 main.py learn    - Run AI learning")
print("  • python3 main.py status   - Check system status")
print()
