import requests
import pandas as pd
from io import StringIO

# Rebuild the URL exactly
URL = "https://fems.fs2c.usda.gov/fuelmodel/sample/download"
PARAMS = {
    "returnAll": "",
    "responseFormat": "csv",
    "siteId": "All",
    "sampleId": "",
    "startDate": "2005-01-01T00:00:00.000Z",
    "endDate": "2025-06-21T23:00:00.000Z",
    "filterByFuelId": "",
    "filterByStatus": "Submitted",
    "filterByCategory": "All",
    "filterBySubCategory": "All",
    "filterByMethod": "All",
    "sortBy": "fuel_type",
    "sortOrder": "asc"
}

# Create headers to mimic browser
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/csv"
}

# Make the request
response = requests.get(URL, headers=headers, params=PARAMS)

# Check and parse
if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text))
    
    # Clean and export as before
    df.columns = [
        "Sample Id", "Date-Time", "Site Name", "SiteId", "Fuel Type",
        "Category", "Sub-Category", "Method", "Sample Avg Value", "Sample Status"
    ]
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
    df = df[df["Date-Time"].notnull()]
    df["Year"] = df["Date-Time"].dt.year

    recent = df[df["Year"] >= 2015].drop(columns="Year")
    older = df[df["Year"] <= 2014].drop(columns="Year")

    recent.to_csv("field_samples_2015_present.csv", index=False)
    older.to_csv("field_samples_2005_2014.csv", index=False)

    print("✅ CSV files generated.")
else:
    print(f"❌ Fetch failed: {response.status_code} - {response.reason}")
