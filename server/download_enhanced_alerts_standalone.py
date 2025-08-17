#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone enhanced download script for Ukraine alerts.
Works without external dependencies using only Python standard library.
"""

import json
import time
import logging
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints
ALERTS_API = "https://vadimklimenko.com/map/statuses.json"
OSM_API = "https://polygons.openstreetmap.fr/get_geojson.py"
WORLD_MAP_API = "https://datahub.io/core/geo-countries/r/countries.geojson"

# Threat types enum
class ThreatType(Enum):
    AIR_RAID = "air_raid"
    TACTICAL_AVIATION = "tactical_aviation"
    CRUISE_MISSILES = "cruise_missiles"
    BALLISTIC_MISSILES = "ballistic_missiles"
    DRONES = "drones"
    ARTILLERY = "artillery"
    CHEMICAL = "chemical"
    NUCLEAR = "nuclear"
    STREET_FIGHTING = "street_fighting"

# Alert level enum
class AlertLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AlertData:
    """Enhanced alert data structure"""
    region_id: str
    region_name: str
    region_name_en: str
    alert_level: str
    threat_types: List[str]
    start_time: Optional[str]
    end_time: Optional[str]
    duration: Dict[str, int]
    intensity: int
    sub_regions: List[str]
    is_active: bool
    last_updated: str

    def calculate_duration(self) -> Dict[str, int]:
        """Calculate duration from start time"""
        if not self.start_time:
            return {"days": 0, "hours": 0, "minutes": 0}

        try:
            # Parse ISO format timestamp
            if 'T' in self.start_time:
                # Handle both with and without timezone
                if '+' in self.start_time or 'Z' in self.start_time:
                    start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
                else:
                    # Assume UTC if no timezone
                    start = datetime.fromisoformat(self.start_time).replace(tzinfo=timezone.utc)
            else:
                # Legacy format
                start = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

            # Calculate end time
            if self.end_time:
                if '+' in self.end_time or 'Z' in self.end_time:
                    end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
                else:
                    end = datetime.fromisoformat(self.end_time).replace(tzinfo=timezone.utc)
            else:
                end = datetime.now(timezone.utc)

            delta = end - start
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60

            self.duration = {"days": days, "hours": hours, "minutes": minutes}
        except Exception as e:
            logger.warning(f"Error calculating duration: {e}")
            self.duration = {"days": 0, "hours": 0, "minutes": 0}

        return self.duration

    def calculate_intensity(self) -> int:
        """Calculate intensity based on threat types and duration"""
        intensity = 0

        # Threat type priorities
        threat_priorities = {
            ThreatType.NUCLEAR.value: 10,
            ThreatType.BALLISTIC_MISSILES.value: 10,
            ThreatType.AIR_RAID.value: 10,
            ThreatType.CRUISE_MISSILES.value: 9,
            ThreatType.TACTICAL_AVIATION.value: 8,
            ThreatType.ARTILLERY.value: 7,
            ThreatType.DRONES.value: 6,
            ThreatType.STREET_FIGHTING.value: 5,
            ThreatType.CHEMICAL.value: 9
        }

        # Base intensity from threats
        for threat in self.threat_types:
            intensity += threat_priorities.get(threat, 5) * 10

        # Increase based on duration
        total_hours = self.duration.get("days", 0) * 24 + self.duration.get("hours", 0)
        if total_hours > 72:
            intensity += 20
        elif total_hours > 24:
            intensity += 10
        elif total_hours > 6:
            intensity += 5

        self.intensity = min(intensity, 100)
        return self.intensity

class StandaloneAlertsDownloader:
    """Standalone downloader using only standard library"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent / "src" / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_url(self, url: str, timeout: int = 30) -> Optional[str]:
        """Fetch URL content with error handling"""
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def download_mock_alerts(self) -> Dict[str, AlertData]:
        """Generate mock alert data matching the design"""
        logger.info("Generating mock alert data...")

        mock_configs = [
            {
                "id": "lugansk",
                "name": "Луганська",
                "name_en": "Luhansk",
                "alert": True,
                "threat_types": ["air_raid", "artillery", "street_fighting"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1220, hours=17)).isoformat(),
                "intensity": 95
            },
            {
                "id": "donetsk",
                "name": "Донецька",
                "name_en": "Donetsk",
                "alert": True,
                "threat_types": ["air_raid", "tactical_aviation", "artillery", "drones"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=3, hours=49)).isoformat(),
                "intensity": 85
            },
            {
                "id": "zaporizhia",
                "name": "Запорізька",
                "name_en": "Zaporizhia",
                "alert": True,
                "threat_types": ["air_raid", "drones"],
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=31)).isoformat(),
                "intensity": 65
            },
            {
                "id": "kherson",
                "name": "Херсонська",
                "name_en": "Kherson",
                "alert": True,
                "threat_types": ["artillery", "drones"],
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat(),
                "intensity": 60
            },
            {
                "id": "crimea",
                "name": "Автономна Республіка Крим",
                "name_en": "Autonomous Republic of Crimea",
                "alert": True,
                "threat_types": ["air_raid", "tactical_aviation"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=990, hours=11)).isoformat(),
                "intensity": 90
            },
            {
                "id": "dnipropetrovsk",
                "name": "Дніпропетровська",
                "name_en": "Dnipropetrovsk",
                "alert": True,
                "threat_types": ["air_raid"],
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=32)).isoformat(),
                "intensity": 50
            }
        ]

        alerts = {}
        for region in mock_configs:
            alert = AlertData(
                region_id=region["id"],
                region_name=region["name"],
                region_name_en=region["name_en"],
                alert_level=self._determine_alert_level(region.get("threat_types", [])),
                threat_types=region.get("threat_types", []),
                start_time=region.get("start_time"),
                end_time=None,
                duration={},
                intensity=region.get("intensity", 0),
                sub_regions=[],
                is_active=region.get("alert", False),
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            alert.calculate_duration()
            alert.calculate_intensity()
            alerts[region["id"]] = alert

        return alerts

    def download_real_alerts(self) -> Optional[Dict[str, AlertData]]:
        """Download real alert data from API"""
        logger.info("Downloading real alert data...")

        content = self.fetch_url(ALERTS_API)
        if not content:
            return None

        try:
            data = json.loads(content)
            states = data.get('states', {})

            alerts = {}
            for region_name, region_data in states.items():
                if region_data.get('enabled'):
                    # Normalize region ID
                    region_id = region_name.lower().replace(' ', '_').replace('.', '')

                    # Determine threat types based on duration
                    threat_types = ['air_raid']  # Default
                    start_time = region_data.get('enabled_at')

                    if start_time:
                        try:
                            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            duration_hours = (datetime.now(timezone.utc) - start_dt).total_seconds() / 3600

                            if duration_hours > 72:
                                threat_types.extend(['artillery', 'street_fighting'])
                            elif duration_hours > 24:
                                threat_types.append('artillery')
                        except:
                            pass

                    alert = AlertData(
                        region_id=region_id,
                        region_name=region_name,
                        region_name_en=region_name,  # Would need translation table
                        alert_level=self._determine_alert_level(threat_types),
                        threat_types=threat_types,
                        start_time=start_time,
                        end_time=region_data.get('disabled_at'),
                        duration={},
                        intensity=0,
                        sub_regions=[],
                        is_active=True,
                        last_updated=datetime.now(timezone.utc).isoformat()
                    )
                    alert.calculate_duration()
                    alert.calculate_intensity()
                    alerts[region_id] = alert

            return alerts
        except Exception as e:
            logger.error(f"Failed to parse alert data: {e}")
            return None

    def _determine_alert_level(self, threat_types: List[str]) -> str:
        """Determine alert level based on threat types"""
        if not threat_types:
            return AlertLevel.NONE.value

        critical_threats = ["nuclear", "ballistic_missiles"]
        high_threats = ["air_raid", "cruise_missiles", "chemical"]
        medium_threats = ["tactical_aviation", "artillery"]

        for threat in threat_types:
            if threat in critical_threats:
                return AlertLevel.CRITICAL.value

        for threat in threat_types:
            if threat in high_threats:
                return AlertLevel.HIGH.value

        for threat in threat_types:
            if threat in medium_threats:
                return AlertLevel.MEDIUM.value

        return AlertLevel.LOW.value

    def save_alerts(self, alerts: Dict[str, AlertData]) -> Path:
        """Save enhanced alert data to JSON file"""
        output_file = self.output_dir / "enhanced_alerts.json"

        # Convert to JSON-serializable format
        alerts_json = {}
        for region_id, alert_data in alerts.items():
            alerts_json[region_id] = asdict(alert_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(alerts_json, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved enhanced alerts to {output_file}")
        return output_file

    def generate_statistics(self, alerts: Dict[str, AlertData]) -> Dict:
        """Generate statistics from alert data"""
        active_alerts = [a for a in alerts.values() if a.is_active]

        stats = {
            "total_regions": len(alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": sum(1 for a in alerts.values() if a.alert_level == AlertLevel.CRITICAL.value),
            "high_alerts": sum(1 for a in alerts.values() if a.alert_level == AlertLevel.HIGH.value),
            "threat_type_counts": {},
            "longest_duration": None,
            "highest_intensity": None,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        # Count threat types and find extremes
        threat_counts = {}
        longest_duration = 0
        highest_intensity = 0
        longest_region = None
        highest_region = None

        for region_id, alert_data in alerts.items():
            if alert_data.is_active:
                # Count threats
                for threat in alert_data.threat_types:
                    threat_counts[threat] = threat_counts.get(threat, 0) + 1

                # Check duration
                total_hours = alert_data.duration.get("days", 0) * 24 + alert_data.duration.get("hours", 0)
                if total_hours > longest_duration:
                    longest_duration = total_hours
                    longest_region = region_id

                # Check intensity
                if alert_data.intensity > highest_intensity:
                    highest_intensity = alert_data.intensity
                    highest_region = region_id

        stats["threat_type_counts"] = threat_counts

        if longest_region:
            stats["longest_duration"] = {
                "region": longest_region,
                "duration": alerts[longest_region].duration,
                "total_hours": longest_duration
            }

        if highest_region:
            stats["highest_intensity"] = {
                "region": highest_region,
                "intensity": highest_intensity,
                "threats": alerts[highest_region].threat_types
            }

        return stats

    def run(self, use_mock: bool = False, try_real_first: bool = True) -> None:
        """Main execution method"""
        logger.info("Starting enhanced alerts download (standalone)...")

        alerts = None

        if not use_mock and try_real_first:
            # Try to download real data first
            alerts = self.download_real_alerts()
            if alerts:
                logger.info(f"Downloaded {len(alerts)} real alerts")

        if not alerts:
            # Fall back to mock data
            alerts = self.download_mock_alerts()
            logger.info(f"Using {len(alerts)} mock alerts")

        # Save alerts
        self.save_alerts(alerts)

        # Generate and save statistics
        stats = self.generate_statistics(alerts)
        stats_file = self.output_dir / "alert_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        # Print summary
        logger.info(f"Alert Statistics:")
        logger.info(f"  Total regions: {stats['total_regions']}")
        logger.info(f"  Active alerts: {stats['active_alerts']}")
        logger.info(f"  Critical alerts: {stats['critical_alerts']}")
        logger.info(f"  High alerts: {stats['high_alerts']}")

        if stats.get("longest_duration"):
            logger.info(f"  Longest alert: {stats['longest_duration']['region']} "
                      f"({stats['longest_duration']['total_hours']} hours)")

        if stats.get("highest_intensity"):
            logger.info(f"  Highest intensity: {stats['highest_intensity']['region']} "
                      f"({stats['highest_intensity']['intensity']}%)")

        logger.info("Enhanced alerts download completed!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Standalone enhanced Ukraine alerts downloader")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for data files"
    )
    parser.add_argument(
        "--mock-only",
        action="store_true",
        help="Use only mock data (don't try to download real alerts)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    downloader = StandaloneAlertsDownloader(output_dir=args.output_dir)
    downloader.run(use_mock=args.mock_only, try_real_first=not args.mock_only)

if __name__ == "__main__":
    main()
