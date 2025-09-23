import 'leaflet/dist/leaflet.css';
import './App.css';
import { MapContainer, GeoJSON, Popup } from 'react-leaflet';
import * as alertsData from './data/alerts.json';
import { useEffect, useState } from 'react';
import { geoRegions } from './data/regions';
import * as countriesData from './data/countries.json';

// const copyRight = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const position = [48.7630002, 30.1807396];
const THEME_STORAGE_KEY = 'ua-alerts-map-theme';

const getStoredTheme = () => {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    return window.localStorage.getItem(THEME_STORAGE_KEY);
  } catch (error) {
    return null;
  }
};

const getPreferredTheme = () => {
  const storedTheme = getStoredTheme();
  if (storedTheme === 'light' || storedTheme === 'dark') {
    return storedTheme;
  }

  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  }

  return 'light';
};

function App() {
  const [ regions ] = useState(alertsData);
  const [ theme, setTheme ] = useState(getPreferredTheme);

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);

    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem(THEME_STORAGE_KEY, theme);
      } catch (error) {
        // Ignore persistence errors (e.g. disabled storage)
      }
    }
  }, [ theme ]);

  if (!regions || !regions.states) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading alert data...
      </div>
    );
  }

  const getAlertColor = (id) => {
    const state = regions.states?.[id];
    if (!state) return 'var(--alert-unknown-color)';
    return state.enabled ? 'var(--alert-active-color)' : 'var(--alert-inactive-color)';
  }

  const getTitle = (regionName) => {
    const data = regions.states?.[regionName];
    if (!data) return `${regionName} - No data available`;
    
    try {
      const dateStr = data.enabled ? data.enabled_at : data.disabled_at;
      if (!dateStr) return `${regionName} - No timestamp available`;
      
      const prefixStr = data.enabled ? 'Enabled at ' : 'Disabled at ';
      const date = new Date(dateStr);
      
      if (isNaN(date.getTime())) return `${regionName} - Invalid timestamp`;
      
      const year = date.getFullYear();
      const day = date.getDate();
      const month = date.toLocaleString('uk', { month: 'long' });
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');

      return `${regionName} ${prefixStr} ${hours}:${minutes} ${day} ${month} ${year}`;
    } catch (error) {
      return `${regionName} - Error loading data`;
    }
  }

  const countryHandler = (country, layer) => {
    const name = country.properties.ADMIN;
    layer.bindPopup(name);
  };

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  };

  const isDarkTheme = theme === 'dark';
  const toggleLabel = `Switch to ${isDarkTheme ? 'light' : 'dark'} theme`;

  return (
    <div className="app">
      <button
        type="button"
        className="theme-toggle"
        onClick={toggleTheme}
        aria-label={toggleLabel}
      >
        <span aria-hidden="true" className="theme-toggle__icon">
          {isDarkTheme ? '☀️' : '🌙'}
        </span>
        <span className="theme-toggle__label">
          {isDarkTheme ? 'Light theme' : 'Dark theme'}
        </span>
      </button>
      <MapContainer
        className="alerts-map"
        center={position}
        zoom={6.25}
        scrollWheelZoom>
        {/* <TileLayer
          attribution={copyRight}
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        /> */}
        <GeoJSON
          data={countriesData}
          color='var(--country-border-color)'
          weight={0.5}
          opacity={1}
          fillColor='var(--country-fill-color)'
          fillOpacity={0.25}
          onEachFeature={countryHandler}
        />
        {/* <TopoJson data={topoDataUa} color='yellow' opacity='1'/> */}
        { Object.keys(geoRegions).map((regionName) => (
          <GeoJSON
            key={regionName}
            data={geoRegions[regionName]}
            color={getAlertColor(regionName)}
            fillColor={getAlertColor(regionName)}
            fillOpacity={0.35}
            opacity={1}
            weight={1}
          >
            <Popup>
              {getTitle(regionName)}
            </Popup>
          </GeoJSON>
        )) }
      </MapContainer>
    </div>
  );
}

export default App;
