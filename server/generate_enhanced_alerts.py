#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate enhanced alert data matching the design mockup.
Creates realistic alert data with multiple threat types, durations, and intensities.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any

# Region configurations based on the image
REGION_ALERT_CONFIG = {
    'Луганська область': {
        'enabled': True,
        'threat_types': ['air_raid', 'artillery', 'street_fighting'],
        'duration_days': 1220,
        'duration_hours': 17,
        'intensity': 95,
        'color': '#dc143c'  # Dark red
    },
    'Донецька область': {
        'enabled': True,
        'threat_types': ['air_raid', 'tactical_aviation', 'artillery', 'drones'],
        'duration_days': 3,
        'duration_hours': 49,
        'intensity': 85,
        'color': '#ff6b6b'  # Medium red
    },
    'Запорізька область': {
        'enabled': True,
        'threat_types': ['air_raid', 'drones'],
        'duration_hours': 31,
        'intensity': 65,
        'color': '#ff8866'  # Light red
    },
    'Херсонська область': {
        'enabled': True,
        'threat_types': ['artillery', 'drones'],
        'duration_hours': 30,
        'intensity': 60,
        'color': '#ffcccb'  # Light pink with dots
    },
    'Автономна Республіка Крим': {
        'enabled': True,
        'threat_types': ['air_raid', 'tactical_aviation'],
        'duration_days': 990,
        'duration_hours': 11,
        'intensity': 90,
        'color': '#dc143c'  # Dark red
    },
    'Дніпропетровська область': {
        'enabled': True,
        'threat_types': ['air_raid'],
        'duration_hours': 32,
        'intensity': 50,
        'color': '#ffcccb'  # Light pink with dots
    },
    # Clear regions (no alerts)
    'Вінницька область': {'enabled': False},
    'Волинська область': {'enabled': False},
    'Житомирська область': {'enabled': False},
    'Закарпатська область': {'enabled': False},
    'Івано-Франківська область': {'enabled': False},
    'Київська область': {'enabled': False},
    'Кіровоградська область': {'enabled': False},
    'Львівська область': {'enabled': False},
    'Миколаївська область': {'enabled': False},
    'Одеська область': {'enabled': False},
    'Полтавська область': {'enabled': False},
    'Рівненська область': {'enabled': False},
    'Сумська область': {'enabled': False},
    'Тернопільська область': {'enabled': False},
    'Харківська область': {'enabled': False},
    'Хмельницька область': {'enabled': False},
    'Черкаська область': {'enabled': False},
    'Чернівецька область': {'enabled': False},
    'Чернігівська область': {'enabled': False},
    'м. Київ': {'enabled': False},
    'м. Севастополь': {'enabled': False}
}

# English names mapping
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

# Threat type metadata
THREAT_METADATA = {
    'air_raid': {
        'label': 'Повітряна тривога',
        'label_en': 'Air raid alert',
        'icon': 'plane',
        'priority': 10,
        'color': '#dc143c'
    },
    'tactical_aviation': {
        'label': 'Активність тактичної авіації',
        'label_en': 'Tactical aviation activity',
        'icon': 'fighter-jet',
        'priority': 8,
        'color': '#ff6b6b'
    },
    'cruise_missiles': {
        'label': 'Крилаті ракети',
        'label_en': 'Cruise missiles',
        'icon': 'rocket',
        'priority': 9,
        'color': '#ff4444'
    },
    'ballistic_missiles': {
        'label': 'Балістичні ракети',
        'label_en': 'Ballistic missiles',
        'icon': 'missile',
        'priority': 10,
        'color': '#cc0000'
    },
    'drones': {
        'label': 'Загроза застосування БпЛА',
        'label_en': 'UAV threat',
        'icon': 'drone',
        'priority': 6,
        'color': '#ff8866'
    },
    'artillery': {
        'label': 'Загроза артобстрілу',
        'label_en': 'Artillery threat',
        'icon': 'explosion',
        'priority': 7,
        'color': '#ff9999',
        'pattern': 'dotted'
    },
    'street_fighting': {
        'label': 'Загроза вуличних боїв',
        'label_en': 'Street fighting threat',
        'icon': 'shield-alt',
        'priority': 5,
        'color': '#cd5c5c',
        'pattern': 'striped'
    }
}

def calculate_start_time(days: int = 0, hours: int = 0, minutes: int = 0) -> str:
    """Calculate start time based on duration"""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days, hours=hours, minutes=minutes)
    return start.isoformat()

def determine_alert_level(threat_types: List[str], intensity: int) -> str:
    """Determine alert level based on threats and intensity"""
    if not threat_types:
        return 'none'

    critical_threats = ['ballistic_missiles', 'nuclear', 'chemical']
    high_threats = ['air_raid', 'cruise_missiles', 'tactical_aviation']
    medium_threats = ['artillery', 'drones']

    for threat in threat_types:
        if threat in critical_threats:
            return 'critical'

    for threat in threat_types:
        if threat in high_threats:
            return 'high'

    for threat in threat_types:
        if threat in medium_threats:
            return 'medium'

    return 'low'

def generate_enhanced_alert(region_name: str, config: Dict) -> Dict[str, Any]:
    """Generate enhanced alert data for a region"""

    if not config.get('enabled', False):
        # No alert
        return {
            'region_id': region_name.lower().replace(' ', '_').replace('.', ''),
            'region_name': region_name,
            'region_name_en': REGION_NAMES_EN.get(region_name, region_name),
            'alert_level': 'none',
            'threat_types': [],
            'start_time': None,
            'end_time': None,
            'duration': {'days': 0, 'hours': 0, 'minutes': 0},
            'intensity': 0,
            'is_active': False,
            'color': '#ffffff',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    # Calculate duration
    days = config.get('duration_days', 0)
    hours = config.get('duration_hours', 0)
    minutes = config.get('duration_minutes', 0)

    # Generate start time
    start_time = calculate_start_time(days, hours, minutes)

    # Get threat types
    threat_types = config.get('threat_types', ['air_raid'])

    # Get intensity
    intensity = config.get('intensity', 50)

    # Determine alert level
    alert_level = determine_alert_level(threat_types, intensity)

    return {
        'region_id': region_name.lower().replace(' ', '_').replace('.', ''),
        'region_name': region_name,
        'region_name_en': REGION_NAMES_EN.get(region_name, region_name),
        'alert_level': alert_level,
        'threat_types': threat_types,
        'start_time': start_time,
        'end_time': None,  # Active alerts have no end time
        'duration': {
            'days': days,
            'hours': hours,
            'minutes': minutes
        },
        'intensity': intensity,
        'is_active': True,
        'color': config.get('color', '#ff6b6b'),
        'threat_metadata': {
            threat: THREAT_METADATA.get(threat, {})
            for threat in threat_types
        },
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

def generate_statistics(alerts: Dict[str, Any]) -> Dict[str, Any]:
    """Generate statistics from alerts data"""

    active_alerts = [a for a in alerts.values() if a['is_active']]

    # Count threat types
    threat_counts = {}
    for alert in active_alerts:
        for threat in alert['threat_types']:
            threat_counts[threat] = threat_counts.get(threat, 0) + 1

    # Find longest and highest intensity
    longest_alert = None
    highest_intensity = None

    if active_alerts:
        longest_alert = max(
            active_alerts,
            key=lambda a: a['duration']['days'] * 24 + a['duration']['hours']
        )
        highest_intensity = max(active_alerts, key=lambda a: a['intensity'])

    return {
        'total_regions': len(alerts),
        'active_alerts': len(active_alerts),
        'clear_regions': len(alerts) - len(active_alerts),
        'threat_type_counts': threat_counts,
        'critical_alerts': sum(1 for a in active_alerts if a['alert_level'] == 'critical'),
        'high_alerts': sum(1 for a in active_alerts if a['alert_level'] == 'high'),
        'medium_alerts': sum(1 for a in active_alerts if a['alert_level'] == 'medium'),
        'low_alerts': sum(1 for a in active_alerts if a['alert_level'] == 'low'),
        'longest_alert': {
            'region': longest_alert['region_name'],
            'region_en': longest_alert['region_name_en'],
            'duration': longest_alert['duration'],
            'total_hours': longest_alert['duration']['days'] * 24 + longest_alert['duration']['hours']
        } if longest_alert else None,
        'highest_intensity': {
            'region': highest_intensity['region_name'],
            'region_en': highest_intensity['region_name_en'],
            'intensity': highest_intensity['intensity'],
            'threats': highest_intensity['threat_types']
        } if highest_intensity else None,
        'generated_at': datetime.now(timezone.utc).isoformat()
    }

def main():
    """Generate enhanced alert data files"""

    output_dir = Path(__file__).parent.parent / 'src' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating enhanced alert data...")
    print("=" * 50)

    # Generate enhanced alerts
    enhanced_alerts = {}
    for region_name, config in REGION_ALERT_CONFIG.items():
        alert = generate_enhanced_alert(region_name, config)
        enhanced_alerts[region_name] = alert

        if alert['is_active']:
            duration = alert['duration']
            print(f"✓ {region_name}: {duration['days']}d {duration['hours']}h - "
                  f"Intensity: {alert['intensity']}% - Threats: {', '.join(alert['threat_types'])}")

    # Save enhanced alerts
    enhanced_file = output_dir / 'enhanced_alerts.json'
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_alerts, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved enhanced alerts to {enhanced_file}")

    # Generate and save statistics
    stats = generate_statistics(enhanced_alerts)
    stats_file = output_dir / 'alert_statistics.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved statistics to {stats_file}")

    # Print summary
    print("\n" + "=" * 50)
    print("ALERT SUMMARY")
    print("=" * 50)
    print(f"Total regions: {stats['total_regions']}")
    print(f"Active alerts: {stats['active_alerts']}")
    print(f"Clear regions: {stats['clear_regions']}")

    if stats['threat_type_counts']:
        print("\nThreat types:")
        for threat, count in sorted(stats['threat_type_counts'].items(),
                                   key=lambda x: x[1], reverse=True):
            metadata = THREAT_METADATA.get(threat, {})
            label = metadata.get('label', threat)
            print(f"  {label}: {count} regions")

    if stats['longest_alert']:
        longest = stats['longest_alert']
        print(f"\nLongest alert: {longest['region']} ({longest['total_hours']} hours)")

    if stats['highest_intensity']:
        highest = stats['highest_intensity']
        print(f"Highest intensity: {highest['region']} ({highest['intensity']}%)")

    print("=" * 50)
    print("✅ Enhanced alert data generation complete!")

if __name__ == '__main__':
    main()
