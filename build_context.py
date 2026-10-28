"""Current-conditions layers for the Field Sample Comparison map (docs/index.html).

  docs/data/phenocams.json   active PhenoCam Network vegetation cameras (latest image within 60 days)
  docs/data/usdm.geojson     current U.S. Drought Monitor, simplified for the web
  docs/data/cameras.geojson  ALERTCalifornia + PhenoCam cameras as flat points for the AGOL web map
                             (image links always point at each camera's latest picture)

ALERTCalifornia cameras and the CA drought outlook (UC Irvine MSDI/SPI, from the ca-rx-planner repo)
are read live by the page itself, since those sources allow it. PhenoCam and the full-size Drought
Monitor file can't be used directly from the page, so this script saves copies. Each part is
optional: if a source is down, its previous file is kept and the rest still runs."""
import json
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'docs' / 'data'
UA = {'User-Agent': 'AppFuelSample (github.com/shelikes2run/AppFuelSample)'}
VEG = {'AG': 'Agriculture', 'DB': 'Deciduous broadleaf', 'DN': 'Deciduous needleleaf', 'EB': 'Evergreen broadleaf',
       'EN': 'Evergreen needleleaf', 'GR': 'Grassland', 'SH': 'Shrubland', 'TN': 'Tundra', 'WL': 'Wetland',
       'NV': 'Non-vegetated', 'UN': 'Understory', 'MX': 'Mixed forest'}
USDM = {0: 'D0 Abnormally dry', 1: 'D1 Moderate drought', 2: 'D2 Severe drought', 3: 'D3 Extreme drought', 4: 'D4 Exceptional drought'}


def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return json.load(r)


def phenocams():
    cutoff = (date.today() - timedelta(days=60)).isoformat()
    url, rows = 'https://phenocam.nau.edu/api/cameras/?format=json&limit=500', []
    while url:
        d = get(url)
        for c in d['results']:
            m = c.get('sitemetadata') or {}
            if not c.get('active') or (c.get('date_last') or '') < cutoff or c.get('Lat') is None:
                continue
            rows.append({'site': c['Sitename'], 'lat': round(c['Lat'], 5), 'lon': round(c['Lon'], 5), 'elev': c.get('Elev'),
                         'veg': VEG.get(m.get('primary_veg_type') or '', m.get('primary_veg_type') or ''),
                         'species': m.get('dominant_species') or '', 'desc': (m.get('site_description') or '')[:160],
                         'last': c.get('date_last')})
        url = d.get('next')
    (OUT / 'phenocams.json').write_text(json.dumps({'generated': date.today().isoformat(), 'cameras': rows}, separators=(',', ':')))
    print(f'phenocams: {len(rows)} active')


def cameras():
    feats = []
    ac = 'https://cameras.alertcalifornia.org/public-camera-data/'
    for f in get(ac + 'all_cameras-v3.json')['features']:
        p, (lon, lat) = f['properties'], f['geometry']['coordinates'][:2]
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(lon, 5), round(lat, 5)]},
                      'properties': {'source': 'ALERTCalifornia', 'cam_id': p['id'], 'name': p['name'],
                                     'area': (p.get('county') or '').title() + ' Co., ' + (p.get('state') or ''),
                                     'veg': '', 'img': f"{ac}{p['id']}/latest-thumb.jpg", 'full': f"{ac}{p['id']}/latest-frame.jpg",
                                     'page': 'https://cameras.alertcalifornia.org/', 'updated': 'Every few minutes'}})
    pc = 'https://phenocam.nau.edu'
    for c in json.loads((OUT / 'phenocams.json').read_text())['cameras']:
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [c['lon'], c['lat']]},
                      'properties': {'source': 'PhenoCam', 'cam_id': c['site'], 'name': c['site'], 'area': c['desc'],
                                     'veg': c['veg'] + (' (' + c['species'] + ')' if c['species'] else ''),
                                     'img': f"{pc}/data/latest/{c['site']}.jpg", 'full': f"{pc}/data/latest/{c['site']}.jpg",
                                     'page': f"{pc}/webcam/sites/{c['site']}/", 'updated': 'Daily, latest ' + c['last']}})
    (OUT / 'cameras.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}, separators=(',', ':')))
    print(f'cameras: {len(feats)}')


def usdm():
    from shapely.geometry import mapping, shape
    d = get('https://droughtmonitor.unl.edu/data/json/usdm_current.json', timeout=300)
    feats = []
    for f in d['features']:
        p = f['properties']
        dm = p.get('DM', p.get('dm'))
        g = shape(f['geometry']).simplify(0.01, preserve_topology=True)
        if g.is_empty:
            continue
        gj = json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), 3))
        feats.append({'type': 'Feature', 'properties': {'dm': int(dm), 'label': USDM.get(int(dm), f'D{dm}')}, 'geometry': gj})
    t = date.today()                              # maps release Thursdays, valid the Tuesday before
    vd = (t - timedelta(days=(t.weekday() - 3) % 7) - timedelta(days=2)).isoformat()
    out = {'type': 'FeatureCollection', 'metadata': {'source': 'U.S. Drought Monitor (droughtmonitor.unl.edu)', 'valid': vd,
                                                     'fetched': date.today().isoformat()}, 'features': feats}
    (OUT / 'usdm.geojson').write_text(json.dumps(out, separators=(',', ':')))
    print(f'usdm: {len(feats)} polygons, valid {vd}, {(OUT / "usdm.geojson").stat().st_size // 1024} KB')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (phenocams, cameras, usdm):
        try:
            fn()
        except Exception as e:  # keep the last good file
            print(f'{fn.__name__}: skipped ({e})', file=sys.stderr)
