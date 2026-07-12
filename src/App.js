import 'leaflet/dist/leaflet.css';
import './App.css';
import { MapContainer, GeoJSON, Popup } from 'react-leaflet';
import alertsData from './data/alerts.json';
import { geoRegions } from './data/regions';

const position = [48.7630002, 30.1807396];
const colors = { active: '#dc2626', inactive: '#15803d', unknown: '#64748b' };
const dateFormat = new Intl.DateTimeFormat('uk-UA', {
  dateStyle: 'long',
  timeStyle: 'short'
});

function getAlertColor(regionName) {
  const state = alertsData.states?.[regionName];
  return state ? colors[state.enabled ? 'active' : 'inactive'] : colors.unknown;
}

function getTitle(regionName) {
  const state = alertsData.states?.[regionName];
  if (!state) return `${regionName}: дані відсутні`;

  const timestamp = state.enabled ? state.enabled_at : state.disabled_at;
  const date = timestamp && new Date(timestamp);
  if (!date || Number.isNaN(date.getTime())) return `${regionName}: час не вказано`;

  return `${regionName}: ${state.enabled ? 'тривога з' : 'відбій о'} ${dateFormat.format(date)}`;
}

function App() {
  const regionNames = Object.keys(geoRegions);
  const activeCount = regionNames.filter(name => alertsData.states?.[name]?.enabled).length;

  return (
    <main className="app">
      <section className="status-panel" aria-label="Стан повітряних тривог">
        <h1>Мапа повітряних тривог</h1>
        <p><strong>{activeCount}</strong> з {regionNames.length} регіонів зараз у тривозі</p>
        <div className="legend" aria-label="Умовні позначення">
          <span><i style={{ background: colors.active }} />Тривога</span>
          <span><i style={{ background: colors.inactive }} />Немає тривоги</span>
          <span><i style={{ background: colors.unknown }} />Немає даних</span>
        </div>
      </section>

      <MapContainer center={position} zoom={6.25} scrollWheelZoom>
        {regionNames.map(regionName => (
          <GeoJSON
            key={regionName}
            data={geoRegions[regionName]}
            pathOptions={{
              color: '#fff',
              fillColor: getAlertColor(regionName),
              fillOpacity: 0.82,
              weight: 1
            }}
          >
            <Popup>{getTitle(regionName)}</Popup>
          </GeoJSON>
        ))}
      </MapContainer>
    </main>
  );
}

export default App;
