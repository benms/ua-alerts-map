# Мапа повітряних тривог України

React/Leaflet map that colors Ukrainian regions from the latest downloaded
alert-status snapshot.

## Run locally

```sh
python3 download_regions.py
npm install
npm start
```

`download_regions.py` creates the ignored GeoJSON and alert files required by
the build. Refresh them before building a new deployment:

```sh
python3 download_regions.py
npm run build
```

Reference data collected from alerts.in.ua, including district-level geometry,
is documented in [`data/alerts.in.ua/README.md`](data/alerts.in.ua/README.md).

The current status source is a downloaded snapshot, not a live browser request.
Do not connect the private compact alerts.in.ua endpoint directly; request its
public API access first.
