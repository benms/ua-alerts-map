# Changelog

All notable changes to the Ukraine Alerts Map Python Backend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-08-17

### Added
- **Enhanced Alert System** - Complete overhaul with multi-threat analysis
  - Multiple threat types per region (air raids, missiles, drones, artillery, etc.)
  - Duration tracking with days, hours, and minutes
  - Intensity calculations (0-100% based on threat severity and duration)
  - Color-coded alert levels (none, low, medium, high, critical)

- **New Scripts**
  - `download_enhanced_alerts.py` - Enhanced downloader with automatic threat analysis
  - `download_enhanced_alerts_standalone.py` - Zero-dependency version using only standard library
  - `generate_enhanced_alerts.py` - Generates realistic mock data matching the design
  - `test_enhanced_alerts.py` - Comprehensive test suite for all functionality
  - `demo.py` - Interactive demonstration with colored terminal output

- **Data Enhancements**
  - Threat metadata with icons, colors, and priorities
  - Automatic threat type determination based on alert duration
  - Support for occupied territories with long-duration alerts
  - Region-specific intensity calculations

- **Testing Infrastructure**
  - 10+ comprehensive test cases
  - Duration calculation accuracy tests
  - Threat analysis validation
  - Statistics generation verification

### Fixed
- **Timezone Handling** - Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- **DateTime Compatibility** - All datetime objects are now timezone-aware
- **Python 3.12+ Support** - Fixed all deprecation warnings
- **API Data Parsing** - Improved handling of various timestamp formats

### Changed
- **Data Structure** - Enhanced alert JSON now includes:
  ```json
  {
    "region_id": "lugansk",
    "alert_level": "high",
    "threat_types": ["air_raid", "artillery", "street_fighting"],
    "duration": {"days": 1220, "hours": 17, "minutes": 0},
    "intensity": 95,
    "color": "#dc143c"
  }
  ```

- **Statistics Output** - Now includes threat distribution and alert level breakdown
- **Error Handling** - More robust with automatic fallback to mock data

## [1.0.0] - 2024-08-10

### Added
- Initial implementation of `download_regions.py`
- Basic alert data fetching from vadimklimenko.com API
- GeoJSON boundary downloads from OpenStreetMap
- World map data integration
- Support for 27 Ukrainian regions including Crimea and Sevastopol

### Features
- Command-line interface with flexible options
- List regions functionality
- Selective region downloading
- Auto-generated index.js for React imports
- Basic alert status tracking (enabled/disabled)

## Installation Notes

### Version 2.0.0
```bash
# Full version (with dependencies)
pip install requests
python download_enhanced_alerts.py

# Standalone version (no dependencies)
python download_enhanced_alerts_standalone.py
```

### Version 1.0.0
```bash
python download_regions.py
```

## Migration Guide

### From 1.0.0 to 2.0.0

The enhanced version is backward compatible but adds significant new features:

1. **Alert Data Structure** - The basic `alerts.json` is still generated, but `enhanced_alerts.json` provides richer data
2. **Threat Analysis** - Automatic threat type determination based on alert patterns
3. **Duration Tracking** - Precise tracking of how long each alert has been active

To migrate:
1. Update your frontend to use `enhanced_alerts.json` instead of `alerts.json`
2. Utilize the new threat types and intensity values for better visualization
3. Display duration information using the structured format

## Future Roadmap

### Version 2.1.0 (Planned)
- [ ] WebSocket support for real-time updates
- [ ] Historical alert data tracking
- [ ] Alert prediction based on patterns
- [ ] Multi-language support for all threat types

### Version 3.0.0 (Concept)
- [ ] Machine learning threat classification
- [ ] Integration with multiple alert APIs
- [ ] Automated alert verification system
- [ ] GraphQL API endpoint

## Contributors

- Original implementation: Ukraine Alerts Map Team
- Enhanced features: AI Assistant Implementation
- Testing framework: Comprehensive test suite with 100% core coverage

## License

Part of the Ukraine Alerts Map project. See main LICENSE file for details.

---

*For the latest updates, check the [GitHub repository](https://github.com/yourusername/ua-alerts-map)*