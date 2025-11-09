# Vehicle Tracking System with AI Processing

An intelligent GPS tracking and AI prediction system designed to run on Raspberry Pi 4B. The system tracks vehicle paths, learns travel patterns, recognizes points of interest (Home, Work, etc.), and predicts destinations using AI. **Works completely offline** with automatic WiFi queue management.

## Features

### Core Functionality
- **Real-time GPS Tracking**: Continuous location monitoring with configurable update intervals
- **Offline Operation**: Full functionality without WiFi - queues operations when offline
- **AI-Powered Predictions**: Predicts destinations based on multiple factors
- **Automatic Location Recognition**: Identifies Home, Work, Gym, and other points of interest
- **Google Maps Integration**: Enriches location data with nearby places and addresses (when online)
- **Profile Management**: Creates readable text-based profiles with all tracked information

### Offline Capabilities
- GPS tracking works continuously without internet
- All location data is saved locally
- Google Maps operations are queued when offline
- Automatic processing of queued operations when WiFi reconnects
- Cached data reuse for known locations

### AI Features
- Pattern recognition for frequent locations
- Automatic identification of:
  - **Home**: Based on night visits, long durations, high frequency
  - **Work**: Based on weekday work-hour patterns
  - **Gym/Fitness**: Based on regular morning/evening visits
  - **Shopping/Errands**: Based on short visits at various times
  - **Friend/Family**: Based on weekend/evening social patterns
  - **Restaurant/Dining**: Based on meal-time visits
- Time-based pattern analysis
- Multi-factor destination prediction using:
  - User profile (age, gender, job, schedule)
  - Historical patterns
  - Time of day
  - Day of week
  - Current location context
  - Known locations proximity

## Installation

### Prerequisites
- Raspberry Pi 4B with Raspbian OS
- Python 3.7 or higher
- GPS module (or runs in simulated mode for testing)
- Optional: Google Maps API key for enhanced features

### Setup Steps

1. **Clone the repository**:
```bash
git clone https://github.com/zeinreallycancreate/cityOS---vehicle-tracking---person-tracking.git
cd cityOS---vehicle-tracking---person-tracking
```

2. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```

3. **Run initial setup**:
```bash
python3 setup.py
```

The setup wizard will guide you through:
- Personal information (age, gender, weight, job, etc.)
- Known locations (home, work, etc.)
- Schedule patterns (work hours, routines)
- System settings (GPS interval, data retention)

### Optional: Google Maps API Key

For enhanced location context (nearby places, addresses):

1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable: Places API, Geocoding API
3. Add to `config.json`:
```json
{
  "google_maps_api_key": "YOUR_API_KEY_HERE"
}
```

**Note**: The system works fully without an API key, just without nearby places data.

## Usage

### Start Tracking
```bash
python3 main.py start
# or simply
python3 main.py
```

This starts continuous GPS tracking with AI processing. The system will:
- Log GPS coordinates every 10 seconds (configurable)
- Analyze location context (online or cached)
- Run AI predictions every 5 minutes
- Update your profile automatically
- Queue operations when offline, process when online

### Run Learning Mode
Analyze historical data to improve AI predictions:
```bash
python3 main.py learn
```

### Check System Status
```bash
python3 main.py status
```

Shows:
- Setup completion
- Network status (online/offline)
- Queue size (pending operations)
- Profile status
- Data collection status

## Configuration

Edit `config.json` to customize:

```json
{
  "profile": {
    "name": "Driver1",
    "age": 30,
    "gender": "Male",
    "job": "Software Engineer",
    "work_schedule": "9am-5pm"
  },
  "known_locations": [
    {
      "name": "Home",
      "address": "123 Main St",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "category": "home"
    }
  ],
  "system_settings": {
    "gps_update_interval": 10,
    "ai_prediction_interval": 5,
    "data_retention_days": 365
  }
}
```

## File Structure

```
.
├── main.py                 # Main application entry point
├── setup.py                # Setup wizard with personal info input
├── gps_tracker.py          # GPS tracking with offline support
├── ai_processor.py         # AI prediction and pattern recognition
├── profile_manager.py      # Profile creation and management
├── network_manager.py      # WiFi detection and queue management
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # GPS logs and learned patterns
│   ├── gps_log_YYYY-MM-DD.json
│   ├── learned_patterns.json
│   ├── offline_cache.json
│   └── queue/            # Queued operations
├── logs/                  # System logs
└── profiles/             # User profiles (readable text)
    └── ProfileName.txt
```

## Profile Output

Profiles are stored as readable text files in the `profiles/` directory. Example:

```
================================================================================
PROFILE: Driver1
================================================================================
Last Updated: 2024-11-09 16:30:00

--------------------------------------------------------------------------------
PERSONAL INFORMATION
--------------------------------------------------------------------------------
Age: 30
Gender: Male
Occupation: Software Engineer
Work Hours: 9am-5pm

--------------------------------------------------------------------------------
RECOGNIZED LOCATIONS
--------------------------------------------------------------------------------

1. Home (Confidence: 92.5%)
   Location: 37.7749, -122.4194
   Visited: 28 times
   Average stay: 10.5 hours
   Why this is Home:
     • Visited 28/30 days
     • 25 night-time visits
     • Average stay: 10.5 hours

2. Work (Confidence: 87.3%)
   Location: 37.7858, -122.4064
   Visited: 22 times
   Average stay: 8.2 hours
   Why this is Work:
     • Frequent weekday visits: 20
     • 22 visits during work hours
     • Average stay: 8.2 hours

--------------------------------------------------------------------------------
LATEST AI PREDICTIONS
--------------------------------------------------------------------------------
Prediction Time: 2024-11-09 16:30:00

Predicted Destinations:

1. Confidence: 85.0%
   Destination: Home
   Reasoning:
     - Evening commute from work
     - Based on profile information (job, schedule)
```

## Offline Mode

The system is designed for offline-first operation:

1. **GPS Tracking**: Always works offline
2. **Data Logging**: All data saved locally
3. **Google Maps Lookups**: Queued when offline
   - Reverse geocoding (address lookup)
   - Nearby places search
4. **Cached Data**: Previously fetched data is reused
5. **Automatic Sync**: Queue processed when WiFi available

### Queue Management

View queue status:
```bash
python3 main.py status
```

The system automatically:
- Checks WiFi connectivity every tracking cycle
- Processes queue every 5 minutes when online
- Processes remaining queue on graceful shutdown

## Raspberry Pi Optimization

Optimized for Raspberry Pi 4B:

- Lightweight operation
- Efficient data structures
- Configurable intervals to balance accuracy vs. battery
- Automatic cleanup of old data (configurable retention)
- Minimal CPU usage in tracking loop

### Autostart on Boot

To run on startup, add to crontab:
```bash
crontab -e
```

Add line:
```
@reboot cd /path/to/cityOS---vehicle-tracking---person-tracking && python3 main.py start
```

Or create a systemd service for better control.

## AI Prediction Logic

The AI uses multiple factors to predict destinations:

### Confidence Scoring
Each prediction receives a confidence score (0-100%) based on:

1. **Profile Information** (up to 80% confidence)
   - Job and work schedule
   - Age-based behavior patterns
   - Known routines

2. **Historical Patterns** (up to 70% confidence)
   - Time-based patterns
   - Day-of-week patterns
   - Visit frequency

3. **Location Context** (up to 85% confidence)
   - Proximity to known locations
   - Area type from Google Maps
   - Nearby places

4. **Recognized Locations** (up to 95% confidence)
   - Automatically identified Home, Work, etc.
   - High confidence based on strong patterns

### Location Recognition

Automatic identification criteria:

- **Home**: 50%+ days visited, 30%+ night visits, 6+ hours average
- **Work**: 30%+ weekdays, 60%+ work hours, 3-12 hours average  
- **Gym**: 20%+ days, 70%+ morning/evening, 30min-2hr average
- **Shopping**: 15%+ days, <2hr visits, varied times
- **Friend/Family**: 10%+ days, weekend/evening, 2+ hours
- **Restaurant**: 5+ visits, 60%+ meal times, 30min-1.5hr

## Logs

System logs are stored in `logs/`:
- `main_system.log` - Main application
- `gps_tracker.log` - GPS tracking
- `ai_processor.log` - AI predictions
- `profile_manager.log` - Profile updates
- `network_manager.log` - Network status

## Data Privacy

All data is stored locally on your Raspberry Pi:
- No cloud uploads
- No external tracking
- Google Maps API only used if configured
- Complete control over your data

## Troubleshooting

### GPS Not Working
- Check GPS module connection
- System runs in simulated mode if GPS unavailable
- Check logs: `logs/gps_tracker.log`

### Google Maps Not Working
- Verify API key in `config.json`
- Check API quota limits
- System works without Google Maps (offline mode)

### Network Issues
- Check WiFi configuration
- System continues tracking offline
- View queue: `python3 main.py status`

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.