"""Data for the Field Sample Comparison page (docs/index.html), from the two FEMS sample CSVs.

  docs/data/index.json        sites (id, name, samples, fuel types, years), fuel types, categories, years
  docs/data/all.json          all sites combined: per fuel type x category x year x half-month  [sum, n, min, max]
  docs/data/sites/<id>.json   one site's samples: [date, fuel type #, category #, value]
Run after fetch_fuel_samples.py (the daily workflow does both)."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs' / 'data'


def main():
    df = pd.concat([pd.read_csv(ROOT / f) for f in ('field_samples_2005_2014.csv', 'field_samples_2015_present.csv')], ignore_index=True)
    df['dt'] = pd.to_datetime(df['Date-Time'], errors='coerce', utc=True).dt.tz_localize(None)
    df = df.dropna(subset=['dt', 'Sample Avg Value']).drop_duplicates('Sample Id')
    df['Fuel Type'] = df['Fuel Type'].fillna('Unknown').astype(str)
    df['Category'] = df['Category'].fillna('Unknown').astype(str)
    fuels = sorted(df['Fuel Type'].unique())
    cats = sorted(df['Category'].unique())
    fi, ci = {f: i for i, f in enumerate(fuels)}, {c: i for i, c in enumerate(cats)}
    df['y'] = df['dt'].dt.year
    df['hm'] = (df['dt'].dt.month - 1) * 2 + (df['dt'].dt.day >= 15).astype(int)      # 0..23: 1st / 15th of each month
    df['f'] = df['Fuel Type'].map(fi)
    df['c'] = df['Category'].map(ci)
    (OUT / 'sites').mkdir(parents=True, exist_ok=True)
    sites = []
    for sid, g in df.groupby('SiteId'):
        g = g.sort_values('dt')
        rows = [[d.strftime('%Y-%m-%d'), int(f), int(c), round(float(v), 1)] for d, f, c, v in zip(g['dt'], g['f'], g['c'], g['Sample Avg Value'])]
        (OUT / 'sites' / f'{int(sid)}.json').write_text(json.dumps(rows, separators=(',', ':')))
        sites.append({'id': int(sid), 'name': str(g['Site Name'].dropna().iloc[-1]) if g['Site Name'].notna().any() else str(sid),
                      'n': len(g), 'fuels': sorted(int(x) for x in g['f'].unique()), 'cats': sorted(int(x) for x in g['c'].unique()),
                      'first': int(g['y'].min()), 'last': int(g['y'].max())})
    agg = df.groupby(['f', 'c', 'y', 'hm'])['Sample Avg Value'].agg(['sum', 'count', 'min', 'max']).reset_index()
    (OUT / 'all.json').write_text(json.dumps([[int(r.f), int(r.c), int(r.y), int(r.hm), round(float(r['sum']), 1), int(r['count']),
                                               round(float(r['min']), 1), round(float(r['max']), 1)] for _, r in agg.iterrows()], separators=(',', ':')))
    (OUT / 'index.json').write_text(json.dumps({
        'generated': pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M UTC'), 'samples': len(df),
        'first': df['dt'].min().strftime('%Y-%m-%d'), 'last': df['dt'].max().strftime('%Y-%m-%d'),
        'fuels': fuels, 'cats': cats, 'years': sorted(int(y) for y in df['y'].unique()),
        'sites': sorted(sites, key=lambda s: s['name'].lower())}, separators=(',', ':')))
    print(f'{len(df)} samples, {len(sites)} sites, {len(fuels)} fuel types → {OUT}')


if __name__ == '__main__':
    main()
