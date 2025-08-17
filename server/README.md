# Ukraine Alerts Map - Python Backend

Enhanced data pipeline for fetching and processing Ukraine air raid alerts with multiple threat types, duration tracking, and intensity calculations.

## Overview

This Python backend provides sophisticated data processing for the Ukraine Alerts Map application, transforming simple alert data into rich, multi-dimensional threat assessments with:

- **Multiple threat types** (air raids, missiles, drones, artillery, etc.)
- **Duration tracking** (days, hours, minutes since alert start)
- **Intensity calculations** (0-100% based on threat severity and duration)
- **Enhanced metadata** (threat icons, colors, patterns, priorities)
- **Real-time data integration** from multiple sources

## Features

### 🎯 Core Capabilities

- **Multi-source data aggregation** - Combines data from OpenStreetMap and alert APIs
- **Threat analysis** - Automatically determines threat types based on alert patterns
- **Duration calculations** - Tracks how long each region has been under alert
- **Intensity scoring** - Calculates threat intensity based on multiple factors
- **GeoJSON boundaries** - Downloads and caches region boundary data
- **Statistics generation** - Provides comprehensive alert statistics

### 📊 Data Enhancements

The backend transforms basic alert data into rich information:

```json
{
  "region_name": "Луганська область",
  "alert_level": "high",
  "threat_types": ["air_raid", "artillery", "street_fighting"],
  "duration": {"days": 1220, "hours": 17, "minutes": 0},
  "intensity": 95,
  "color": "#dc143c"
}
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Basic Setup

```bash
# Navigate to server directory
cd server

# Install dependencies (if using pip)
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Download all data (regions, alerts, world map)
python download_regions.py

# Generate enhanced alert data matching the design
python generate_enhanced_alerts.py

# Download enhanced alerts with threat analysis
python download_enhanced_alerts.py --skip-boundaries

# Use standalone version (no external dependencies)
python download_enhanced_alerts_standalone.py

# Run tests
python test_enhanced_alerts.py

# Interactive demo
python demo.py
```

### Command Line Options

#### download_regions.py

Main data pipeline script with flexible options:

```bash
# List all available regions
python download_regions.py --list-regions

# Download specific regions only
python download_regions.py --regions "м. Київ" "Львівська область"

# Skip certain data types
python download_regions.py --skip-regions  # Skip region boundaries
python download_regions.py --skip-alerts   # Skip alert data
python download_regions.py --skip-world    # Skip world map

# Verbose output
python download_regions.py -v

# Custom output directory
python download_regions.py --output-dir /path/to/output
```

#### generate_enhanced_alerts.py

Generate realistic enhanced alert data based on the design mockup:

```bash
# Generate enhanced alerts with threat analysis
python generate_enhanced_alerts.py
```

This creates:
- `enhanced_alerts.json` - Full alert data with threat types and metadata
- `alert_statistics.json` - Comprehensive statistics about active alerts

#### test_enhanced_alerts.py

Run comprehensive test suite:

```bash
# Run all tests
python test_enhanced_alerts.py

# Verbose test output
python test_enhanced_alerts.py -v
```

#### download_enhanced_alerts.py

Enhanced downloader with automatic threat analysis:

```bash
# Download alerts with threat analysis
python download_enhanced_alerts.py

# Skip region boundaries download
python download_enhanced_alerts.py --skip-boundaries

# Use verbose logging
python download_enhanced_alerts.py -v
```

#### download_enhanced_alerts_standalone.py

Standalone version using only Python standard library (no pip install required):

```bash
# Download with automatic API fallback
python download_enhanced_alerts_standalone.py

# Use mock data only (for testing)
python download_enhanced_alerts_standalone.py --mock-only

# Specify output directory
python download_enhanced_alerts_standalone.py --output-dir /path/to/output
```

## Data Structures

### Enhanced Alert Data

Each region's alert contains:

| Field | Type | Description |
|-------|------|-------------|
| `region_id` | string | Normalized region identifier |
| `region_name` | string | Ukrainian region name |
| `region_name_en` | string | English region name |
| `alert_level` | enum | none, low, medium, high, critical |
| `threat_types` | array | Active threat types |
| `start_time` | ISO 8601 | When alert started |
| `duration` | object | Days, hours, minutes |
| `intensity` | 0-100 | Calculated threat intensity |
| `is_active` | boolean | Whether alert is currently active |
| `color` | hex | Display color for the region |

### Threat Types

| Type | Description | Icon | Priority |
|------|-------------|------|----------|
| `air_raid` | Air raid alert | ✈️ | 10 |
| `tactical_aviation` | Tactical aviation activity | 🛩️ | 8 |
| `cruise_missiles` | Cruise missile threat | 🚀 | 9 |
| `ballistic_missiles` | Ballistic missile threat | 🎯 | 10 |
| `drones` | UAV/drone threat | 🛸 | 6 |
| `artillery` | Artillery shelling threat | 💥 | 7 |
| `street_fighting` | Urban combat operations | 🛡️ | 5 |

### Alert Levels

- **🟢 None** - No active threats
- **🟡 Low** - Minor threat activity
- **🟠 Medium** - Moderate threat level
- **🔴 High** - Significant threat level
- **⚫ Critical** - Maximum threat level

## API Integration

### Primary Data Sources

1. **OpenStreetMap** - Region boundary data
   - Endpoint: `https://polygons.openstreetmap.fr/`
   - Format: GeoJSON

2. **Alert Status API** - Real-time alert data
   - Endpoint: `https://vadimklimenko.com/map/statuses.json`
   - Format: JSON with nested region/district structure

3. **World Countries** - Global map overlay
   - Endpoint: `https://datahub.io/core/geo-countries/`
   - Format: GeoJSON

## Output Files

The scripts generate the following files in `../src/data/`:

```
src/data/
├── regions/
│   ├── *.json                    # Individual region GeoJSON files
│   └── index.js                  # Auto-generated import index
├── alerts.json                   # Raw alert data
├── enhanced_alerts.json          # Enhanced alert data with threat analysis
├── alert_statistics.json         # Statistical summary
└── countries.json               # World map data
```

## Statistics Generated

The system automatically calculates:

- Total regions and active alerts
- Alert counts by threat type
- Longest running alert (region and duration)
- Highest intensity alert
- Critical vs high vs medium vs low alerts
- Clear vs threatened regions

Example statistics output:

```json
{
  "total_regions": 27,
  "active_alerts": 6,
  "threat_type_counts": {
    "air_raid": 5,
    "artillery": 3,
    "drones": 3
  },
  "longest_alert": {
    "region": "Луганська область",
    "total_hours": 29297
  },
  "highest_intensity": {
    "region": "Луганська область",
    "intensity": 95
  }
}
```

## Available Scripts

| Script | Purpose | Dependencies |
|--------|---------|--------------|
| `download_regions.py` | Main data pipeline | None |
| `generate_enhanced_alerts.py` | Generate mock data matching design | None |
| `download_enhanced_alerts.py` | Enhanced downloader with threat analysis | requests |
| `download_enhanced_alerts_standalone.py` | Standalone enhanced downloader | None |
| `test_enhanced_alerts.py` | Comprehensive test suite | None |
| `demo.py` | Interactive demonstration | None |

## Testing

### Test Coverage

- ✅ Alert level determination logic
- ✅ Duration calculation accuracy
- ✅ Threat type analysis
- ✅ Statistics generation
- ✅ Data structure validation
- ✅ JSON file generation
- ✅ Region ID normalization
- ✅ Timezone-aware datetime handling

### Running Tests

```bash
# Run all tests
python test_enhanced_alerts.py

# Run with pytest (if installed)
pytest tests/

# Run specific test
python -m unittest test_enhanced_alerts.TestEnhancedAlerts.test_duration_calculation_accuracy
```

## Known Issues and Fixes

### Timezone Handling

The scripts now properly handle timezone-aware datetime objects. All timestamps use `datetime.now(timezone.utc)` instead of the deprecated `datetime.utcnow()` to ensure compatibility with Python 3.12+.

### Dependencies

Two versions are available:
- **Full version** (`download_enhanced_alerts.py`) - Requires `requests` library
- **Standalone version** (`download_enhanced_alerts_standalone.py`) - Uses only Python standard library

## Development

### Adding New Threat Types

1. Add to `ThreatType` enum in `download_regions.py`
2. Add metadata to `THREAT_METADATA` in `generate_enhanced_alerts.py`
3. Update threat analysis logic in `_analyze_threats()`
4. Add appropriate icon and styling in frontend

### Adding New Regions

1. Add region to `REGION_IDS` with OSM relation ID
2. Add English translation to `REGION_NAMES_EN`
3. Run `python download_regions.py --regions "New Region"`

### Customizing Alert Generation

Edit `REGION_ALERT_CONFIG` in `generate_enhanced_alerts.py`:

```python
'Region Name': {
    'enabled': True,
    'threat_types': ['air_raid', 'drones'],
    'duration_days': 5,
    'duration_hours': 12,
    'intensity': 75,
    'color': '#ff6b6b'
}
```

## Error Handling

The system includes robust error handling:

- **Network failures** - Automatic retries with exponential backoff
- **Invalid data** - Graceful degradation with logged warnings
- **Missing regions** - Skips and continues with available data
- **API changes** - Flexible parsing to handle structure variations

## Performance

- **Rate limiting** - Respects API rate limits (0.5s between requests)
- **Caching** - Stores downloaded data locally
- **Batch processing** - Efficient handling of multiple regions
- **Parallel capable** - Can be extended for concurrent downloads

## Troubleshooting

### Common Issues

1. **"Region not found"**
   - Check region name spelling (must match exactly)
   - Use `--list-regions` to see available regions

2. **"Failed to download alerts"**
   - Check internet connection
   - Verify API endpoint is accessible
   - Check for API changes
   - Try the standalone version which includes mock data fallback

3. **"Invalid timestamp format" or timezone errors**
   - Fixed in latest version - now uses `timezone.utc` consistently
   - All datetime objects are timezone-aware
   - Handles both ISO format and legacy timestamps

4. **"ModuleNotFoundError: No module named 'requests'"**
   - Install with `pip install requests`
   - Or use `download_enhanced_alerts_standalone.py` which needs no dependencies

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python download_regions.py -v
```

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to all functions
- Keep functions focused and testable

### Testing Requirements

- Add tests for new features
- Maintain >80% code coverage
- Ensure all tests pass before committing

## License

This backend is part of the Ukraine Alerts Map project. See main project LICENSE for details.

## Support

For issues or questions:
- Check existing GitHub issues
- Review test output for diagnostic info
- Enable verbose mode for detailed logging

---

*Built with ❤️ to provide accurate, timely alert information for Ukraine*