#!/usr/bin/env python3
"""
Web Server for Vehicle Tracking System
Provides web interface on localhost port 80 to view all collected information
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
import json
import os
import glob
from datetime import datetime, timedelta
import logging

from network_manager import NetworkManager
from profile_manager import ProfileManager
from ai_processor import AIProcessor


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vehicle-tracking-system-2024'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WebServer')


def load_config():
    """Load configuration"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {}


def get_recent_locations(days=7):
    """Get recent GPS locations"""
    locations = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = cutoff_date + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        log_file = f'data/gps_log_{date_str}.json'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                day_logs = json.load(f)
                locations.extend(day_logs)
    
    return locations


def get_system_stats():
    """Get system statistics"""
    stats = {
        'total_locations': 0,
        'days_tracked': 0,
        'recognized_locations': 0,
        'queue_size': 0,
        'online': False,
        'last_update': None
    }
    
    # Count GPS logs
    log_files = glob.glob('data/gps_log_*.json')
    stats['days_tracked'] = len(log_files)
    
    for log_file in log_files:
        with open(log_file, 'r') as f:
            logs = json.load(f)
            stats['total_locations'] += len(logs)
    
    # Get recognized locations
    if os.path.exists('data/learned_patterns.json'):
        with open('data/learned_patterns.json', 'r') as f:
            patterns = json.load(f)
            stats['recognized_locations'] = len(patterns.get('recognized_locations', []))
    
    # Network status
    network_mgr = NetworkManager()
    stats['online'] = network_mgr.check_connectivity()
    stats['queue_size'] = network_mgr.get_queue_size()
    
    # Last update
    if log_files:
        latest_log = sorted(log_files)[-1]
        with open(latest_log, 'r') as f:
            logs = json.load(f)
            if logs:
                stats['last_update'] = logs[-1].get('timestamp')
    
    return stats


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Get system status"""
    config = load_config()
    stats = get_system_stats()
    
    return jsonify({
        'status': 'running',
        'profile': config.get('profile', {}),
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/locations')
def api_locations():
    """Get recent GPS locations"""
    days = int(request.args.get('days', 7))
    locations = get_recent_locations(days)
    
    # Format for map display
    formatted = []
    for loc in locations:
        location_data = loc.get('location', {})
        formatted.append({
            'lat': location_data.get('latitude'),
            'lon': location_data.get('longitude'),
            'timestamp': location_data.get('timestamp'),
            'speed': location_data.get('speed'),
            'altitude': location_data.get('altitude')
        })
    
    return jsonify({
        'count': len(formatted),
        'locations': formatted
    })


@app.route('/api/recognized-locations')
def api_recognized_locations():
    """Get recognized locations (Home, Work, etc.)"""
    if not os.path.exists('data/learned_patterns.json'):
        return jsonify({'locations': []})
    
    with open('data/learned_patterns.json', 'r') as f:
        patterns = json.load(f)
    
    recognized = patterns.get('recognized_locations', [])
    
    return jsonify({
        'count': len(recognized),
        'locations': recognized
    })


@app.route('/api/predictions')
def api_predictions():
    """Get latest AI predictions"""
    # This would be updated by the main tracking system
    # For now, generate on-demand
    try:
        ai_processor = AIProcessor()
        
        # Get latest location
        locations = get_recent_locations(days=1)
        if not locations:
            return jsonify({'predictions': []})
        
        latest = locations[-1]
        location = latest.get('location', {})
        context = latest.get('context', {})
        
        prediction = ai_processor.predict_destination(location, context)
        
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        return jsonify({'error': str(e), 'predictions': []})


@app.route('/api/profile')
def api_profile():
    """Get profile data"""
    config = load_config()
    
    profile_data = {
        'basic_info': config.get('profile', {}),
        'known_locations': config.get('known_locations', []),
        'schedule_patterns': config.get('schedule_patterns', {}),
    }
    
    # Add learned patterns if available
    if os.path.exists('data/learned_patterns.json'):
        with open('data/learned_patterns.json', 'r') as f:
            profile_data['learned_patterns'] = json.load(f)
    
    return jsonify(profile_data)


@app.route('/api/daily-summary/<date>')
def api_daily_summary(date):
    """Get summary for a specific day"""
    log_file = f'data/gps_log_{date}.json'
    
    if not os.path.exists(log_file):
        return jsonify({'error': 'No data for this date'}), 404
    
    with open(log_file, 'r') as f:
        logs = json.load(f)
    
    # Calculate summary
    summary = {
        'date': date,
        'total_points': len(logs),
        'start_time': logs[0].get('timestamp') if logs else None,
        'end_time': logs[-1].get('timestamp') if logs else None,
        'unique_locations': set()
    }
    
    for log in logs:
        loc = log.get('location', {})
        lat = round(loc.get('latitude', 0), 3)
        lon = round(loc.get('longitude', 0), 3)
        summary['unique_locations'].add(f"{lat},{lon}")
    
    summary['unique_locations'] = len(summary['unique_locations'])
    
    return jsonify(summary)


@app.route('/profile')
def profile_page():
    """Profile page"""
    return render_template('profile.html')


@app.route('/map')
def map_page():
    """Map view page"""
    return render_template('map.html')


@app.route('/logs')
def logs_page():
    """Logs page"""
    return render_template('logs.html')


def create_templates():
    """Create HTML templates"""
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Create index.html
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Tracking System Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .nav {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            font-weight: 500;
        }
        .nav a:hover { text-decoration: underline; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-card .label {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-online { background: #4caf50; }
        .status-offline { background: #f44336; }
        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #667eea;
        }
        .location-list {
            list-style: none;
        }
        .location-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .location-item:last-child { border-bottom: none; }
        .location-name {
            font-weight: 500;
            font-size: 16px;
        }
        .location-confidence {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        .location-details {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 Vehicle Tracking System</h1>
        <p>AI-Powered GPS Tracking & Destination Prediction</p>
    </div>
    
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/map">Map View</a>
            <a href="/logs">Logs</a>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <h3>System Status</h3>
                <div class="value" id="status">
                    <span class="status-indicator status-offline"></span>
                    Loading...
                </div>
            </div>
            <div class="stat-card">
                <h3>Total Locations</h3>
                <div class="value" id="total-locations">-</div>
                <div class="label">GPS points tracked</div>
            </div>
            <div class="stat-card">
                <h3>Days Tracked</h3>
                <div class="value" id="days-tracked">-</div>
                <div class="label">days of data</div>
            </div>
            <div class="stat-card">
                <h3>Recognized Places</h3>
                <div class="value" id="recognized-count">-</div>
                <div class="label">identified locations</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📍 Recognized Locations</h2>
            <ul class="location-list" id="recognized-locations">
                <li class="loading">Loading recognized locations...</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>🎯 Latest AI Predictions</h2>
            <ul class="location-list" id="predictions">
                <li class="loading">Loading predictions...</li>
            </ul>
        </div>
    </div>
    
    <script>
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const stats = data.stats;
                
                // Update status
                const statusIndicator = stats.online ? 
                    '<span class="status-indicator status-online"></span>Online' :
                    '<span class="status-indicator status-offline"></span>Offline';
                document.getElementById('status').innerHTML = statusIndicator;
                
                // Update stats
                document.getElementById('total-locations').textContent = stats.total_locations.toLocaleString();
                document.getElementById('days-tracked').textContent = stats.days_tracked;
                document.getElementById('recognized-count').textContent = stats.recognized_locations;
                
            } catch (error) {
                console.error('Error loading status:', error);
            }
        }
        
        async function loadRecognizedLocations() {
            try {
                const response = await fetch('/api/recognized-locations');
                const data = await response.json();
                
                const list = document.getElementById('recognized-locations');
                
                if (data.locations.length === 0) {
                    list.innerHTML = '<li class="loading">No recognized locations yet. More data needed.</li>';
                    return;
                }
                
                list.innerHTML = data.locations.map(loc => `
                    <li class="location-item">
                        <div>
                            <div class="location-name">${loc.type}</div>
                            <div class="location-details">
                                ${loc.visit_count} visits · Avg ${loc.average_duration_hours.toFixed(1)}h
                            </div>
                        </div>
                        <span class="location-confidence">${(loc.confidence * 100).toFixed(0)}%</span>
                    </li>
                `).join('');
                
            } catch (error) {
                console.error('Error loading recognized locations:', error);
                document.getElementById('recognized-locations').innerHTML = 
                    '<li class="loading">Error loading data</li>';
            }
        }
        
        async function loadPredictions() {
            try {
                const response = await fetch('/api/predictions');
                const data = await response.json();
                
                const list = document.getElementById('predictions');
                
                if (!data.predictions || data.predictions.length === 0) {
                    list.innerHTML = '<li class="loading">No predictions available yet.</li>';
                    return;
                }
                
                list.innerHTML = data.predictions.map(pred => {
                    const loc = pred.location;
                    const name = loc.name || loc.type || 'Unknown Location';
                    const reasons = pred.reasons ? pred.reasons.join(', ') : '';
                    
                    return `
                        <li class="location-item">
                            <div>
                                <div class="location-name">${name}</div>
                                <div class="location-details">${reasons}</div>
                            </div>
                            <span class="location-confidence">${(pred.confidence * 100).toFixed(0)}%</span>
                        </li>
                    `;
                }).join('');
                
            } catch (error) {
                console.error('Error loading predictions:', error);
                document.getElementById('predictions').innerHTML = 
                    '<li class="loading">Error loading predictions</li>';
            }
        }
        
        // Load data on page load
        loadStatus();
        loadRecognizedLocations();
        loadPredictions();
        
        // Refresh every 30 seconds
        setInterval(() => {
            loadStatus();
            loadRecognizedLocations();
            loadPredictions();
        }, 30000);
    </script>
</body>
</html>''')
    
    # Create profile.html
    with open('templates/profile.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile - Vehicle Tracking System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 24px; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .nav {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
            font-weight: 500;
        }
        .section {
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .info-row {
            display: grid;
            grid-template-columns: 150px 1fr;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .info-row:last-child { border-bottom: none; }
        .info-label {
            font-weight: 500;
            color: #666;
        }
        .info-value {
            color: #333;
        }
        pre {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>👤 User Profile</h1>
    </div>
    
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/map">Map View</a>
            <a href="/logs">Logs</a>
        </div>
        
        <div class="section">
            <h2>Personal Information</h2>
            <div id="basic-info">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Known Locations</h2>
            <div id="known-locations">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Schedule Patterns</h2>
            <div id="schedule">Loading...</div>
        </div>
        
        <div class="section">
            <h2>Raw Profile Data (JSON)</h2>
            <pre id="raw-data">Loading...</pre>
        </div>
    </div>
    
    <script>
        async function loadProfile() {
            try {
                const response = await fetch('/api/profile');
                const data = await response.json();
                
                // Basic info
                const basicInfo = data.basic_info || {};
                document.getElementById('basic-info').innerHTML = Object.entries(basicInfo)
                    .filter(([key, value]) => value)
                    .map(([key, value]) => `
                        <div class="info-row">
                            <div class="info-label">${key.replace(/_/g, ' ').toUpperCase()}</div>
                            <div class="info-value">${value}</div>
                        </div>
                    `).join('') || '<p>No profile information available</p>';
                
                // Known locations
                const knownLocs = data.known_locations || [];
                document.getElementById('known-locations').innerHTML = knownLocs.length > 0 ?
                    knownLocs.map(loc => `
                        <div class="info-row">
                            <div class="info-label">${loc.name || 'Unknown'}</div>
                            <div class="info-value">
                                ${loc.address || ''} 
                                ${loc.category ? `(${loc.category})` : ''}
                            </div>
                        </div>
                    `).join('') : '<p>No known locations configured</p>';
                
                // Schedule
                const schedule = data.schedule_patterns || {};
                document.getElementById('schedule').innerHTML = Object.entries(schedule)
                    .filter(([key, value]) => value)
                    .map(([key, value]) => `
                        <div class="info-row">
                            <div class="info-label">${key.replace(/_/g, ' ').toUpperCase()}</div>
                            <div class="info-value">${value}</div>
                        </div>
                    `).join('') || '<p>No schedule patterns configured</p>';
                
                // Raw data
                document.getElementById('raw-data').textContent = JSON.stringify(data, null, 2);
                
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }
        
        loadProfile();
    </script>
</body>
</html>''')
    
    # Create map.html and logs.html placeholders
    with open('templates/map.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Map View - Vehicle Tracking</title>
    <style>
        body { margin: 0; font-family: Arial, sans-serif; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }
        .container { padding: 20px; }
        .nav { background: white; padding: 15px; }
        .nav a { color: #667eea; text-decoration: none; margin-right: 20px; }
    </style>
</head>
<body>
    <div class="header"><h1>🗺️ Map View</h1></div>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/map">Map View</a>
            <a href="/logs">Logs</a>
        </div>
        <p>Map visualization coming soon. Install leaflet.js or similar for interactive maps.</p>
    </div>
</body>
</html>''')
    
    with open('templates/logs.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Logs - Vehicle Tracking</title>
    <style>
        body { margin: 0; font-family: Arial, sans-serif; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }
        .container { padding: 20px; }
        .nav { background: white; padding: 15px; margin-bottom: 20px; }
        .nav a { color: #667eea; text-decoration: none; margin-right: 20px; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header"><h1>📋 System Logs</h1></div>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/map">Map View</a>
            <a href="/logs">Logs</a>
        </div>
        <h3>Recent GPS Logs</h3>
        <pre id="logs">Loading...</pre>
    </div>
    <script>
        async function loadLogs() {
            try {
                const response = await fetch('/api/locations?days=1');
                const data = await response.json();
                document.getElementById('logs').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('logs').textContent = 'Error loading logs: ' + error;
            }
        }
        loadLogs();
    </script>
</body>
</html>''')


def start_server(host='0.0.0.0', port=80):
    """Start the web server"""
    create_templates()
    logger.info(f"Starting web server on {host}:{port}")
    logger.info(f"Access dashboard at: http://localhost:{port}")
    
    try:
        app.run(host=host, port=port, debug=False)
    except PermissionError:
        logger.error(f"Permission denied to bind to port {port}. Try running with sudo or use port 8080.")
        logger.info("Trying port 8080 instead...")
        app.run(host=host, port=8080, debug=False)


if __name__ == '__main__':
    import sys
    
    # Check for port argument
    port = 80
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number")
            sys.exit(1)
    
    start_server(port=port)
