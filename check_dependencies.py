#!/usr/bin/env python3
"""
Dependency checker for Vehicle Tracking System
Run this to verify all required dependencies are installed
"""

import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("✗ Python version: {}.{} (requires 3.7+)".format(
            sys.version_info.major, sys.version_info.minor))
        return False
    else:
        print("✓ Python version: {}.{}".format(
            sys.version_info.major, sys.version_info.minor))
        return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = [
        ('flask', 'Flask web framework'),
        ('googlemaps', 'Google Maps API client'),
        ('numpy', 'NumPy for numerical computing'),
        ('pandas', 'Pandas for data analysis'),
        ('sklearn', 'Scikit-learn for machine learning'),
        ('geopy', 'Geopy for geocoding'),
        ('requests', 'Requests for HTTP'),
    ]
    
    all_ok = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module:15s} - {description}")
        except ImportError:
            print(f"✗ {module:15s} - {description} (NOT INSTALLED)")
            all_ok = False
    
    return all_ok

def check_custom_modules():
    """Check if custom modules can be imported"""
    modules = [
        'gps_tracker',
        'ai_processor', 
        'profile_manager',
        'network_manager',
        'advanced_prediction',
        'web_server'
    ]
    
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module} - {e}")
            all_ok = False
    
    return all_ok

def main():
    """Main entry point"""
    print("=" * 80)
    print("VEHICLE TRACKING SYSTEM - DEPENDENCY CHECK")
    print("=" * 80)
    print()
    
    # Check Python version
    print("Checking Python version...")
    py_ok = check_python_version()
    print()
    
    if not py_ok:
        print("ERROR: Python 3.7 or higher is required")
        print("Please upgrade Python before continuing.")
        sys.exit(1)
    
    # Check dependencies
    print("Checking required dependencies...")
    deps_ok = check_dependencies()
    print()
    
    if not deps_ok:
        print("ERROR: Some dependencies are missing")
        print()
        print("To install all dependencies, run:")
        print("  pip3 install -r requirements.txt")
        print()
        print("Or install individually:")
        print("  pip3 install flask googlemaps numpy pandas scikit-learn geopy requests")
        print()
        sys.exit(1)
    
    # Check custom modules
    print("Checking custom modules...")
    modules_ok = check_custom_modules()
    print()
    
    if not modules_ok:
        print("WARNING: Some custom modules failed to import")
        print("This may be due to missing optional dependencies")
        print()
    
    # Summary
    print("=" * 80)
    if py_ok and deps_ok and modules_ok:
        print("✓ ALL CHECKS PASSED - System is ready to use!")
    elif py_ok and deps_ok:
        print("⚠ DEPENDENCIES OK - Some warnings, but system should work")
    else:
        print("✗ CHECKS FAILED - Please install missing dependencies")
    print("=" * 80)
    print()

if __name__ == '__main__':
    main()
