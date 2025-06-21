import pandas as pd
from datetime import datetime

print("🚀 Starting fuel sample fetch...")

try:
    # URL and Parameters
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

    # Build query string
    query_string = "&".join([f"{key}={value}" for key, value in PARAMS.items()])
    full_url = f"{URL}?{query_string}"
    print(f"📥 Fetching data from:\n{full_url}")

    # Load and clean data
    df = pd.read_csv(full_url)
    print(f"✅ Retrieved {len(df)} records.")

    df.columns = [
        "Sample Id", "Date-Time", "Site Name", "SiteId", "Fuel Type",
        "Category", "Sub-Category", "Method", "Sample Avg Value", "Sample Status"
    ]
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
    df = df[df["Date-Time"].notnull()]
    df["Year"] = df["Date-Time"].dt.year

    # Split into two files
    recent = df[df["Year"] >= 2015].drop(columns="Year")
    older = df[df["Year"] <= 2014].drop(columns="Year")

    # Save both CSVs
    recent.to_csv("field_samples_2015_present.csv", index=False)
    older.to_csv("field_samples_2005_2014.csv", index=False)

    print("✅ CSV files generated:")
    print("- field_samples_2005_2014.csv")
    print("- field_samples_2015_present.csv")

except Exception as e:
    print("❌ ERROR OCCURRED:")
    print(str(e))
    exit(1)
