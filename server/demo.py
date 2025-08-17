#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for Ukraine Alerts Map Enhanced Python Backend
Demonstrates all features of the enhanced alert system.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Add colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.ENDC, bold: bool = False):
    """Print colored text to terminal"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.ENDC}")
    else:
        print(f"{color}{text}{Colors.ENDC}")

def print_section(title: str):
    """Print a section header"""
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  {title}", Colors.CYAN, bold=True)
    print_colored("=" * 60, Colors.CYAN)
    print()

def demo_alert_levels():
    """Demonstrate alert level system"""
    print_section("ALERT LEVEL SYSTEM")

    levels = [
        ("🟢 NONE", "No active threats", Colors.GREEN),
        ("🟡 LOW", "Minor threat activity", Colors.YELLOW),
        ("🟠 MEDIUM", "Moderate threat level", Colors.YELLOW),
        ("🔴 HIGH", "Significant threat level", Colors.RED),
        ("⚫ CRITICAL", "Maximum threat level", Colors.RED)
    ]

    for icon_level, description, color in levels:
        print_colored(f"  {icon_level}: {description}", color)

def demo_threat_types():
    """Demonstrate threat type system"""
    print_section("THREAT TYPE SYSTEM")

    threats = [
        ("✈️  Air Raid", "air_raid", "Active air raid alert", 10),
        ("🛩️  Tactical Aviation", "tactical_aviation", "Enemy aircraft activity", 8),
        ("🚀 Cruise Missiles", "cruise_missiles", "Cruise missile threat", 9),
        ("🎯 Ballistic Missiles", "ballistic_missiles", "Ballistic missile threat", 10),
        ("🛸 Drones/UAVs", "drones", "Unmanned aerial vehicles", 6),
        ("💥 Artillery", "artillery", "Artillery shelling threat", 7),
        ("🛡️  Street Fighting", "street_fighting", "Urban combat operations", 5)
    ]

    print_colored("  Icon  Type                  ID                      Priority", Colors.BLUE, bold=True)
    print_colored("  " + "-" * 56, Colors.BLUE)

    for icon_name, threat_id, description, priority in threats:
        priority_color = Colors.RED if priority >= 9 else Colors.YELLOW if priority >= 7 else Colors.GREEN
        print(f"  {icon_name:<20} {threat_id:<22} ", end="")
        print_colored(f"[{priority:2}]", priority_color)
        print(f"    {description}")

def demo_active_alerts():
    """Show current active alerts from enhanced data"""
    print_section("ACTIVE ALERTS (from enhanced_alerts.json)")

    data_file = Path(__file__).parent.parent / 'src' / 'data' / 'enhanced_alerts.json'

    if not data_file.exists():
        print_colored("  ⚠️  No enhanced alerts file found. Run generate_enhanced_alerts.py first.", Colors.YELLOW)
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        alerts = json.load(f)

    active_alerts = [(name, data) for name, data in alerts.items() if data.get('is_active', False)]

    if not active_alerts:
        print_colored("  ✓ All regions clear - no active alerts", Colors.GREEN)
        return

    # Sort by intensity
    active_alerts.sort(key=lambda x: x[1].get('intensity', 0), reverse=True)

    print_colored(f"  Found {len(active_alerts)} active alerts:", Colors.YELLOW, bold=True)
    print()

    for region_name, alert in active_alerts[:6]:  # Show top 6
        duration = alert.get('duration', {})
        intensity = alert.get('intensity', 0)
        threats = alert.get('threat_types', [])

        # Color based on intensity
        if intensity >= 80:
            color = Colors.RED
            symbol = "🔴"
        elif intensity >= 60:
            color = Colors.YELLOW
            symbol = "🟠"
        else:
            color = Colors.GREEN
            symbol = "🟡"

        print(f"  {symbol} ", end="")
        print_colored(f"{region_name:<30}", color, bold=True)
        print(f"     Duration: {duration.get('days', 0):4}d {duration.get('hours', 0):2}h")
        print(f"     Intensity: {intensity:3}%")
        print(f"     Threats: {', '.join(threats)}")
        print()

def demo_statistics():
    """Show alert statistics"""
    print_section("ALERT STATISTICS")

    stats_file = Path(__file__).parent.parent / 'src' / 'data' / 'alert_statistics.json'

    if not stats_file.exists():
        print_colored("  ⚠️  No statistics file found. Run generate_enhanced_alerts.py first.", Colors.YELLOW)
        return

    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    print_colored("  Overall Status:", Colors.BLUE, bold=True)
    print(f"    • Total regions monitored: {stats['total_regions']}")
    print(f"    • Regions under alert: {stats['active_alerts']}")
    print(f"    • Clear regions: {stats['clear_regions']}")

    if stats.get('threat_type_counts'):
        print()
        print_colored("  Threat Distribution:", Colors.BLUE, bold=True)
        for threat, count in sorted(stats['threat_type_counts'].items(),
                                   key=lambda x: x[1], reverse=True):
            bar = "█" * (count * 5)
            print(f"    • {threat:<20} {bar} ({count})")

    if stats.get('longest_alert'):
        print()
        print_colored("  Notable Alerts:", Colors.BLUE, bold=True)
        longest = stats['longest_alert']
        print(f"    • Longest running: {longest['region']} ({longest['total_hours']:,} hours)")

    if stats.get('highest_intensity'):
        highest = stats['highest_intensity']
        print(f"    • Highest intensity: {highest['region']} ({highest['intensity']}%)")

def demo_data_pipeline():
    """Explain the data pipeline"""
    print_section("DATA PIPELINE WORKFLOW")

    steps = [
        ("1️⃣  Download Regions", "python download_regions.py",
         "Fetches GeoJSON boundaries from OpenStreetMap"),
        ("2️⃣  Fetch Alerts", "python download_regions.py --skip-regions",
         "Gets real-time alert data from APIs"),
        ("3️⃣  Generate Enhanced", "python generate_enhanced_alerts.py",
         "Creates rich alert data with threat analysis"),
        ("4️⃣  Run Tests", "python test_enhanced_alerts.py",
         "Validates all data processing functions"),
        ("5️⃣  Integration", "npm start (in parent directory)",
         "React app uses the generated JSON files")
    ]

    for step, command, description in steps:
        print_colored(f"  {step}", Colors.GREEN, bold=True)
        print(f"    Command: {command}")
        print(f"    Purpose: {description}")
        print()

def demo_region_examples():
    """Show example region data structures"""
    print_section("EXAMPLE DATA STRUCTURES")

    print_colored("  Basic Alert (from alerts.json):", Colors.BLUE, bold=True)
    basic_example = {
        "enabled": True,
        "enabled_at": "2022-04-04T16:45:39+00:00",
        "disabled_at": None
    }
    print(json.dumps(basic_example, indent=4))

    print()
    print_colored("  Enhanced Alert (from enhanced_alerts.json):", Colors.BLUE, bold=True)
    enhanced_example = {
        "region_id": "zaporizhia_oblast",
        "region_name": "Запорізька область",
        "region_name_en": "Zaporizhia",
        "alert_level": "high",
        "threat_types": ["air_raid", "drones"],
        "duration": {"days": 0, "hours": 31, "minutes": 0},
        "intensity": 65,
        "is_active": True,
        "color": "#ff8866"
    }
    print(json.dumps(enhanced_example, indent=4))

def demo_usage_examples():
    """Show common usage examples"""
    print_section("COMMON USAGE EXAMPLES")

    examples = [
        ("Download everything fresh",
         "python download_regions.py"),

        ("Update alerts only (fast)",
         "python download_regions.py --skip-regions --skip-world"),

        ("Generate mock data for testing",
         "python generate_enhanced_alerts.py"),

        ("Download specific regions",
         'python download_regions.py --regions "м. Київ" "Одеська область"'),

        ("List all available regions",
         "python download_regions.py --list-regions"),

        ("Run test suite",
         "python test_enhanced_alerts.py -v"),

        ("Check current alerts",
         "python demo.py")
    ]

    for description, command in examples:
        print_colored(f"  {description}:", Colors.GREEN)
        print(f"    $ {command}")
        print()

def main():
    """Run the demo"""
    print_colored("\n╔════════════════════════════════════════════════════════════╗", Colors.CYAN, bold=True)
    print_colored("║     UKRAINE ALERTS MAP - ENHANCED PYTHON BACKEND DEMO     ║", Colors.CYAN, bold=True)
    print_colored("╚════════════════════════════════════════════════════════════╝", Colors.CYAN, bold=True)

    # Run all demos
    demo_alert_levels()
    demo_threat_types()
    demo_active_alerts()
    demo_statistics()
    demo_data_pipeline()
    demo_region_examples()
    demo_usage_examples()

    # Final message
    print_section("NEXT STEPS")
    print_colored("  To get started:", Colors.GREEN, bold=True)
    print("  1. Run: python generate_enhanced_alerts.py")
    print("  2. Check: ../src/data/enhanced_alerts.json")
    print("  3. Start React app: cd .. && npm start")
    print()
    print_colored("  For help:", Colors.BLUE, bold=True)
    print("  • Run any script with --help flag")
    print("  • Check server/README.md for documentation")
    print("  • Run tests: python test_enhanced_alerts.py")
    print()
    print_colored("  ✨ Happy coding! ✨", Colors.CYAN, bold=True)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", Colors.RED)
        sys.exit(1)
