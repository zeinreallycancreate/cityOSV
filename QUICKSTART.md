# Quick Start Guide

## First Time Setup

1. **Run the installation script** (recommended):
   ```bash
   ./install.sh
   ```
   
   This automatically handles:
   - Detecting externally managed Python (common on modern systems)
   - Creating a virtual environment if needed
   - Installing all dependencies
   - Verifying the installation
   
   **If you see "externally managed" error**, the script handles it automatically!

2. **Alternative: Manual setup**

   a. **Check dependencies (recommended):**
   ```bash
   python3 check_dependencies.py
   ```
   This will show which packages need to be installed.

   b. **For modern systems (Python 3.11+):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip3 install -r requirements.txt
   ```
   
   c. **For older systems:**
   ```bash
   pip3 install -r requirements.txt
   ```
   
   If you get permission errors:
   ```bash
   pip3 install --user -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python3 check_dependencies.py
   ```
   All checks should pass (✓).

4. **Run setup wizard:**
   ```bash
   # If using virtual environment
   source venv/bin/activate
   python3 setup.py
   
   # Or with convenience script
   ./run.sh setup.py
   ```
   
   Enter your information:
   - Personal info (age, gender, weight, job)
   - Known locations (Home, Work, etc.)
   - Schedule patterns
   - System settings

5. **Optional: Add Google Maps API key**
   Edit `config.json` and add:
   ```json
   "google_maps_api_key": "YOUR_API_KEY"
   ```

## Daily Use

**Remember**: If you used a virtual environment, activate it first:
```bash
source venv/bin/activate
```

Or use the convenience script: `./run.sh main.py <command>`

### Start Tracking (Runs in Background)
```bash
python3 main.py start
```
Tracks GPS continuously and logs data.

### View Dashboard (Recommended)
```bash
sudo python3 main.py web
# or on port 8080:
python3 main.py web 8080
```
Open browser to `http://localhost`

### Check Status
```bash
python3 main.py status
```

### Run AI Learning (Weekly)
```bash
python3 main.py learn
```
Analyzes past 30 days to improve predictions.

## Understanding Your Profile

Profile is at: `profiles/YourName.txt`

Contains:
- Personal information
- Known locations
- Schedule patterns
- **Recognized locations** (auto-detected)
  - Home
  - Work
  - Gym
  - Shopping spots
  - Friend/family places
- AI predictions with confidence scores

## Offline Operation

System works WITHOUT WiFi:
- GPS tracking continues
- All data saved locally
- Google Maps operations queued
- Auto-processes when WiFi returns

Check queue: `python3 main.py status`

## Web Dashboard Features

Access at `http://localhost` (or custom port)

### Dashboard Tab
- System status (online/offline)
- Total locations tracked
- Days of data
- Recognized locations count
- Latest predictions

### Profile Tab
- Your personal information
- Known locations
- Schedule patterns
- JSON data export

### Map Tab
- Visual map of tracked locations (placeholder for now)

### Logs Tab
- Recent GPS data
- JSON format logs

## Advanced Prediction Explained

The INSANE prediction engine analyzes:

1. **What time it is** - morning, evening, weekend?
2. **How you feel** - stressed, energetic, tired?
3. **Where you are** - home area, work area, shopping?
4. **Your patterns** - where do you usually go now?
5. **Your personality** - spontaneous or routine?
6. **Why** - commute, leisure, errands?
7. **When you'll arrive** - estimated times
8. **What might happen** - multiple scenarios
9. **Risks** - unusual patterns?
10. **What's influencing you** - work, social, health?
11. **Alternative outcomes** - what if scenarios?

**Confidence Scores:**
- 80-100%: Very confident (strong patterns)
- 60-80%: Good confidence (clear indicators)
- 40-60%: Moderate (some uncertainty)
- Below 40%: Low confidence (unusual situation)

## Recognized Location Criteria

### Home (92%+ confidence)
- Visited 50%+ of days
- 30%+ visits at night (10pm-6am)
- Average stay > 6 hours

### Work (87%+ confidence)
- Visited 30%+ of weekdays
- 60%+ visits during work hours (9am-5pm)
- Average stay 3-12 hours

### Gym (70% confidence)
- Visited 20%+ of days
- 70%+ morning/evening visits
- Average stay 30min-2hrs

### Shopping (65% confidence)
- Visited 15%+ of days
- Stay < 2 hours
- Various times of day

### Friend/Family (60% confidence)
- Visited 10%+ of days
- Weekend or evening pattern
- Stay > 2 hours

## Raspberry Pi Optimization

### Autostart on Boot
```bash
crontab -e
```
Add (adjust path as needed):
```
# If using virtual environment
@reboot cd /path/to/repo && source venv/bin/activate && python3 main.py start &
@reboot cd /path/to/repo && source venv/bin/activate && python3 main.py web &

# Or without virtual environment
@reboot cd /path/to/repo && python3 main.py start &
@reboot cd /path/to/repo && python3 main.py web &
```

### Check Logs
```bash
tail -f logs/main_system.log
tail -f logs/gps_tracker.log
tail -f logs/ai_processor.log
```

### Storage Management
Data retention (default 365 days) configured in setup.
Clean old data manually:
```bash
rm data/gps_log_2023-*.json  # Delete 2023 data
```

## Troubleshooting

### "Externally Managed" Error

If you see:
```
error: externally-managed-environment
```

**This is normal on modern systems!** Solutions:

1. **Use the install script** (easiest):
   ```bash
   ./install.sh
   ```

2. **Or create virtual environment manually**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

3. **Always activate before use**:
   ```bash
   source venv/bin/activate
   ```

### ModuleNotFoundError or Import Errors

If you see `ModuleNotFoundError` when running the system:

```bash
# If using virtual environment, activate it first!
source venv/bin/activate

# Check what's missing
python3 check_dependencies.py

# Install all dependencies
pip3 install -r requirements.txt
```

**Common fixes:**
- **Externally managed**: Use virtual environment (see above)
- Upgrade pip: `pip3 install --upgrade pip`
- Check Python version: `python3 --version` (need 3.7+)
- Install individually if batch fails (see README.md)

### No GPS Data
- Check GPS module connection
- System runs in simulated mode for testing
- Real GPS will activate when module detected

### Web Interface Port 80 Permission Denied
```bash
# Use sudo
sudo python3 main.py web

# Or use alternate port
python3 main.py web 8080
```

### Google Maps Not Working
- Check API key in `config.json`
- Verify API quota
- System works without it (offline mode)

### Queue Growing Large
- Check WiFi connection
- Run: `python3 main.py status`
- Operations process automatically when online

## Privacy & Security

✓ All data stored locally on your Pi
✓ No cloud uploads
✓ No external tracking
✓ Google Maps only used if you configure it
✓ Complete data control

## Support

For issues:
1. Check logs in `logs/` directory
2. Run `python3 main.py status`
3. Review README.md
4. Open GitHub issue

## Advanced Usage

### Custom Intervals
Edit `config.json`:
```json
{
  "system_settings": {
    "gps_update_interval": 10,      // seconds
    "ai_prediction_interval": 5,    // minutes
    "data_retention_days": 365
  }
}
```

### API Endpoints

When web server running:
- `GET /api/status` - System status
- `GET /api/locations?days=7` - GPS data
- `GET /api/recognized-locations` - Auto-detected places
- `GET /api/predictions` - AI predictions
- `GET /api/profile` - Profile data
- `GET /api/daily-summary/<date>` - Day summary

Example:
```bash
curl http://localhost/api/status | python3 -m json.tool
```

### Export Data

GPS logs: `data/gps_log_*.json`
Profile: `profiles/YourName.txt`
Patterns: `data/learned_patterns.json`

Copy to backup:
```bash
tar -czf backup.tar.gz data/ profiles/ config.json
```

## Getting Started Checklist

- [ ] Install Python 3.7+
- [ ] Install dependencies: `pip3 install -r requirements.txt`
- [ ] Run setup: `python3 setup.py`
- [ ] (Optional) Add Google Maps API key
- [ ] Test: `python3 main.py status`
- [ ] Start tracking: `python3 main.py start`
- [ ] Open dashboard: `python3 main.py web`
- [ ] After 1 week: `python3 main.py learn`

## Tips for Best Results

1. **Let it learn** - System improves with more data (7+ days)
2. **Be consistent** - Regular routines = better recognition
3. **Update profile** - Re-run `python3 setup.py` if life changes
4. **Check weekly** - Run learning mode weekly
5. **Use web dashboard** - Visual feedback helps understand patterns
6. **Trust the AI** - Higher confidence = more accurate

Enjoy your intelligent vehicle tracking system! 🚗🤖
