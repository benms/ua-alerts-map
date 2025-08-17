/**
 * Alert Types and Data Structures for Ukraine Alerts Map
 * Defines the various alert levels, threat types, and data models
 */

// Alert severity levels
export const AlertLevel = {
  NONE: 'none',                    // No active alerts (white regions)
  LOW: 'low',                      // Low-level threat (light pink)
  MEDIUM: 'medium',                // Medium threat (medium red)
  HIGH: 'high',                    // High threat (crimson)
  CRITICAL: 'critical',            // Critical threat (dark red)
  AIR_RAID: 'air_raid',           // Active air raid alert
  TACTICAL_AVIATION: 'tactical',   // Tactical aviation activity
  BALLISTIC: 'ballistic',          // Ballistic missile threat
};

// Types of threats that can be active
export const ThreatType = {
  AIR_RAID: 'air_raid',
  TACTICAL_AVIATION: 'tactical_aviation',
  CRUISE_MISSILES: 'cruise_missiles',
  BALLISTIC_MISSILES: 'ballistic_missiles',
  DRONES: 'drones',
  ARTILLERY: 'artillery',
  CHEMICAL: 'chemical',
  NUCLEAR: 'nuclear',
  STREET_FIGHTING: 'street_fighting',
};

// Threat type metadata for UI display
export const ThreatMetadata = {
  [ThreatType.AIR_RAID]: {
    icon: 'plane',
    label: 'Повітряна тривога',
    color: '#dc143c',
    priority: 10,
  },
  [ThreatType.TACTICAL_AVIATION]: {
    icon: 'fighter-jet',
    label: 'Активність тактичної авіації',
    color: '#ff6b6b',
    priority: 8,
  },
  [ThreatType.CRUISE_MISSILES]: {
    icon: 'rocket',
    label: 'Крилаті ракети',
    color: '#ff4444',
    priority: 9,
  },
  [ThreatType.BALLISTIC_MISSILES]: {
    icon: 'missile',
    label: 'Балістичні ракети',
    color: '#cc0000',
    priority: 10,
  },
  [ThreatType.DRONES]: {
    icon: 'drone',
    label: 'Загроза застосування БпЛА',
    color: '#ff8866',
    priority: 6,
  },
  [ThreatType.ARTILLERY]: {
    icon: 'explosion',
    label: 'Загроза артобстрілу',
    color: '#ff9999',
    priority: 7,
    pattern: 'dotted',
  },
  [ThreatType.CHEMICAL]: {
    icon: 'biohazard',
    label: 'Хімічна загроза',
    color: '#9932cc',
    priority: 9,
  },
  [ThreatType.NUCLEAR]: {
    icon: 'radiation',
    label: 'Радіаційна загроза',
    color: '#8b0000',
    priority: 10,
  },
  [ThreatType.STREET_FIGHTING]: {
    icon: 'shield-alt',
    label: 'Загроза вуличних боїв',
    color: '#cd5c5c',
    priority: 5,
    pattern: 'striped',
  },
};

// Alert data structure for a region
export class AlertData {
  constructor(data = {}) {
    this.regionId = data.regionId || '';
    this.regionName = data.regionName || '';
    this.regionNameEn = data.regionNameEn || '';
    this.alertLevel = data.alertLevel || AlertLevel.NONE;
    this.threatTypes = data.threatTypes || [];
    this.startTime = data.startTime || null;
    this.endTime = data.endTime || null;
    this.duration = data.duration || { days: 0, hours: 0, minutes: 0 };
    this.intensity = data.intensity || 0; // 0-100 scale
    this.subRegions = data.subRegions || [];
    this.isActive = data.isActive !== undefined ? data.isActive : false;
    this.lastUpdated = data.lastUpdated || new Date().toISOString();
  }

  // Calculate duration from start time
  calculateDuration() {
    if (!this.startTime) return { days: 0, hours: 0, minutes: 0 };

    const start = new Date(this.startTime);
    const now = this.endTime ? new Date(this.endTime) : new Date();
    const diff = now - start;

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    this.duration = { days, hours, minutes };
    return this.duration;
  }

  // Get formatted duration string
  getFormattedDuration() {
    const { days, hours, minutes } = this.duration;
    if (days > 0) {
      return `${days} д. ${hours} год.`;
    } else if (hours > 0) {
      return `${hours} год. ${minutes} хв.`;
    } else {
      return `${minutes} хв.`;
    }
  }

  // Calculate intensity based on threat types and duration
  calculateIntensity() {
    let intensity = 0;

    // Base intensity from threat types
    this.threatTypes.forEach(threat => {
      const metadata = ThreatMetadata[threat];
      if (metadata) {
        intensity += metadata.priority * 10;
      }
    });

    // Increase intensity based on duration
    const { days, hours } = this.duration;
    const durationHours = days * 24 + hours;
    if (durationHours > 72) intensity += 20;
    else if (durationHours > 24) intensity += 10;
    else if (durationHours > 6) intensity += 5;

    // Cap at 100
    this.intensity = Math.min(intensity, 100);
    return this.intensity;
  }

  // Get the highest priority threat type
  getPrimaryThreat() {
    if (this.threatTypes.length === 0) return null;

    return this.threatTypes.reduce((primary, current) => {
      const primaryMeta = ThreatMetadata[primary];
      const currentMeta = ThreatMetadata[current];
      return (currentMeta?.priority || 0) > (primaryMeta?.priority || 0)
        ? current
        : primary;
    }, this.threatTypes[0]);
  }

  // Get color based on alert level and intensity
  getColor() {
    if (this.alertLevel === AlertLevel.NONE) {
      return '#ffffff';
    }

    const primaryThreat = this.getPrimaryThreat();
    if (primaryThreat && ThreatMetadata[primaryThreat]) {
      return ThreatMetadata[primaryThreat].color;
    }

    // Fallback to intensity-based color
    const intensity = this.intensity;
    if (intensity > 80) return '#8b0000'; // Dark red
    if (intensity > 60) return '#dc143c'; // Crimson
    if (intensity > 40) return '#ff6b6b'; // Medium red
    if (intensity > 20) return '#ffcccb'; // Light pink
    return '#ffe0e0'; // Very light pink
  }

  // Check if alert is critical
  isCritical() {
    return this.alertLevel === AlertLevel.CRITICAL ||
           this.threatTypes.includes(ThreatType.BALLISTIC_MISSILES) ||
           this.threatTypes.includes(ThreatType.NUCLEAR);
  }

  // Convert to JSON
  toJSON() {
    return {
      regionId: this.regionId,
      regionName: this.regionName,
      regionNameEn: this.regionNameEn,
      alertLevel: this.alertLevel,
      threatTypes: this.threatTypes,
      startTime: this.startTime,
      endTime: this.endTime,
      duration: this.duration,
      intensity: this.intensity,
      subRegions: this.subRegions,
      isActive: this.isActive,
      lastUpdated: this.lastUpdated,
    };
  }

  // Create from JSON
  static fromJSON(json) {
    return new AlertData(json);
  }
}

// Region data structure
export class RegionData {
  constructor(data = {}) {
    this.id = data.id || '';
    this.name = data.name || '';
    this.nameEn = data.nameEn || '';
    this.center = data.center || [0, 0]; // [lat, lng]
    this.bounds = data.bounds || null;
    this.population = data.population || 0;
    this.area = data.area || 0;
    this.type = data.type || 'oblast'; // oblast, city, raion
    this.parentId = data.parentId || null;
    this.geoJSON = data.geoJSON || null;
  }

  // Check if point is within region bounds
  containsPoint(lat, lng) {
    if (!this.bounds) return false;
    const [minLat, minLng, maxLat, maxLng] = this.bounds;
    return lat >= minLat && lat <= maxLat && lng >= minLng && lng <= maxLng;
  }

  // Get region display name
  getDisplayName(language = 'uk') {
    return language === 'en' ? this.nameEn : this.name;
  }
}

// Alert history entry
export class AlertHistoryEntry {
  constructor(data = {}) {
    this.id = data.id || Date.now().toString();
    this.regionId = data.regionId || '';
    this.alertLevel = data.alertLevel || AlertLevel.NONE;
    this.threatTypes = data.threatTypes || [];
    this.startTime = data.startTime || new Date().toISOString();
    this.endTime = data.endTime || null;
    this.duration = data.duration || null;
    this.maxIntensity = data.maxIntensity || 0;
  }

  // Check if this entry is currently active
  isActive() {
    return !this.endTime;
  }

  // Calculate total duration in minutes
  getTotalMinutes() {
    if (!this.duration) return 0;
    const { days, hours, minutes } = this.duration;
    return days * 24 * 60 + hours * 60 + minutes;
  }
}

// Export utility functions
export const AlertUtils = {
  // Get alert level from intensity
  getAlertLevelFromIntensity(intensity) {
    if (intensity === 0) return AlertLevel.NONE;
    if (intensity < 20) return AlertLevel.LOW;
    if (intensity < 40) return AlertLevel.MEDIUM;
    if (intensity < 70) return AlertLevel.HIGH;
    return AlertLevel.CRITICAL;
  },

  // Sort regions by alert priority
  sortByAlertPriority(regions) {
    return regions.sort((a, b) => {
      // Critical alerts first
      if (a.isCritical() && !b.isCritical()) return -1;
      if (!a.isCritical() && b.isCritical()) return 1;

      // Then by intensity
      if (a.intensity !== b.intensity) {
        return b.intensity - a.intensity;
      }

      // Then by duration
      const aDuration = a.getTotalMinutes();
      const bDuration = b.getTotalMinutes();
      return bDuration - aDuration;
    });
  },

  // Merge alert data updates
  mergeAlertData(existing, update) {
    const merged = new AlertData(existing);

    // Update fields
    Object.keys(update).forEach(key => {
      if (update[key] !== undefined && update[key] !== null) {
        merged[key] = update[key];
      }
    });

    // Recalculate derived fields
    merged.calculateDuration();
    merged.calculateIntensity();

    return merged;
  },

  // Check if alert requires immediate attention
  requiresImmediateAttention(alert) {
    return alert.isCritical() ||
           alert.threatTypes.includes(ThreatType.BALLISTIC_MISSILES) ||
           alert.threatTypes.includes(ThreatType.CRUISE_MISSILES);
  },
};

export default {
  AlertLevel,
  ThreatType,
  ThreatMetadata,
  AlertData,
  RegionData,
  AlertHistoryEntry,
  AlertUtils,
};
