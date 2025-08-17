#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for enhanced alerts functionality.
Tests data generation, API integration, and data validation.
"""

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_enhanced_alerts import (
    generate_enhanced_alert,
    calculate_start_time,
    determine_alert_level,
    generate_statistics,
    REGION_ALERT_CONFIG,
    THREAT_METADATA
)

class TestEnhancedAlerts(unittest.TestCase):
    """Test cases for enhanced alerts functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_region = "Тестова область"
        self.test_config_active = {
            'enabled': True,
            'threat_types': ['air_raid', 'drones'],
            'duration_days': 2,
            'duration_hours': 15,
            'intensity': 75,
            'color': '#ff6b6b'
        }
        self.test_config_inactive = {
            'enabled': False
        }

    def test_calculate_start_time(self):
        """Test start time calculation"""
        # Test with days and hours
        start_time = calculate_start_time(days=5, hours=10)
        start_dt = datetime.fromisoformat(start_time)
        expected = datetime.now(timezone.utc) - timedelta(days=5, hours=10)

        # Allow for small time differences due to execution time
        time_diff = abs((start_dt - expected).total_seconds())
        self.assertLess(time_diff, 1, "Start time calculation should be accurate within 1 second")

    def test_determine_alert_level(self):
        """Test alert level determination"""
        # Test critical level (not in our current threats, but for completeness)
        self.assertEqual(
            determine_alert_level(['ballistic_missiles'], 90),
            'critical'
        )

        # Test high level
        self.assertEqual(
            determine_alert_level(['air_raid'], 80),
            'high'
        )

        # Test medium level
        self.assertEqual(
            determine_alert_level(['artillery', 'drones'], 60),
            'medium'
        )

        # Test low level
        self.assertEqual(
            determine_alert_level(['unknown_threat'], 30),
            'low'
        )

        # Test none level
        self.assertEqual(
            determine_alert_level([], 0),
            'none'
        )

    def test_generate_enhanced_alert_active(self):
        """Test generation of active alert"""
        alert = generate_enhanced_alert(self.test_region, self.test_config_active)

        # Check basic fields
        self.assertEqual(alert['region_name'], self.test_region)
        self.assertTrue(alert['is_active'])
        self.assertEqual(alert['alert_level'], 'high')

        # Check threat types
        self.assertEqual(alert['threat_types'], ['air_raid', 'drones'])

        # Check duration
        self.assertEqual(alert['duration']['days'], 2)
        self.assertEqual(alert['duration']['hours'], 15)

        # Check intensity and color
        self.assertEqual(alert['intensity'], 75)
        self.assertEqual(alert['color'], '#ff6b6b')

        # Check threat metadata exists
        self.assertIn('threat_metadata', alert)
        self.assertIn('air_raid', alert['threat_metadata'])

    def test_generate_enhanced_alert_inactive(self):
        """Test generation of inactive alert"""
        alert = generate_enhanced_alert(self.test_region, self.test_config_inactive)

        # Check basic fields
        self.assertEqual(alert['region_name'], self.test_region)
        self.assertFalse(alert['is_active'])
        self.assertEqual(alert['alert_level'], 'none')

        # Check empty fields
        self.assertEqual(alert['threat_types'], [])
        self.assertIsNone(alert['start_time'])
        self.assertIsNone(alert['end_time'])

        # Check default values
        self.assertEqual(alert['intensity'], 0)
        self.assertEqual(alert['color'], '#ffffff')

        # Check duration is zero
        self.assertEqual(alert['duration']['days'], 0)
        self.assertEqual(alert['duration']['hours'], 0)
        self.assertEqual(alert['duration']['minutes'], 0)

    def test_region_id_generation(self):
        """Test region ID generation from names"""
        test_cases = [
            ("Київська область", "київська_область"),
            ("м. Київ", "м_київ"),
            ("Автономна Республіка Крим", "автономна_республіка_крим")
        ]

        for region_name, expected_id in test_cases:
            config = {'enabled': False}
            alert = generate_enhanced_alert(region_name, config)
            self.assertEqual(alert['region_id'], expected_id)

    def test_generate_statistics(self):
        """Test statistics generation"""
        # Generate test alerts
        alerts = {}
        for region_name, config in list(REGION_ALERT_CONFIG.items())[:5]:
            alerts[region_name] = generate_enhanced_alert(region_name, config)

        stats = generate_statistics(alerts)

        # Check basic counts
        self.assertEqual(stats['total_regions'], 5)
        self.assertIsInstance(stats['active_alerts'], int)
        self.assertIsInstance(stats['clear_regions'], int)
        self.assertEqual(stats['active_alerts'] + stats['clear_regions'], 5)

        # Check threat counts if there are active alerts
        if stats['active_alerts'] > 0:
            self.assertIsInstance(stats['threat_type_counts'], dict)
            self.assertGreater(len(stats['threat_type_counts']), 0)

            # Check longest alert
            self.assertIsNotNone(stats['longest_alert'])
            self.assertIn('region', stats['longest_alert'])
            self.assertIn('duration', stats['longest_alert'])
            self.assertIn('total_hours', stats['longest_alert'])

            # Check highest intensity
            self.assertIsNotNone(stats['highest_intensity'])
            self.assertIn('region', stats['highest_intensity'])
            self.assertIn('intensity', stats['highest_intensity'])
            self.assertIn('threats', stats['highest_intensity'])

    def test_threat_metadata_completeness(self):
        """Test that all threat types have metadata"""
        required_fields = ['label', 'label_en', 'icon', 'priority', 'color']

        for threat_type, metadata in THREAT_METADATA.items():
            for field in required_fields:
                self.assertIn(
                    field,
                    metadata,
                    f"Threat type '{threat_type}' missing required field '{field}'"
                )

            # Check priority is a number
            self.assertIsInstance(metadata['priority'], int)
            self.assertGreaterEqual(metadata['priority'], 0)
            self.assertLessEqual(metadata['priority'], 10)

            # Check color is a hex color
            self.assertTrue(
                metadata['color'].startswith('#'),
                f"Color for '{threat_type}' should be hex format"
            )

    def test_real_region_configs(self):
        """Test actual region configurations from the mockup"""
        # Test Luhansk (longest duration)
        luhansk_config = REGION_ALERT_CONFIG.get('Луганська область')
        self.assertIsNotNone(luhansk_config)
        self.assertTrue(luhansk_config['enabled'])
        self.assertEqual(luhansk_config['duration_days'], 1220)
        self.assertEqual(luhansk_config['duration_hours'], 17)
        self.assertIn('air_raid', luhansk_config['threat_types'])

        # Test Donetsk
        donetsk_config = REGION_ALERT_CONFIG.get('Донецька область')
        self.assertIsNotNone(donetsk_config)
        self.assertTrue(donetsk_config['enabled'])
        self.assertIn('tactical_aviation', donetsk_config['threat_types'])

        # Test a clear region
        kyiv_config = REGION_ALERT_CONFIG.get('м. Київ')
        self.assertIsNotNone(kyiv_config)
        self.assertFalse(kyiv_config['enabled'])

    def test_data_file_generation(self):
        """Test that data files can be generated and are valid JSON"""
        output_dir = Path(__file__).parent.parent / 'src' / 'data'

        # Check if enhanced_alerts.json exists and is valid
        enhanced_file = output_dir / 'enhanced_alerts.json'
        if enhanced_file.exists():
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)
                    self.assertGreater(len(data), 0)

                    # Check structure of first alert
                    first_alert = next(iter(data.values()))
                    required_fields = [
                        'region_id', 'region_name', 'alert_level',
                        'threat_types', 'is_active', 'intensity'
                    ]
                    for field in required_fields:
                        self.assertIn(field, first_alert)

                except json.JSONDecodeError:
                    self.fail("enhanced_alerts.json is not valid JSON")

        # Check if alert_statistics.json exists and is valid
        stats_file = output_dir / 'alert_statistics.json'
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                try:
                    stats = json.load(f)
                    self.assertIsInstance(stats, dict)
                    self.assertIn('total_regions', stats)
                    self.assertIn('active_alerts', stats)
                    self.assertIn('threat_type_counts', stats)
                except json.JSONDecodeError:
                    self.fail("alert_statistics.json is not valid JSON")

    def test_duration_calculation_accuracy(self):
        """Test that duration calculations are accurate"""
        test_cases = [
            (1220, 17, 0),  # Luhansk
            (990, 11, 0),   # Crimea
            (3, 49, 0),     # Donetsk
            (0, 31, 0),     # Zaporizhia
        ]

        for days, hours, minutes in test_cases:
            start_time = calculate_start_time(days, hours, minutes)
            start_dt = datetime.fromisoformat(start_time)
            now = datetime.now(timezone.utc)

            actual_delta = now - start_dt
            expected_delta = timedelta(days=days, hours=hours, minutes=minutes)

            # Allow for small differences (up to 1 second)
            diff_seconds = abs((actual_delta - expected_delta).total_seconds())
            self.assertLess(
                diff_seconds, 1,
                f"Duration {days}d {hours}h {minutes}m calculation off by {diff_seconds} seconds"
            )

def run_tests(verbose=False):
    """Run all tests and print results"""
    print("Running Enhanced Alerts Tests...")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedAlerts)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        return 1

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test enhanced alerts functionality')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    sys.exit(run_tests(verbose=args.verbose))
