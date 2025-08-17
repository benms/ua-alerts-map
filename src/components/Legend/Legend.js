import React, { useState } from 'react';
import './Legend.css';
import { ThreatType, ThreatMetadata } from '../../types/AlertTypes';

const Legend = ({
  language = 'uk',
  collapsible = true,
  defaultCollapsed = false,
  position = 'bottom-left'
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  // Legend items configuration
  const legendItems = [
    {
      type: 'alert',
      color: '#dc143c',
      icon: 'plane',
      label: language === 'uk' ? 'Повітряна тривога' : 'Air raid alert',
      description: language === 'uk' ? 'Активна повітряна тривога' : 'Active air raid alert'
    },
    {
      type: 'tactical',
      color: '#ff6b6b',
      icon: 'fighter-jet',
      label: language === 'uk' ? 'Активність тактичної авіації' : 'Tactical aviation activity',
      description: language === 'uk' ? 'Зафіксована активність ворожої авіації' : 'Enemy aviation activity detected'
    },
    {
      type: 'missiles',
      color: '#ff4444',
      icon: 'rocket',
      label: language === 'uk' ? 'Ракетна загроза' : 'Missile threat',
      description: language === 'uk' ? 'Загроза ракетного удару' : 'Missile strike threat'
    },
    {
      type: 'drones',
      color: '#ff8866',
      icon: 'drone',
      label: language === 'uk' ? 'Загроза застосування БпЛА' : 'UAV threat',
      description: language === 'uk' ? 'Безпілотні літальні апарати' : 'Unmanned aerial vehicles'
    },
    {
      type: 'artillery',
      color: '#ff9999',
      pattern: 'dotted',
      icon: 'explosion',
      label: language === 'uk' ? 'Загроза артобстрілу' : 'Artillery threat',
      description: language === 'uk' ? 'Можливий артилерійський обстріл' : 'Possible artillery shelling'
    },
    {
      type: 'chemical',
      color: '#9932cc',
      icon: 'biohazard',
      label: language === 'uk' ? 'Хімічна загроза' : 'Chemical threat',
      description: language === 'uk' ? 'Загроза хімічної атаки' : 'Chemical attack threat'
    },
    {
      type: 'nuclear',
      color: '#8b0000',
      icon: 'radiation',
      label: language === 'uk' ? 'Радіаційна загроза' : 'Radiation threat',
      description: language === 'uk' ? 'Підвищений радіаційний фон' : 'Elevated radiation levels'
    },
    {
      type: 'fighting',
      color: '#cd5c5c',
      pattern: 'striped',
      icon: 'shield-alt',
      label: language === 'uk' ? 'Загроза вуличних боїв' : 'Street fighting threat',
      description: language === 'uk' ? 'Можливі бойові дії' : 'Possible combat operations'
    },
    {
      type: 'clear',
      color: '#ffffff',
      border: '#e2e8f0',
      icon: 'check-circle',
      label: language === 'uk' ? 'Відбій тривоги' : 'All clear',
      description: language === 'uk' ? 'Немає активних загроз' : 'No active threats'
    }
  ];

  // Additional legend info
  const additionalInfo = [
    {
      type: 'duration',
      icon: 'clock',
      label: language === 'uk' ? 'Тривалість' : 'Duration',
      description: language === 'uk' ? 'д. - дні, год. - години, хв. - хвилини' : 'd. - days, h. - hours, m. - minutes'
    },
    {
      type: 'intensity',
      icon: 'signal',
      label: language === 'uk' ? 'Інтенсивність' : 'Intensity',
      description: language === 'uk' ? 'Яскравість кольору відображає рівень загрози' : 'Color brightness indicates threat level'
    }
  ];

  const toggleCollapse = () => {
    if (collapsible) {
      setIsCollapsed(!isCollapsed);
    }
  };

  const renderLegendItem = (item) => {
    return (
      <div key={item.type} className="legend-item" title={item.description}>
        <div className="legend-item-indicator">
          {item.pattern ? (
            <div
              className={`legend-color pattern-${item.pattern}`}
              style={{
                backgroundColor: item.pattern === 'dotted' ? 'transparent' : item.color,
                color: item.color,
                borderColor: item.border || item.color
              }}
            />
          ) : (
            <div
              className="legend-color"
              style={{
                backgroundColor: item.color,
                borderColor: item.border || item.color
              }}
            />
          )}
          {item.icon && (
            <div className="legend-icon" style={{ color: item.color !== '#ffffff' ? item.color : '#4a5568' }}>
              <i className={`fas fa-${item.icon}`}></i>
            </div>
          )}
        </div>
        <div className="legend-item-text">
          <div className="legend-label">{item.label}</div>
          {!isCollapsed && item.description && (
            <div className="legend-description">{item.description}</div>
          )}
        </div>
      </div>
    );
  };

  const renderAdditionalInfo = (info) => {
    return (
      <div key={info.type} className="legend-info-item">
        <div className="legend-info-icon">
          <i className={`fas fa-${info.icon}`}></i>
        </div>
        <div className="legend-info-text">
          <div className="legend-info-label">{info.label}</div>
          <div className="legend-info-description">{info.description}</div>
        </div>
      </div>
    );
  };

  return (
    <div className={`map-legend map-legend-${position} ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="legend-header" onClick={toggleCollapse}>
        <h4>{language === 'uk' ? 'Умовні позначення' : 'Legend'}</h4>
        {collapsible && (
          <button
            className="legend-toggle"
            aria-label={isCollapsed ? 'Expand legend' : 'Collapse legend'}
            aria-expanded={!isCollapsed}
          >
            <i className={`fas fa-chevron-${isCollapsed ? 'up' : 'down'}`}></i>
          </button>
        )}
      </div>

      <div className={`legend-content ${isCollapsed ? 'hidden' : ''}`}>
        <div className="legend-section">
          <h5 className="legend-section-title">
            {language === 'uk' ? 'Типи загроз' : 'Threat Types'}
          </h5>
          <div className="legend-items">
            {legendItems.map(renderLegendItem)}
          </div>
        </div>

        {!isCollapsed && (
          <div className="legend-section legend-info-section">
            <h5 className="legend-section-title">
              {language === 'uk' ? 'Додаткова інформація' : 'Additional Information'}
            </h5>
            <div className="legend-info-items">
              {additionalInfo.map(renderAdditionalInfo)}
            </div>
          </div>
        )}

        <div className="legend-footer">
          <div className="legend-timestamp">
            {language === 'uk' ? 'Оновлено:' : 'Updated:'} {new Date().toLocaleTimeString(language === 'uk' ? 'uk-UA' : 'en-US')}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Legend;
