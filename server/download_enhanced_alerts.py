#!/usr/bin/env python3
"""
Enhanced download script for Ukraine alerts with multiple threat types and duration tracking.
Downloads region boundaries, alert statuses with threat details, and calculates durations.
"""

import json
import time
import logging
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints
ALERTS_API_BASE = "https://api.ukrainealarm.com"
ALERTS_IN_UA_API = "https://alerts.in.ua/api/v1"
OSM_NOMINATIM_API = "https://nominatim.openstreetmap.org"
OVERPASS_API = "https://overpass-api.de/api/interpreter"

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

        start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00')) if self.end_time else datetime.now(timezone.utc)

        delta = end - start
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        self.duration = {"days": days, "hours": hours, "minutes": minutes}
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

class EnhancedAlertsDownloader:
    """Enhanced downloader for Ukraine alerts with multiple data sources"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent / "src" / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Cache for API responses
        self.cache = {}

    def download_alerts_from_multiple_sources(self) -> Dict[str, AlertData]:
        """Download and merge alert data from multiple sources"""
        logger.info("Fetching alert data from multiple sources...")

        alerts = {}

        # Try primary source
        try:
            primary_alerts = self._fetch_primary_alerts()
            alerts.update(primary_alerts)
        except Exception as e:
            logger.error(f"Failed to fetch primary alerts: {e}")

        # Try secondary source
        try:
            secondary_alerts = self._fetch_secondary_alerts()
            alerts = self._merge_alerts(alerts, secondary_alerts)
        except Exception as e:
            logger.error(f"Failed to fetch secondary alerts: {e}")

        # Calculate durations and intensities
        for alert_id, alert_data in alerts.items():
            alert_data.calculate_duration()
            alert_data.calculate_intensity()

        return alerts

    def _fetch_primary_alerts(self) -> Dict[str, AlertData]:
        """Fetch alerts from primary API (alerts.in.ua style)"""
        alerts = {}

        # Simulated API response - replace with actual API call
        mock_regions = [
            {
                "id": "lugansk",
                "name": "Луганська",
                "name_en": "Luhansk",
                "alert": True,
                "threat_types": ["air_raid", "artillery"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1220, hours=17)).isoformat(),
                "intensity": 85
            },
            {
                "id": "donetsk",
                "name": "Донецька",
                "name_en": "Donetsk",
                "alert": True,
                "threat_types": ["air_raid", "tactical_aviation", "artillery"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=3, hours=49)).isoformat(),
                "intensity": 90
            },
            {
                "id": "zaporizhia",
                "name": "Запорізька",
                "name_en": "Zaporizhia",
                "alert": True,
                "threat_types": ["air_raid"],
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=31)).isoformat(),
                "intensity": 60
            },
            {
                "id": "kherson",
                "name": "Херсонська",
                "name_en": "Kherson",
                "alert": True,
                "threat_types": ["artillery", "drones"],
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat(),
                "intensity": 55
            },
            {
                "id": "crimea",
                "name": "Автономна Республіка Крим",
                "name_en": "Autonomous Republic of Crimea",
                "alert": True,
                "threat_types": ["air_raid", "tactical_aviation"],
                "start_time": (datetime.now(timezone.utc) - timedelta(days=990, hours=11)).isoformat(),
                "intensity": 80
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

        for region in mock_regions:
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
            alerts[region["id"]] = alert

        return alerts

    def _fetch_secondary_alerts(self) -> Dict[str, AlertData]:
        """Fetch alerts from secondary API source"""
        alerts = {}

        # This would be another API source
        # For now, return empty dict
        return alerts

    def _merge_alerts(self, primary: Dict[str, AlertData], secondary: Dict[str, AlertData]) -> Dict[str, AlertData]:
        """Merge alert data from multiple sources"""
        merged = primary.copy()

        for region_id, alert_data in secondary.items():
            if region_id in merged:
                # Merge threat types
                existing_threats = set(merged[region_id].threat_types)
                new_threats = set(alert_data.threat_types)
                merged[region_id].threat_types = list(existing_threats.union(new_threats))

                # Use earliest start time
                if alert_data.start_time and merged[region_id].start_time:
                    existing_start = datetime.fromisoformat(merged[region_id].start_time.replace('Z', '+00:00'))
                    new_start = datetime.fromisoformat(alert_data.start_time.replace('Z', '+00:00'))
                    if new_start < existing_start:
                        merged[region_id].start_time = alert_data.start_time

                # Use highest intensity
                merged[region_id].intensity = max(merged[region_id].intensity, alert_data.intensity)
            else:
                merged[region_id] = alert_data

        return merged

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

    def download_region_boundaries(self) -> Dict[str, Any]:
        """Download GeoJSON boundaries for all regions"""
        logger.info("Downloading region boundaries...")

        regions_dir = self.output_dir / "regions"
        regions_dir.mkdir(exist_ok=True)

        # List of Ukrainian regions with their OSM relation IDs
        regions = {
            "vinnytsia": 60433,
            "volyn": 72525,
            "dnipropetrovsk": 71248,
            "donetsk": 71249,
            "zhytomyr": 71250,
            "zakarpattia": 72526,
            "zaporizhia": 71251,
            "ivano-frankivsk": 72527,
            "kyiv": 71252,
            "kirovohrad": 71253,
            "lugansk": 71254,
            "lviv": 72528,
            "mykolaiv": 71255,
            "odesa": 72529,
            "poltava": 71256,
            "rivne": 72530,
            "sumy": 71257,
            "ternopil": 72531,
            "kharkiv": 71258,
            "kherson": 71259,
            "khmelnytskyi": 72532,
            "cherkasy": 71260,
            "chernivtsi": 72533,
            "chernihiv": 71261,
            "crimea": 72639,
            "kyiv_city": 421866,
            "sevastopol": 1574364
        }

        boundaries = {}

        for region_name, relation_id in regions.items():
            try:
                # Query Overpass API for region boundary
                query = f"""
                [out:json][timeout:25];
                relation({relation_id});
                out geom;
                """

                response = self.session.post(
                    OVERPASS_API,
                    data={"data": query},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("elements"):
                        element = data["elements"][0]
                        # Convert to GeoJSON format
                        geojson = self._convert_to_geojson(element)

                        # Save individual region file
                        region_file = regions_dir / f"{region_name}.geojson"
                        with open(region_file, 'w', encoding='utf-8') as f:
                            json.dump(geojson, f, ensure_ascii=False, indent=2)

                        boundaries[region_name] = geojson
                        logger.info(f"Downloaded boundary for {region_name}")

                    # Rate limiting
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to download boundary for {region_name}: {e}")

        return boundaries

    def _convert_to_geojson(self, osm_element: Dict) -> Dict:
        """Convert OSM element to GeoJSON format"""
        # This is a simplified conversion - real implementation would need
        # proper geometry processing
        return {
            "type": "Feature",
            "properties": {
                "id": osm_element.get("id"),
                "name": osm_element.get("tags", {}).get("name"),
                "name:en": osm_element.get("tags", {}).get("name:en"),
                "admin_level": osm_element.get("tags", {}).get("admin_level")
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": []  # Would need proper coordinate extraction
            }
        }

    def save_enhanced_alerts(self, alerts: Dict[str, AlertData]) -> Path:
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
        stats = {
            "total_regions": len(alerts),
            "active_alerts": sum(1 for a in alerts.values() if a.is_active),
            "critical_alerts": sum(1 for a in alerts.values() if a.alert_level == AlertLevel.CRITICAL.value),
            "threat_type_counts": {},
            "longest_duration": None,
            "highest_intensity": None,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        # Count threat types
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

    def run(self, download_boundaries: bool = True, download_alerts: bool = True) -> None:
        """Main execution method"""
        logger.info("Starting enhanced alerts download...")

        if download_boundaries:
            boundaries = self.download_region_boundaries()
            logger.info(f"Downloaded {len(boundaries)} region boundaries")

        if download_alerts:
            alerts = self.download_alerts_from_multiple_sources()
            self.save_enhanced_alerts(alerts)

            # Generate and save statistics
            stats = self.generate_statistics(alerts)
            stats_file = self.output_dir / "alert_statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)

            logger.info(f"Alert Statistics:")
            logger.info(f"  Total regions: {stats['total_regions']}")
            logger.info(f"  Active alerts: {stats['active_alerts']}")
            logger.info(f"  Critical alerts: {stats['critical_alerts']}")

            if stats.get("longest_duration"):
                logger.info(f"  Longest alert: {stats['longest_duration']['region']} "
                          f"({stats['longest_duration']['total_hours']} hours)")

            if stats.get("highest_intensity"):
                logger.info(f"  Highest intensity: {stats['highest_intensity']['region']} "
                          f"({stats['highest_intensity']['intensity']}%)")

        logger.info("Enhanced alerts download completed!")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Download enhanced Ukraine alerts data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for data files"
    )
    parser.add_argument(
        "--skip-boundaries",
        action="store_true",
        help="Skip downloading region boundaries"
    )
    parser.add_argument(
        "--skip-alerts",
        action="store_true",
        help="Skip downloading alert data"
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

    downloader = EnhancedAlertsDownloader(output_dir=args.output_dir)
    downloader.run(
        download_boundaries=not args.skip_boundaries,
        download_alerts=not args.skip_alerts
    )

if __name__ == "__main__":
    main()
