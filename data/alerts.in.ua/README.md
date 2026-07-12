# alerts.in.ua reference data

Captured from the rendered `https://alerts.in.ua/?_=1764783051897` page on
2026-07-12. These files are reference inputs for improving this project; they
are not wired into the app.

| File | Contents | Best use here |
| --- | --- | --- |
| `locations.json` | 174 Ukrainian names: 26 oblasts, 45 raions, 65 hromadas, 38 cities | Search/autocomplete and consistent Ukrainian labels |
| `simplified-map.svg` | 32 map paths covering 27 oblast/city labels | Lightweight overview map or visual reference |
| `districts.svg` | 139 district paths, 136 district UIDs, oblast/raion/city metadata | Add raion-level drill-down and match compact alert location IDs |
| `ukraine-border.svg` | National outline | Clip/background layer |
| `active-alerts.msgpack` | Raw compact live-alert snapshot | Protocol/schema research only |
| `active-alerts.json` | The same snapshot decoded to readable JSON | Inspect fields and test data without a MessagePack dependency |

## Sources

- `locations.json`: `https://cdn.alerts.in.ua/assets/locations.json?v=5`
- `simplified-map.svg`: `https://cdn.alerts.in.ua/assets/maps/simplified.svg?v=4`
- `districts.svg`: `https://cdn.alerts.in.ua/assets/regions/v2/districts.svg?v=12`
- `ukraine-border.svg`: `https://cdn.alerts.in.ua/assets/maps/ua-border.svg`
- alert snapshot: `https://api.alerts.in.ua/v3/alerts/active.mp`

The exported district and border resources were SVG fragments. They are wrapped
in an `<svg viewBox="0 0 4961 3508">` root here so browsers can use them as
standalone images; their geometry and metadata are unchanged.

## Important API caveat

The compact alert response says it is private and may change at any time, and
directs integrators to `https://alerts.in.ua/api-request`. Use the included
alert files as a dated fixture only. Request public API access before replacing
the project's current status source.

The compact payload has top-level collections `alerts`, `pt`, `ta`, `fa`, and
`an`; short field names are undocumented. At capture time, `alerts` had 43
records spanning oblast (`o`), raion (`r`), hromada (`h`), and city (`c`)
locations. The SVG `data-uid` values are the clearest observed join point to
payload location IDs such as `luid`/`lruid`.

## Recommended first improvement

Use `locations.json` for names and `districts.svg` for raion drill-down while
keeping the current oblast GeoJSON renderer. Do not make production behavior
depend on the private compact feed.
