import pandas as pd
import requests
from datetime import datetime
from io import StringIO

# Construct URL
URL = "https://fems.fs2c.usda.gov/fuelmodel/sample/download"
PARAMS = {
    "returnAll": "",
    "responseFormat": "csv",
    "siteId": "All",
    "sampleId": "",
    "startDate": "2005-01-01T00:00:00.000Z",
    "endDate": datetime.utcnow().strftime("%Y-%m-%dT23:00:00.000Z"),
    "filterByFuelId": "",
    "filterByStatus": "Submitted",
    "filterByCategory": "All",
    "filterBySubCategory": "All",
    "filterByMethod": "All",
    "sortBy": "fuel_type",
    "sortOrder": "asc"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OpenAI-FuelFetcher/1.0)"
}

query_string = "&".join([f"{key}={value}" for key, value in PARAMS.items()])
full_url = f"{URL}?{query_string}"

print(f"🔍 Fetching: {full_url}")

try:
    # Use requests with custom headers
    response = requests.get(full_url, headers=HEADERS)
    response.raise_for_status()  # Raise error if status code != 200
    df = pd.read_csv(StringIO(response.text))
    print(f"✅ Downloaded: {len(df)} rows")

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

    print("✅ CSV files saved successfully.")

except Exception as e:
    print(f"❌ Fetch failed: {e}")
    exit(1)
