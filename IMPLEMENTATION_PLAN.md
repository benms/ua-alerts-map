# Implementation Plan: Enhanced Ukraine Alerts Map

## Overview
Transform the current basic alert map into a sophisticated multi-state alert visualization system matching the alerts.in.ua design.

## Current State Analysis
- **Current**: Simple binary states (orange for alert, green for clear)
- **Target**: Multi-level alert system with duration tracking, threat type indicators, and enhanced visual design

## Phase 1: Data Model Enhancement (Days 1-2)

### 1.1 Alert State Types
Create new data structures to support multiple alert levels:

```javascript
// src/types/AlertTypes.js
const AlertLevel = {
  NONE: 'none',                    // White/clear regions
  AIR_RAID: 'air_raid',            // Red regions
  TACTICAL_AVIATION: 'tactical',    // With airplane icon
  BALLISTIC_THREAT: 'ballistic',   // With missile icon
  ARTILLERY: 'artillery',          // With explosion icon
  CHEMICAL_THREAT: 'chemical',     // With warning icon
  NUCLEAR_THREAT: 'nuclear'        // With radiation icon
};

const AlertData = {
  regionId: 'string',
  regionName: 'string',
  alertLevel: 'AlertLevel',
  threatTypes: ['array of active threats'],
  startTime: 'ISO timestamp',
  duration: {
    days: 'number',
    hours: 'number',
    minutes: 'number'
  },
  intensity: 'number (0-100)', // For color gradation
  subRegions: ['affected sub-regions']
};
```

### 1.2 Update Data Pipeline
Modify `server/download_regions.py` to fetch enhanced alert data:
- Add threat type parsing
- Calculate duration from timestamps
- Support sub-regional alerts
- Add intensity calculation based on threat severity

## Phase 2: Visual Design System (Days 3-4)

### 2.1 Color Palette
```css
:root {
  /* Alert levels */
  --alert-none: #ffffff;
  --alert-low: #ffcccb;      /* Light pink */
  --alert-medium: #ff6b6b;   /* Medium red */
  --alert-high: #dc143c;     /* Crimson */
  --alert-critical: #8b0000;  /* Dark red */
  
  /* Region states */
  --region-border: #4a5568;
  --region-hover: rgba(0,0,0,0.1);
  --region-selected: rgba(0,0,0,0.2);
  
  /* Text colors */
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --text-alert: #ffffff;
}
```

### 2.2 Icon System
Implement threat type indicators:
```javascript
// src/components/ThreatIcons.js
- Airplane icon for air threats
- Missile icon for ballistic threats
- Explosion icon for artillery
- Warning triangle for chemical threats
- Radiation symbol for nuclear threats
```

## Phase 3: Map Component Refactoring (Days 5-7)

### 3.1 Enhanced Region Rendering
```javascript
// src/components/UkraineMap.js
function getRegionStyle(alertData) {
  return {
    fillColor: getAlertColor(alertData.intensity),
    fillOpacity: 0.7 + (alertData.intensity * 0.003),
    weight: alertData.alertLevel !== 'none' ? 2 : 1,
    color: '#4a5568',
    dashArray: alertData.subRegions.length > 0 ? '3' : '',
  };
}
```

### 3.2 Region Labels with Duration
```javascript
// src/components/RegionLabel.js
<div className="region-label">
  <div className="region-name">{region.name}</div>
  {alert.duration && (
    <div className="alert-duration">
      {alert.duration.days} д. {alert.duration.hours} год.
    </div>
  )}
</div>
```

### 3.3 Threat Indicators Overlay
```javascript
// src/components/ThreatIndicators.js
function renderThreatIcons(region, threats) {
  return threats.map(threat => (
    <L.Marker 
      position={getRegionCenter(region)}
      icon={getThreatIcon(threat)}
      zIndexOffset={1000}
    />
  ));
}
```

## Phase 4: Legend Component (Days 8-9)

### 4.1 Dynamic Legend
```javascript
// src/components/Legend.js
const LegendItems = [
  { 
    color: '#dc143c', 
    label: 'Повітряна тривога',
    icon: 'airplane'
  },
  { 
    color: '#ff6b6b', 
    label: 'Активність тактичної авіації',
    icon: 'fighter-jet'
  },
  { 
    color: '#ffcccb', 
    label: 'Загроза застосування БпЛА',
    icon: 'drone'
  },
  { 
    pattern: 'dotted', 
    label: 'Загроза артобстрілу',
    icon: 'explosion'
  },
  { 
    pattern: 'striped', 
    label: 'Загроза вуличних боїв',
    icon: 'warning'
  },
  { 
    pattern: 'hashed', 
    label: 'Потенційні загрози',
    icon: 'info'
  }
];
```

## Phase 5: Real-time Updates (Days 10-11)

### 5.1 WebSocket Integration
```javascript
// src/services/AlertService.js
class AlertService {
  constructor() {
    this.ws = new WebSocket('wss://alerts.in.ua/ws');
  }
  
  subscribeToAlerts(callback) {
    this.ws.on('alert-update', (data) => {
      callback(parseAlertData(data));
    });
  }
}
```

### 5.2 Alert Transitions
```javascript
// src/hooks/useAlertTransitions.js
function useAlertTransitions(alerts) {
  // Smooth color transitions
  // Pulse effect for new alerts
  // Fade out for cleared alerts
}
```

## Phase 6: Enhanced Features (Days 12-14)

### 6.1 Alert History Timeline
- Show alert progression over time
- Duration statistics per region
- Historical threat patterns

### 6.2 Region Details Panel
```javascript
// src/components/RegionDetails.js
- Current alert status
- Active threat types with icons
- Alert duration counter
- Sub-regional breakdown
- Recent alert history
```

### 6.3 Alert Notifications
- Browser notifications for new alerts
- Sound alerts (optional)
- Alert severity-based notifications

## Phase 7: Performance Optimization (Days 15-16)

### 7.1 Map Rendering
- Use React.memo for region components
- Implement viewport-based rendering
- Optimize GeoJSON loading

### 7.2 Data Management
```javascript
// src/hooks/useAlertData.js
- Implement data caching
- Use SWR for smart refetching
- Batch updates for multiple regions
```

## Phase 8: Testing & Deployment (Days 17-18)

### 8.1 Testing Suite
```javascript
// src/__tests__/
- Alert state transitions
- Duration calculations
- Icon rendering
- Legend accuracy
- Real-time update handling
```

### 8.2 Build Optimization
```bash
# package.json updates
- Code splitting for map components
- Lazy load heavy dependencies
- Optimize bundle size
```

## Technical Stack Updates

### Dependencies to Add
```json
{
  "dependencies": {
    "@fortawesome/react-fontawesome": "^0.2.0",  // For threat icons
    "date-fns": "^2.30.0",                       // Duration calculations
    "classnames": "^2.3.2",                      // Dynamic styling
    "framer-motion": "^10.16.0",                 // Animations
    "socket.io-client": "^4.5.0"                 // WebSocket support
  }
}
```

## File Structure
```
src/
├── components/
│   ├── Map/
│   │   ├── UkraineMap.js
│   │   ├── RegionLayer.js
│   │   ├── ThreatIndicators.js
│   │   └── RegionLabel.js
│   ├── Legend/
│   │   ├── Legend.js
│   │   └── LegendItem.js
│   ├── Panel/
│   │   ├── RegionDetails.js
│   │   └── AlertHistory.js
│   └── Icons/
│       └── ThreatIcons.js
├── hooks/
│   ├── useAlertData.js
│   ├── useAlertTransitions.js
│   └── useWebSocket.js
├── services/
│   ├── AlertService.js
│   └── RegionService.js
├── utils/
│   ├── alertHelpers.js
│   ├── colorHelpers.js
│   └── durationHelpers.js
└── styles/
    ├── alerts.css
    ├── map.css
    └── legend.css
```

## Implementation Timeline

### Week 1 (Days 1-7)
- ✅ Data model enhancement
- ✅ Visual design system
- ✅ Map component refactoring

### Week 2 (Days 8-14)
- ✅ Legend component
- ✅ Real-time updates
- ✅ Enhanced features

### Week 3 (Days 15-18)
- ✅ Performance optimization
- ✅ Testing
- ✅ Deployment preparation

## Success Metrics
- [ ] All region states accurately displayed
- [ ] Alert durations calculated correctly
- [ ] Threat icons rendered appropriately
- [ ] Legend matches all possible states
- [ ] Real-time updates within 1 second
- [ ] Page load time < 3 seconds
- [ ] Mobile responsive design
- [ ] Accessibility compliance (WCAG 2.1 AA)

## Next Steps
1. Review and approve implementation plan
2. Set up development branch
3. Begin Phase 1 implementation
4. Daily progress reviews
5. User testing after each phase