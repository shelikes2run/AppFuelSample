# Field Sample Comparison

Compares this year's fuel moisture field samples (FEMS / NFMD) with each site's history, by fuel type and category.

- Web page: https://shelikes2run.github.io/AppFuelSample/ (GitHub Pages, `docs/index.html`)
- ArcGIS Online app: **Field Sample Comparison** (Experience Builder, NIFC org). Its map (web map
  *Field Sample Sites & Current Conditions*) picks the site; the page is embedded on the right with `?embed=1&site=<id>`.

## Features

- Filter by site, fuel type, category, current year, historical years and months
- This year against the historical average, minimum and maximum, by half-month (1st and 15th)
- Export the filtered data (CSV), all charts (PDF) or one chart (PNG)
- Map of every sample site, colored by its latest sample
- Current conditions for the picked site: nearby live cameras and drought (below)

## Data (updated daily, no keys needed)

The workflow `.github/workflows/update_fuel_data_daily.yml` runs every day:

1. `fetch_fuel_samples.py`: the FEMS field samples (`field_samples_2015_present.csv`) and site list (`site_metadata.csv`)
2. `build_web.py`: the page's data in `docs/data/` (sites, combined summary, one file per site, `sites.geojson`)
3. `build_context.py`: cameras and drought (below)

## Cameras and drought

- **ALERTCalifornia cameras** (UC San Diego, CA). The page reads the camera list and latest frames live.
- **PhenoCam Network** vegetation cameras (U.S.). `build_context.py` saves the active cameras to `docs/data/phenocams.json`.
- **U.S. Drought Monitor**, current week. `build_context.py` saves a simplified copy to `docs/data/usdm.geojson`.
- **CA drought forecast by river basin** (UC Irvine CHRS, MSDI and SPI), read live from the ca-rx-planner repo's daily file, the same layer as the CA Prescribed Fire Planner.
- `docs/data/cameras.geojson` combines both camera sources for the AGOL web map.

When a site is picked, the panel lists the cameras within 40 km, showing first the ones currently looking toward the site, along with the drought there.

The earlier Streamlit app (`app.py`) was retired in October 2026; it remains in the git history.
