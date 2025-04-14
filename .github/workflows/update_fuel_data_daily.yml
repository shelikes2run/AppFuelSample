import pandas as pd
from datetime import datetime

# URL for fetching USDA FEMS fuel model data
URL = "https://fems.fs2c.usda.gov/fuelmodel/sample/download"
PARAMS = {
    "returnAll": "",
    "responseFormat": "csv",
    "siteId": "All",
    "sampleId": "",
    "startDate": "2005-01-01T00:00:00.000Z",
    "endDate": "2025-03-25T23:00:00.000Z",
    "filterByFuelId": "",
    "filterByStatus": "Submitted",
    "filterByCategory": "All",
    "filterBySubCategory": "All",
    "filterByMethod": "All",
    "sortBy": "fuel_type",
    "sortOrder": "asc"
}

# Read CSV directly from constructed URL
query_string = "&".join([f"{key}={value}" for key, value in PARAMS.items()])
full_url = f"{URL}?{query_string}"

df = pd.read_csv(full_url)
df.columns = [
    "Sample Id", "Date-Time", "Site Name", "SiteId", "Fuel Type",
    "Category", "Sub-Category", "Method", "Sample Avg Value", "Sample Status"
]
df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
df = df[df["Date-Time"].notnull()]
df["Year"] = df["Date-Time"].dt.year

# Split into two parts
recent = df[df["Year"] >= 2015].drop(columns="Year")
older = df[df["Year"] <= 2014].drop(columns="Year")

# Save locally
recent.to_csv("field_samples_2015_present.csv", index=False)
older.to_csv("field_samples_2005_2014.csv", index=False)

print("✅ CSV files generated:")
print("- field_samples_2005_2014.csv")
print("- field_samples_2015_present.csv")
