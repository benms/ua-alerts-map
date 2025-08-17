#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for Ukraine Alerts Map Python Backend.
Checks that all components are installed and working correctly.
"""

import sys
import os
import json
import importlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.ENDC, bold=False):
    """Print colored text"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.ENDC}")
    else:
        print(f"{color}{text}{Colors.ENDC}")

def print_header(title):
    """Print section header"""
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  {title}", Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN)
    print()

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_colored(f"  ✅ Python {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
        return True
    else:
        print_colored(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (3.8+ required)", Colors.RED)
        return False

def check_script_exists(script_name):
    """Check if a script exists"""
    script_path = Path(__file__).parent / script_name
    if script_path.exists():
        print_colored(f"  ✅ {script_name}", Colors.GREEN)
        return True
    else:
        print_colored(f"  ❌ {script_name} not found", Colors.RED)
        return False

def check_optional_dependencies():
    """Check optional dependencies"""
    dependencies = {
        'requests': 'For enhanced downloader',
        'pytest': 'For running test suite',
        'rich': 'For rich terminal output',
        'click': 'For CLI enhancements'
    }

    results = {}
    for module, description in dependencies.items():
        try:
            importlib.import_module(module)
            print_colored(f"  ✅ {module} - {description}", Colors.GREEN)
            results[module] = True
        except ImportError:
            print_colored(f"  ⚠️  {module} - {description} (optional)", Colors.YELLOW)
            results[module] = False

    return results

def test_import_scripts():
    """Test importing main scripts"""
    scripts_to_test = [
        ('generate_enhanced_alerts', 'AlertData generation'),
        ('download_enhanced_alerts_standalone', 'Standalone downloader'),
        ('test_enhanced_alerts', 'Test suite')
    ]

    success = True
    for module_name, description in scripts_to_test:
        try:
            # Add current directory to path
            sys.path.insert(0, str(Path(__file__).parent))
            module = importlib.import_module(module_name)
            print_colored(f"  ✅ {module_name} - {description}", Colors.GREEN)
        except ImportError as e:
            print_colored(f"  ❌ {module_name} - {e}", Colors.RED)
            success = False
        except Exception as e:
            print_colored(f"  ⚠️  {module_name} - {e}", Colors.YELLOW)

    return success

def check_data_directories():
    """Check if data directories exist"""
    base_dir = Path(__file__).parent.parent / 'src' / 'data'
    directories = {
        base_dir: 'Main data directory',
        base_dir / 'regions': 'Regions directory'
    }

    all_exist = True
    for dir_path, description in directories.items():
        if dir_path.exists():
            print_colored(f"  ✅ {description}: {dir_path.relative_to(Path(__file__).parent.parent)}", Colors.GREEN)
        else:
            print_colored(f"  ⚠️  {description} not found (will be created)", Colors.YELLOW)
            # Try to create it
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_colored(f"      Created: {dir_path}", Colors.GREEN)
            except Exception as e:
                print_colored(f"      Failed to create: {e}", Colors.RED)
                all_exist = False

    return all_exist

def test_basic_functionality():
    """Test basic functionality"""
    try:
        # Test datetime handling
        now = datetime.now(timezone.utc)
        iso_string = now.isoformat()
        parsed = datetime.fromisoformat(iso_string)
        print_colored(f"  ✅ Timezone-aware datetime handling", Colors.GREEN)

        # Test JSON handling
        test_data = {
            "region": "Test",
            "alert": True,
            "timestamp": iso_string
        }
        json_string = json.dumps(test_data)
        parsed_data = json.loads(json_string)
        print_colored(f"  ✅ JSON serialization/deserialization", Colors.GREEN)

        # Test Path operations
        test_path = Path(__file__).parent / "test_file.tmp"
        test_path.write_text("test")
        test_path.unlink()
        print_colored(f"  ✅ File I/O operations", Colors.GREEN)

        return True
    except Exception as e:
        print_colored(f"  ❌ Basic functionality test failed: {e}", Colors.RED)
        return False

def run_sample_generation():
    """Try to run sample data generation"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from generate_enhanced_alerts import generate_enhanced_alert, REGION_ALERT_CONFIG

        # Test with a sample region
        test_config = {
            'enabled': True,
            'threat_types': ['air_raid', 'drones'],
            'duration_days': 1,
            'duration_hours': 5,
            'intensity': 75,
            'color': '#ff6b6b'
        }

        alert = generate_enhanced_alert("Test Region", test_config)

        if alert and alert['is_active'] and alert['intensity'] == 75:
            print_colored(f"  ✅ Alert generation working", Colors.GREEN)
            print(f"     Generated alert with {len(alert['threat_types'])} threats, "
                  f"intensity {alert['intensity']}%")
            return True
        else:
            print_colored(f"  ❌ Alert generation produced unexpected results", Colors.RED)
            return False

    except Exception as e:
        print_colored(f"  ⚠️  Could not test alert generation: {e}", Colors.YELLOW)
        return False

def check_output_files():
    """Check for generated output files"""
    data_dir = Path(__file__).parent.parent / 'src' / 'data'
    files = {
        'enhanced_alerts.json': 'Enhanced alerts data',
        'alert_statistics.json': 'Alert statistics',
        'alerts.json': 'Basic alerts data'
    }

    found_any = False
    for filename, description in files.items():
        file_path = data_dir / filename
        if file_path.exists():
            print_colored(f"  ✅ {filename} - {description}", Colors.GREEN)
            # Check if it's valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"     Contains {len(data)} entries")
                    found_any = True
            except Exception as e:
                print_colored(f"     ⚠️  Invalid JSON: {e}", Colors.YELLOW)
        else:
            print_colored(f"  ⚠️  {filename} not found (run generators to create)", Colors.YELLOW)

    return found_any

def main():
    """Run all verification checks"""
    print_colored("\n╔════════════════════════════════════════════════════════════╗", Colors.CYAN, bold=True)
    print_colored("║    UKRAINE ALERTS MAP - BACKEND VERIFICATION SCRIPT       ║", Colors.CYAN, bold=True)
    print_colored("╚════════════════════════════════════════════════════════════╝", Colors.CYAN, bold=True)

    all_checks_passed = True

    # Check Python version
    print_header("Python Version Check")
    if not check_python_version():
        all_checks_passed = False

    # Check core scripts exist
    print_header("Core Scripts Check")
    scripts = [
        'download_regions.py',
        'generate_enhanced_alerts.py',
        'download_enhanced_alerts.py',
        'download_enhanced_alerts_standalone.py',
        'test_enhanced_alerts.py',
        'demo.py'
    ]

    for script in scripts:
        if not check_script_exists(script):
            all_checks_passed = False

    # Check optional dependencies
    print_header("Optional Dependencies")
    deps = check_optional_dependencies()

    # Test imports
    print_header("Import Tests")
    if not test_import_scripts():
        all_checks_passed = False

    # Check directories
    print_header("Directory Structure")
    if not check_data_directories():
        all_checks_passed = False

    # Test basic functionality
    print_header("Basic Functionality Tests")
    if not test_basic_functionality():
        all_checks_passed = False

    # Test alert generation
    print_header("Alert Generation Test")
    run_sample_generation()

    # Check output files
    print_header("Output Files Check")
    check_output_files()

    # Final summary
    print_header("VERIFICATION SUMMARY")

    if all_checks_passed:
        print_colored("  ✅ All core checks passed!", Colors.GREEN, bold=True)
        print()
        print_colored("  Next steps:", Colors.BLUE, bold=True)
        print("  1. Run: python generate_enhanced_alerts.py")
        print("  2. Run: python demo.py")
        print("  3. Check generated files in ../src/data/")
    else:
        print_colored("  ⚠️  Some checks failed or need attention", Colors.YELLOW, bold=True)
        print()
        print_colored("  Recommendations:", Colors.BLUE, bold=True)

        if not deps.get('requests'):
            print("  • Install requests: pip install requests")
            print("    OR use download_enhanced_alerts_standalone.py")

        print("  • Run: python generate_enhanced_alerts.py to create sample data")
        print("  • Check README.md for troubleshooting tips")

    print()
    print_colored("  For detailed help, see server/README.md", Colors.CYAN)
    print()

    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    sys.exit(main())
