# Field Sample Comparison Dashboard

This interactive dashboard allows users to compare current-year field sample data to historical trends for various fuel types and vegetation categories.

## Features

- 🔍 Filter by site, fuel type, category, year, and month
- 📊 Visualize current vs. historical data with average, min, and max overlays
- 📅 Data aggregated by bi-monthly intervals (1st and 15th of each month)
- 📥 Export filtered data to CSV
- 🖼️ Download individual graphs as PNG or PDF

## Getting Started

### Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deployed on Streamlit Cloud

1. https://appfuelsample-gvoxhxzzyefqcr2atsuqyc.streamlit.app/

Enjoy!

## Web page and ArcGIS Online app (replaces the Streamlit app)

`docs/index.html` is the same dashboard as a static page, published with GitHub Pages
(https://shelikes2run.github.io/AppFuelSample/) and embedded in the NIFC ArcGIS Online
Experience Builder app **Field Sample Comparison**. The daily workflow fetches the FEMS samples and
then runs `build_web.py`, which writes the page's data to `docs/data/` (no keys needed).
