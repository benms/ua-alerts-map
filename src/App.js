import 'leaflet/dist/leaflet.css';
import './App.css';
import { MapContainer, GeoJSON, Popup } from 'react-leaflet';
import * as alertsData from './data/alerts.json';
import { useState } from 'react';
import { geoRegions } from './data/regions';
import * as countriesData from './data/countries.json';

// const copyRight = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const position = [48.7630002, 30.1807396];

function App() {
  const [ regions ] = useState(alertsData);

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
    if (!state) return 'gray';
    return state.enabled ? 'orange' : 'green';
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

  return (
    <MapContainer
      style={{backgroundColor: 'white'}}
      center={position}
      zoom={6.25}
      scrollWheelZoom>
      {/* <TileLayer
        attribution={copyRight}
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      /> */}
      <GeoJSON
        data={countriesData}
        color='black'
        weight={0.5}
        opacity={1}
        fillColor='gray'
        fillOpacity={0.2}
        onEachFeature={countryHandler}
        />
       {/* <TopoJson data={topoDataUa} color='yellow' opacity='1'/> */}
      { Object.keys(geoRegions).map((regionName) => (
        <GeoJSON
          key={regionName}
          data={geoRegions[regionName]}
          color={getAlertColor(regionName)}
          opacity={1}
          weight={1}
          >
          <Popup>
            {getTitle(regionName)}
          </Popup>
        </GeoJSON>
      )) }
    </MapContainer>
  );
}

export default App;
