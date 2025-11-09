#!/usr/bin/env python3
"""
Main Application - Vehicle Tracking System with AI Processing
Runs on Raspberry Pi 4B to track vehicle paths and predict destinations
Works offline - queues operations when WiFi unavailable
"""

import sys
import time
import os
import signal
from datetime import datetime
import logging

from gps_tracker import GPSTracker
from ai_processor import AIProcessor
from profile_manager import ProfileManager
from network_manager import NetworkManager


class VehicleTrackingSystem:
    """Main system coordinator"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.logger = self._setup_logger()
        self.running = False
        
        # Initialize components
        self.gps_tracker = GPSTracker(config_path)
        self.ai_processor = AIProcessor(config_path)
        self.profile_manager = ProfileManager(config_path)
        self.network_manager = NetworkManager()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('VehicleTrackingSystem')
        logger.setLevel(logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/main_system.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start the tracking system"""
        self.logger.info("=" * 80)
        self.logger.info("VEHICLE TRACKING SYSTEM WITH AI PROCESSING")
        self.logger.info("=" * 80)
        self.logger.info("Optimized for Raspberry Pi 4B")
        self.logger.info("Offline-capable with WiFi queue management")
        self.logger.info("")
        
        # Check network status
        is_online = self.network_manager.check_connectivity()
        status = "Online ✓" if is_online else "Offline (will queue operations)"
        self.logger.info(f"Network Status: {status}")
        
        # Check if queue has pending operations
        queue_size = self.network_manager.get_queue_size()
        if queue_size > 0:
            self.logger.info(f"Found {queue_size} queued operations from previous session")
        
        self.logger.info("")
        self.logger.info("Starting main tracking loop...")
        self.logger.info("-" * 80)
        
        self.running = True
        
        # Get configuration
        config = self._load_config()
        gps_interval = config.get('system_settings', {}).get('gps_update_interval', 10)
        ai_interval = config.get('system_settings', {}).get('ai_prediction_interval', 5) * 60
        
        last_ai_analysis = datetime.now()
        last_profile_update = datetime.now()
        
        try:
            while self.running:
                # Get current location (works offline)
                location = self.gps_tracker.get_current_location()
                
                if location:
                    # Get context (cached if offline)
                    context = self.gps_tracker.analyze_current_context(location)
                    
                    # Log location
                    self.gps_tracker.log_location(location, context)
                    
                    # Check if time for AI analysis
                    time_since_ai = (datetime.now() - last_ai_analysis).total_seconds()
                    if time_since_ai >= ai_interval:
                        self.logger.info("Running AI prediction analysis...")
                        
                        # Make prediction
                        prediction = self.ai_processor.predict_destination(location, context)
                        
                        # Log prediction
                        if prediction and prediction.get('predictions'):
                            top_pred = prediction['predictions'][0]
                            confidence = top_pred.get('confidence', 0) * 100
                            loc_name = top_pred.get('location', {}).get('name', 'Unknown')
                            
                            self.logger.info(f"AI Prediction: {loc_name} (confidence: {confidence:.1f}%)")
                        
                        # Update profile
                        self.logger.info("Updating profile...")
                        self.profile_manager.create_profile(
                            predictions=prediction,
                            learned_patterns=self.ai_processor.learned_patterns
                        )
                        
                        last_ai_analysis = datetime.now()
                        last_profile_update = datetime.now()
                    
                    # Network status
                    is_online = self.network_manager.check_connectivity()
                    mode = "Online" if is_online else "Offline"
                    
                    self.logger.info(
                        f"[{mode}] Tracked: {location['latitude']:.6f}, {location['longitude']:.6f}"
                    )
                    
                    # Process queue if online
                    if is_online:
                        queue_size = self.network_manager.get_queue_size()
                        if queue_size > 0:
                            self.logger.info(f"Processing {queue_size} queued operations...")
                            self.gps_tracker.process_queued_operations()
                
                # Sleep
                time.sleep(gps_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the tracking system"""
        if not self.running:
            return
        
        self.running = False
        
        self.logger.info("")
        self.logger.info("-" * 80)
        self.logger.info("Shutting down system...")
        
        # Final AI learning from accumulated data
        try:
            self.logger.info("Running final AI learning analysis...")
            self.ai_processor.learn_from_data(days=30)
        except Exception as e:
            self.logger.error(f"Error in final learning: {e}")
        
        # Final profile update
        try:
            self.logger.info("Updating final profile...")
            self.profile_manager.create_profile(
                learned_patterns=self.ai_processor.learned_patterns
            )
        except Exception as e:
            self.logger.error(f"Error updating profile: {e}")
        
        # Process remaining queue if online
        if self.network_manager.check_connectivity():
            queue_size = self.network_manager.get_queue_size()
            if queue_size > 0:
                self.logger.info(f"Processing {queue_size} remaining queued operations...")
                try:
                    self.gps_tracker.process_queued_operations()
                except Exception as e:
                    self.logger.error(f"Error processing queue: {e}")
        else:
            queue_size = self.network_manager.get_queue_size()
            if queue_size > 0:
                self.logger.warning(f"{queue_size} operations remain queued (offline)")
        
        self.logger.info("System shutdown complete")
        self.logger.info("=" * 80)
    
    def _load_config(self):
        """Load configuration"""
        if os.path.exists(self.config_path):
            import json
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def run_learning_mode(self, days: int = 30):
        """
        Run learning mode to analyze historical data
        
        Args:
            days: Number of days to analyze
        """
        self.logger.info("=" * 80)
        self.logger.info("RUNNING AI LEARNING MODE")
        self.logger.info("=" * 80)
        
        self.ai_processor.learn_from_data(days)
        
        self.logger.info("Updating profile with learned patterns...")
        self.profile_manager.create_profile(
            learned_patterns=self.ai_processor.learned_patterns
        )
        
        self.logger.info("Learning mode complete")
        self.logger.info(f"Profile updated at: {self.profile_manager.get_profile_path()}")


def print_usage():
    """Print usage information"""
    print("""
Vehicle Tracking System with AI Processing
==========================================

Usage:
    python main.py [command]

Commands:
    start       - Start the tracking system (default)
    learn       - Run AI learning mode on historical data
    status      - Show system status
    web         - Start web server on localhost port 80
    help        - Show this help message

Examples:
    python main.py              # Start tracking
    python main.py start        # Start tracking
    python main.py learn        # Analyze historical data
    python main.py status       # Show system status
    python main.py web          # Start web interface
    python main.py web 8080     # Start web interface on port 8080
""")


def show_status():
    """Show system status"""
    print("\n" + "=" * 80)
    print("VEHICLE TRACKING SYSTEM STATUS")
    print("=" * 80)
    
    # Check if setup completed
    if not os.path.exists('config.json'):
        print("\n⚠ Setup not completed. Run 'python setup.py' first.\n")
        return
    
    print("\n✓ Setup completed")
    
    # Network status
    network_mgr = NetworkManager()
    is_online = network_mgr.check_connectivity()
    print(f"✓ Network: {'Online' if is_online else 'Offline'}")
    
    # Queue status
    queue_size = network_mgr.get_queue_size()
    if queue_size > 0:
        print(f"⚠ Queue: {queue_size} operations pending")
    else:
        print(f"✓ Queue: Empty")
    
    # Profile status
    profile_mgr = ProfileManager()
    if profile_mgr.profile_exists():
        print(f"✓ Profile: {profile_mgr.get_profile_path()}")
    else:
        print(f"⚠ Profile: Not yet created")
    
    # Data directory
    if os.path.exists('data'):
        import glob
        log_files = glob.glob('data/gps_log_*.json')
        print(f"✓ Data: {len(log_files)} log files")
    else:
        print(f"⚠ Data: No data collected yet")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point"""
    # Check if setup was completed
    if not os.path.exists('config.json'):
        print("\n⚠ Error: System not configured!")
        print("Please run the setup wizard first:")
        print("  python setup.py\n")
        sys.exit(1)
    
    # Parse command
    command = sys.argv[1] if len(sys.argv) > 1 else 'start'
    
    if command == 'help' or command == '--help' or command == '-h':
        print_usage()
        return
    
    if command == 'status':
        show_status()
        return
    
    if command == 'web':
        # Start web server
        from web_server import start_server
        port = 80
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print("Invalid port number")
                sys.exit(1)
        start_server(port=port)
        return
    
    # Initialize system
    system = VehicleTrackingSystem()
    
    if command == 'learn':
        system.run_learning_mode(days=30)
    elif command == 'start':
        system.start()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
