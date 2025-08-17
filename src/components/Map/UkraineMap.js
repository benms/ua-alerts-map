import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Tooltip, LayerGroup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { AlertData, ThreatMetadata, AlertUtils } from '../../types/AlertTypes';
import ThreatIndicators from './ThreatIndicators';
import RegionLabel from './RegionLabel';
import './UkraineMap.css';

// Map configuration
const MAP_CONFIG = {
  center: [48.3794, 31.1656], // Center of Ukraine
  zoom: 6,
  minZoom: 5,
  maxZoom: 10,
  bounds: [
    [44.0, 22.0], // Southwest
    [52.5, 40.5], // Northeast
  ],
};

// Style configuration for regions based on alert state
const getRegionStyle = (alertData, isHovered = false, isSelected = false) => {
  const baseStyle = {
    weight: 1,
    color: '#4a5568',
    dashArray: '',
    fillOpacity: 0.7,
  };

  if (!alertData || !alertData.isActive) {
    return {
      ...baseStyle,
      fillColor: '#ffffff',
      fillOpacity: isHovered ? 0.5 : 0.3,
      weight: isHovered ? 2 : 1,
    };
  }

  const color = alertData.getColor();
  const intensity = alertData.intensity;

  // Add pattern for specific threat types
  const primaryThreat = alertData.getPrimaryThreat();
  const threatMeta = primaryThreat ? ThreatMetadata[primaryThreat] : null;

  return {
    ...baseStyle,
    fillColor: color,
    fillOpacity: 0.5 + (intensity * 0.005), // Dynamic opacity based on intensity
    weight: alertData.isCritical() ? 3 : isHovered ? 2 : 1,
    color: alertData.isCritical() ? '#8b0000' : '#4a5568',
    dashArray: threatMeta?.pattern === 'dotted' ? '3' :
               threatMeta?.pattern === 'striped' ? '10, 5' : '',
  };
};

// Custom icon for threat indicators
const createThreatIcon = (threatType) => {
  const metadata = ThreatMetadata[threatType];
  if (!metadata) return null;

  return L.divIcon({
    html: `
      <div class="threat-icon threat-icon-${threatType}">
        <i class="fas fa-${metadata.icon}"></i>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    className: 'threat-marker',
  });
};

const UkraineMap = ({
  regions = [],
  alerts = {},
  onRegionClick,
  onRegionHover,
  selectedRegion,
  showLabels = true,
  showThreatIndicators = true,
  language = 'uk'
}) => {
  const [hoveredRegion, setHoveredRegion] = useState(null);
  const [mapInstance, setMapInstance] = useState(null);
  const [regionLayers, setRegionLayers] = useState({});

  // Process alert data
  const processedAlerts = useMemo(() => {
    const processed = {};
    Object.keys(alerts).forEach(regionId => {
      const alertData = new AlertData(alerts[regionId]);
      alertData.calculateDuration();
      alertData.calculateIntensity();
      processed[regionId] = alertData;
    });
    return processed;
  }, [alerts]);

  // Get critical alerts for priority display
  const criticalAlerts = useMemo(() => {
    return Object.values(processedAlerts)
      .filter(alert => alert.isActive && alert.isCritical())
      .sort((a, b) => b.intensity - a.intensity);
  }, [processedAlerts]);

  // Handle region interactions
  const onEachRegion = useCallback((feature, layer) => {
    const regionId = feature.properties.id || feature.properties.name;
    const regionName = feature.properties.name;

    // Store layer reference
    setRegionLayers(prev => ({ ...prev, [regionId]: layer }));

    // Set up event handlers
    layer.on({
      mouseover: (e) => {
        setHoveredRegion(regionId);
        if (onRegionHover) {
          onRegionHover(regionId, e);
        }

        // Update style on hover
        const alertData = processedAlerts[regionId];
        layer.setStyle(getRegionStyle(alertData, true, selectedRegion === regionId));

        // Bring to front if has alert
        if (alertData?.isActive) {
          layer.bringToFront();
        }
      },
      mouseout: (e) => {
        setHoveredRegion(null);
        if (onRegionHover) {
          onRegionHover(null, e);
        }

        // Reset style
        const alertData = processedAlerts[regionId];
        layer.setStyle(getRegionStyle(alertData, false, selectedRegion === regionId));
      },
      click: (e) => {
        if (onRegionClick) {
          onRegionClick(regionId, feature, e);
        }
      }
    });

    // Add tooltip with region info
    if (processedAlerts[regionId]?.isActive) {
      const alert = processedAlerts[regionId];
      const tooltipContent = `
        <div class="region-tooltip">
          <div class="region-name">${regionName}</div>
          ${alert.isActive ? `
            <div class="alert-info">
              <div class="alert-duration">${alert.getFormattedDuration()}</div>
              <div class="threat-types">
                ${alert.threatTypes.map(type =>
                  `<span class="threat-badge">${ThreatMetadata[type]?.label || type}</span>`
                ).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      `;

      layer.bindTooltip(tooltipContent, {
        permanent: false,
        direction: 'top',
        className: 'custom-tooltip',
      });
    }

    // Apply initial style
    const alertData = processedAlerts[regionId];
    layer.setStyle(getRegionStyle(alertData, false, selectedRegion === regionId));
  }, [processedAlerts, selectedRegion, onRegionClick, onRegionHover]);

  // Update region styles when alerts change
  useEffect(() => {
    Object.keys(regionLayers).forEach(regionId => {
      const layer = regionLayers[regionId];
      const alertData = processedAlerts[regionId];
      if (layer) {
        layer.setStyle(getRegionStyle(
          alertData,
          hoveredRegion === regionId,
          selectedRegion === regionId
        ));
      }
    });
  }, [processedAlerts, regionLayers, hoveredRegion, selectedRegion]);

  // Render region GeoJSON
  const renderRegion = (region) => {
    if (!region.geoJSON) return null;

    const regionId = region.id || region.name;
    const alertData = processedAlerts[regionId];

    return (
      <GeoJSON
        key={regionId}
        data={region.geoJSON}
        onEachFeature={onEachRegion}
        style={() => getRegionStyle(alertData, false, selectedRegion === regionId)}
      />
    );
  };

  // Render threat indicators for a region
  const renderThreatIndicators = (region) => {
    const regionId = region.id || region.name;
    const alertData = processedAlerts[regionId];

    if (!alertData?.isActive || !alertData.threatTypes.length) return null;
    if (!showThreatIndicators) return null;

    const primaryThreat = alertData.getPrimaryThreat();
    if (!primaryThreat) return null;

    const icon = createThreatIcon(primaryThreat);
    if (!icon) return null;

    // Get region center coordinates
    const center = region.center || calculateRegionCenter(region.geoJSON);
    if (!center) return null;

    return (
      <Marker
        key={`threat-${regionId}`}
        position={center}
        icon={icon}
        zIndexOffset={1000}
      />
    );
  };

  // Render region labels
  const renderRegionLabel = (region) => {
    if (!showLabels) return null;

    const regionId = region.id || region.name;
    const alertData = processedAlerts[regionId];

    // Only show labels for regions with active alerts
    if (!alertData?.isActive) return null;

    const center = region.center || calculateRegionCenter(region.geoJSON);
    if (!center) return null;

    return (
      <RegionLabel
        key={`label-${regionId}`}
        position={center}
        region={region}
        alertData={alertData}
        language={language}
      />
    );
  };

  // Calculate region center from GeoJSON
  const calculateRegionCenter = (geoJSON) => {
    if (!geoJSON) return null;

    try {
      const layer = L.geoJSON(geoJSON);
      const bounds = layer.getBounds();
      const center = bounds.getCenter();
      return [center.lat, center.lng];
    } catch (error) {
      console.error('Error calculating region center:', error);
      return null;
    }
  };

  // Pulse animation for critical alerts
  useEffect(() => {
    if (!mapInstance) return;

    criticalAlerts.forEach(alert => {
      const layer = regionLayers[alert.regionId];
      if (layer) {
        // Add pulse class for animation
        layer.getElement()?.classList.add('pulse-alert');
      }
    });

    return () => {
      // Cleanup animations
      Object.values(regionLayers).forEach(layer => {
        layer.getElement()?.classList.remove('pulse-alert');
      });
    };
  }, [criticalAlerts, regionLayers, mapInstance]);

  return (
    <div className="ukraine-map-container">
      <MapContainer
        center={MAP_CONFIG.center}
        zoom={MAP_CONFIG.zoom}
        minZoom={MAP_CONFIG.minZoom}
        maxZoom={MAP_CONFIG.maxZoom}
        bounds={MAP_CONFIG.bounds}
        maxBounds={MAP_CONFIG.bounds}
        maxBoundsViscosity={1.0}
        className="ukraine-map"
        whenCreated={setMapInstance}
      >
        {/* Base map tiles */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {/* Ukraine regions layer */}
        <LayerGroup>
          {regions.map(region => renderRegion(region))}
        </LayerGroup>

        {/* Threat indicators layer */}
        {showThreatIndicators && (
          <LayerGroup>
            {regions.map(region => renderThreatIndicators(region))}
          </LayerGroup>
        )}

        {/* Region labels layer */}
        {showLabels && (
          <LayerGroup>
            {regions.map(region => renderRegionLabel(region))}
          </LayerGroup>
        )}

        {/* Additional threat indicators component for complex visualizations */}
        {showThreatIndicators && (
          <ThreatIndicators
            alerts={processedAlerts}
            regions={regions}
            mapInstance={mapInstance}
          />
        )}
      </MapContainer>

      {/* Alert summary panel */}
      <div className="alert-summary">
        <div className="summary-header">
          <h3>Активні тривоги</h3>
          <span className="alert-count">
            {Object.values(processedAlerts).filter(a => a.isActive).length}
          </span>
        </div>
        {criticalAlerts.length > 0 && (
          <div className="critical-alerts">
            <h4>Критичні загрози:</h4>
            {criticalAlerts.slice(0, 3).map(alert => (
              <div key={alert.regionId} className="critical-alert-item">
                <span className="region-name">{alert.regionName}</span>
                <span className="duration">{alert.getFormattedDuration()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UkraineMap;
