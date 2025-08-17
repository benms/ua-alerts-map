#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced download script for Ukraine alerts map.
Downloads region boundaries, real-time alert statuses with threat analysis, and world map data.
"""

import json
import time
import logging
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Original region IDs from OpenStreetMap
REGION_IDS = {
    'Вінницька область': 90726,
    'Волинська область': 71064,
    'Дніпропетровська область': 101746,
    'Донецька область': 71973,
    'Житомирська область': 71245,
    'Закарпатська область': 72489,
    'Запорізька область': 71980,
    'Івано-Франківська область': 72488,
    'Київська область': 71248,
    'Кіровоградська область': 101859,
    'Луганська область': 71971,
    'Львівська область': 72380,
    'Миколаївська область': 72635,
    'Одеська область': 72634,
    'Полтавська область': 91294,
    'Рівненська область': 71236,
    'Сумська область': 71250,
    'Тернопільська область': 72525,
    'Харківська область': 71254,
    'Херсонська область': 71022,
    'Хмельницька область': 90742,
    'Черкаська область': 91278,
    'Чернівецька область': 72526,
    'Чернігівська область': 71249,
    'м. Київ': 421866,
    'Автономна Республіка Крим': 72639,
    'м. Севастополь': 1574364
}

# Region name mappings for English
REGION_NAMES_EN = {
    'Вінницька область': 'Vinnytsia',
    'Волинська область': 'Volyn',
    'Дніпропетровська область': 'Dnipropetrovsk',
    'Донецька область': 'Donetsk',
    'Житомирська область': 'Zhytomyr',
    'Закарпатська область': 'Zakarpattia',
    'Запорізька область': 'Zaporizhia',
    'Івано-Франківська область': 'Ivano-Frankivsk',
    'Київська область': 'Kyiv Oblast',
    'Кіровоградська область': 'Kirovohrad',
    'Луганська область': 'Luhansk',
    'Львівська область': 'Lviv',
    'Миколаївська область': 'Mykolaiv',
    'Одеська область': 'Odesa',
    'Полтавська область': 'Poltava',
    'Рівненська область': 'Rivne',
    'Сумська область': 'Sumy',
    'Тернопільська область': 'Ternopil',
    'Харківська область': 'Kharkiv',
    'Херсонська область': 'Kherson',
    'Хмельницька область': 'Khmelnytskyi',
    'Черкаська область': 'Cherkasy',
    'Чернівецька область': 'Chernivtsi',
    'Чернігівська область': 'Chernihiv',
    'м. Київ': 'Kyiv City',
    'Автономна Республіка Крим': 'Crimea',
    'м. Севастополь': 'Sevastopol'
}

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
class EnhancedAlertData:
    """Enhanced alert data structure with threat analysis"""
    region_id: str
    region_name: str
    region_name_en: str
    alert_level: str
    threat_types: List[str]
    start_time: Optional[str]
    end_time: Optional[str]
    duration: Dict[str, int]
    intensity: int
    is_active: bool
    last_updated: str

    def calculate_duration(self) -> Dict[str, int]:
        """Calculate duration from start time"""
        if not self.start_time:
            return {"days": 0, "hours": 0, "minutes": 0}

        try:
            # Handle different timestamp formats
            if 'T' in self.start_time:
                start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
            else:
                start = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')

            end = datetime.utcnow()
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

        # Base intensity from threat count
        intensity = len(self.threat_types) * 20

        # Additional intensity based on specific threats
        if ThreatType.BALLISTIC_MISSILES.value in self.threat_types:
            intensity += 30
        if ThreatType.AIR_RAID.value in self.threat_types:
            intensity += 25
        if ThreatType.CRUISE_MISSILES.value in self.threat_types:
            intensity += 20
        if ThreatType.TACTICAL_AVIATION.value in self.threat_types:
            intensity += 15

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

class RegionsDownloader:
    """Main downloader class for regions and alerts"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent.parent / "src" / "data"
        self.regions_dir = self.output_dir / "regions"

        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.regions_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "regions_downloaded": 0,
            "alerts_processed": 0,
            "errors": []
        }

    def download_regions(self, regions: List[str] = None) -> None:
        """Download GeoJSON boundaries for specified or all regions"""
        regions_to_download = regions if regions else list(REGION_IDS.keys())

        logger.info(f"Downloading {len(regions_to_download)} regions...")

        for region_name in regions_to_download:
            if region_name not in REGION_IDS:
                logger.warning(f"Unknown region: {region_name}")
                continue

            region_id = REGION_IDS[region_name]
            output_file = self.regions_dir / f"{region_name}.json"

            try:
                logger.info(f"Downloading {region_name} (ID: {region_id})...")
                url = f"https://polygons.openstreetmap.fr/get_geojson.py?id={region_id}&params=0"

                # Download with timeout
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))

                    # Add metadata to the GeoJSON
                    if 'properties' not in data:
                        data['properties'] = {}

                    data['properties'].update({
                        'name': region_name,
                        'name_en': REGION_NAMES_EN.get(region_name, region_name),
                        'id': region_id,
                        'downloaded_at': datetime.utcnow().isoformat() + 'Z'
                    })

                    # Save to file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    logger.info(f"✓ Downloaded {region_name}")
                    self.stats["regions_downloaded"] += 1

                    # Rate limiting to be respectful to the API
                    time.sleep(0.5)

            except Exception as e:
                error_msg = f"Failed to download {region_name}: {str(e)}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)

    def download_alerts(self) -> Dict[str, Any]:
        """Download current alert statuses and enhance with threat analysis"""
        logger.info("Downloading alert statuses...")

        alerts_data = {}
        enhanced_alerts = {}

        try:
            # Primary source - vadimklimenko.com
            url = "https://vadimklimenko.com/map/statuses.json"
            with urllib.request.urlopen(url, timeout=10) as response:
                full_data = json.loads(response.read().decode('utf-8'))

            # Extract states data from the actual API structure
            if 'states' in full_data:
                alerts_data = full_data['states']
            else:
                alerts_data = full_data

            logger.info(f"Downloaded {len(alerts_data)} alert statuses")

            # Process and enhance each alert
            for region_name, alert_info in alerts_data.items():
                region_name_normalized = self._normalize_region_name(region_name)

                # Determine threat types based on alert data
                threat_types = self._analyze_threats(alert_info)

                # Get timestamps
                start_time = alert_info.get('enabled_at', None)
                end_time = alert_info.get('disabled_at', None)

                # Create enhanced alert data
                enhanced_alert = EnhancedAlertData(
                    region_id=region_name_normalized.lower().replace(' ', '_'),
                    region_name=region_name_normalized,
                    region_name_en=REGION_NAMES_EN.get(region_name_normalized, region_name),
                    alert_level=self._determine_alert_level(alert_info, threat_types),
                    threat_types=threat_types,
                    start_time=start_time,
                    end_time=end_time,
                    duration={},
                    intensity=0,
                    is_active=alert_info.get('enabled', False),
                    last_updated=datetime.utcnow().isoformat() + 'Z'
                )

                # Calculate duration and intensity
                enhanced_alert.calculate_duration()
                enhanced_alert.calculate_intensity()

                enhanced_alerts[region_name_normalized] = enhanced_alert
                self.stats["alerts_processed"] += 1

            # Save original alerts
            alerts_file = self.output_dir / "alerts.json"
            # Save just the states for compatibility
            states_to_save = alerts_data if 'states' not in full_data else {'states': alerts_data, 'version': full_data.get('version', 1)}
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(states_to_save, f, ensure_ascii=False, indent=2)

            # Save enhanced alerts
            enhanced_file = self.output_dir / "enhanced_alerts.json"
            enhanced_data = {
                name: asdict(alert) for name, alert in enhanced_alerts.items()
            }
            with open(enhanced_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ Saved alerts to {alerts_file}")
            logger.info(f"✓ Saved enhanced alerts to {enhanced_file}")

        except Exception as e:
            error_msg = f"Failed to download alerts: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)

        return enhanced_alerts

    def _normalize_region_name(self, name: str) -> str:
        """Normalize region name to match our region IDs"""
        # Remove any extra whitespace
        name = ' '.join(name.split())

        # Check if it's already in our list
        if name in REGION_IDS:
            return name

        # Handle special cases
        if name == "АР Крим":
            return "Автономна Республіка Крим"
        if name == "Севастополь'" or name == "Севастополь":
            return "м. Севастополь"
        if name == "Київ":
            return "м. Київ"

        # Try adding 'область' if it's missing
        if 'область' not in name and 'м.' not in name and 'Автономна' not in name and 'АР' not in name:
            name_with_oblast = name + ' область'
            if name_with_oblast in REGION_IDS:
                return name_with_oblast

        # Try to find a partial match
        for region_name in REGION_IDS.keys():
            if name in region_name or region_name in name:
                return region_name

        return name

    def _analyze_threats(self, alert_info: Dict) -> List[str]:
        """Analyze alert info to determine threat types"""
        threats = []

        if not alert_info.get('enabled', False):
            return threats

        # Default to air raid for any active alert
        threats.append(ThreatType.AIR_RAID.value)

        # Try to analyze based on duration (longer alerts might indicate ongoing operations)
        start_time_str = alert_info.get('enabled_at')
        if start_time_str:
            try:
                # Handle ISO format with timezone
                if 'T' in start_time_str:
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                else:
                    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')

                duration_hours = (datetime.utcnow() - start_time).total_seconds() / 3600

                # Special regions with very long durations (occupied territories)
                region_name = alert_info.get('name', '')
                if duration_hours > 365 * 24:  # Over a year
                    threats.append(ThreatType.STREET_FIGHTING.value)
                    if any(x in region_name for x in ['Крим', 'Севастополь', 'Луганськ', 'Донецьк']):
                        threats.append(ThreatType.ARTILLERY.value)
                elif duration_hours > 72:
                    # Very long duration might indicate frontline areas
                    threats.append(ThreatType.ARTILLERY.value)
                    if duration_hours > 168:  # Over a week
                        threats.append(ThreatType.STREET_FIGHTING.value)
                elif duration_hours > 24:
                    # Long duration might indicate artillery or ongoing operations
                    threats.append(ThreatType.ARTILLERY.value)

            except Exception as e:
                logger.debug(f"Could not parse time for threat analysis: {e}")

        return threats

    def _determine_alert_level(self, alert_info: Dict, threat_types: List[str]) -> str:
        """Determine alert level based on alert info and threats"""
        if not alert_info.get('enabled', False):
            return AlertLevel.NONE.value

        # Check threat types for severity
        if ThreatType.BALLISTIC_MISSILES.value in threat_types:
            return AlertLevel.CRITICAL.value
        if ThreatType.AIR_RAID.value in threat_types:
            return AlertLevel.HIGH.value
        if ThreatType.ARTILLERY.value in threat_types:
            return AlertLevel.MEDIUM.value

        return AlertLevel.LOW.value

    def download_world_map(self) -> None:
        """Download world countries GeoJSON"""
        logger.info("Downloading world map...")

        try:
            url = "https://datahub.io/core/geo-countries/r/countries.geojson"
            output_file = self.output_dir / "countries.json"

            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                logger.info(f"✓ Downloaded world map to {output_file}")

        except Exception as e:
            error_msg = f"Failed to download world map: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)

    def generate_index(self) -> None:
        """Generate index.js file for importing all regions"""
        logger.info("Generating regions index...")

        index_file = self.regions_dir / "index.js"

        # Get all JSON files in regions directory
        region_files = sorted(self.regions_dir.glob("*.json"))

        if not region_files:
            logger.warning("No region files found to index")
            return

        # Generate import statements and exports
        imports = []
        exports = []

        for file in region_files:
            name = file.stem  # filename without extension
            var_name = name.replace(' ', '_').replace('.', '_').replace('-', '_')

            imports.append(f"import {var_name} from './{file.name}';")
            exports.append(f"  '{name}': {var_name},")

        # Write index file
        index_content = f"""// Auto-generated index file for region imports
// Generated at {datetime.utcnow().isoformat()}Z

{chr(10).join(imports)}

const regions = {{
{chr(10).join(exports)}
}};

export default regions;
"""

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        logger.info(f"✓ Generated index for {len(region_files)} regions")

    def print_statistics(self) -> None:
        """Print download statistics"""
        print("\n" + "="*50)
        print("DOWNLOAD STATISTICS")
        print("="*50)
        print(f"Regions downloaded: {self.stats['regions_downloaded']}")
        print(f"Alerts processed: {self.stats['alerts_processed']}")

        if self.stats['errors']:
            print(f"\n⚠ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print("\n✅ No errors encountered")

        print("="*50)

    def run(self, skip_regions=False, skip_alerts=False, skip_world=False, regions=None) -> None:
        """Main execution method"""
        start_time = time.time()

        logger.info("Starting enhanced data download...")

        if not skip_regions:
            self.download_regions(regions)
            self.generate_index()

        if not skip_alerts:
            alerts = self.download_alerts()

            # Print some alert statistics
            if alerts:
                active_alerts = [a for a in alerts.values() if a.is_active]
                logger.info(f"Active alerts: {len(active_alerts)}/{len(alerts)}")

                # Find longest running alert
                if active_alerts:
                    longest = max(active_alerts,
                                key=lambda a: a.duration.get('days', 0) * 24 + a.duration.get('hours', 0))
                    logger.info(f"Longest alert: {longest.region_name} - {longest.duration['days']}d {longest.duration['hours']}h")

        if not skip_world:
            self.download_world_map()

        elapsed = time.time() - start_time
        logger.info(f"✅ Download completed in {elapsed:.1f} seconds")

        self.print_statistics()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download enhanced Ukraine regions and alert data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_regions.py                    # Download everything
  python download_regions.py --skip-world       # Skip world map download
  python download_regions.py --list-regions     # List available regions
  python download_regions.py --regions "м. Київ" "Львівська область"  # Specific regions only
        """
    )

    parser.add_argument(
        "--skip-regions",
        action="store_true",
        help="Skip downloading region boundaries"
    )
    parser.add_argument(
        "--skip-alerts",
        action="store_true",
        help="Skip downloading alert data"
    )
    parser.add_argument(
        "--skip-world",
        action="store_true",
        help="Skip downloading world map"
    )
    parser.add_argument(
        "--regions",
        nargs="+",
        help="Download only specific regions (by name)"
    )
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all available regions and exit"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Custom output directory (default: ../src/data)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Handle list regions
    if args.list_regions:
        print("\nAvailable regions:")
        print("-" * 40)
        for i, (name, region_id) in enumerate(REGION_IDS.items(), 1):
            name_en = REGION_NAMES_EN.get(name, '')
            print(f"{i:2}. {name:30} (ID: {region_id:6}) [{name_en}]")
        print("-" * 40)
        print(f"Total: {len(REGION_IDS)} regions")
        return

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run downloader
    downloader = RegionsDownloader(output_dir=args.output_dir)
    downloader.run(
        skip_regions=args.skip_regions,
        skip_alerts=args.skip_alerts,
        skip_world=args.skip_world,
        regions=args.regions
    )

if __name__ == '__main__':
    main()
