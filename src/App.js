import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';
import './App.css';
import * as alertsData from './data/alerts.json';
import { useState } from 'react';
import { geoRegions } from './data/regions';

const copyRight = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const position = [48.7630002, 30.1807396];

function App() {
  const [ regions ] = useState(alertsData);

  const getAlertColor = (id) => {
    return regions.states[id].enabled ? 'orange' : 'green';
  }

  const getTitle = (regionName) => {
    const data = regions.states[regionName];
    const dateStr = data.enabled ? data.enabled_at : data.disabled_at;
    const prefixStr = data.enabled ? '{regionName} Enabled at ' : 'Disabled at ';
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const day = date.getDate();
    const month = date.getMonth();
    const hours = date.getHours();
    const minutes = date.getMinutes();

    return `${regionName} ${prefixStr} ${hours}:${minutes} ${day} ${month} ${year}`;
  }

  return (
    <MapContainer center={position} zoom={6.25} scrollWheelZoom={true}>
      <TileLayer
        attribution={copyRight}
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      { Object.keys(geoRegions).map((regionName) => (
        <GeoJSON key={regionName} data={geoRegions[regionName]} color={getAlertColor(regionName)} opacity="1">
          <Popup>
            {getTitle(regionName)}
          </Popup>
        </GeoJSON>
      )) }
    </MapContainer>
  );
}

export default App;
