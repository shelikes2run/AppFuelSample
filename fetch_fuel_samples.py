import pandas as pd
from datetime import datetime

# ================================
# 📅 Define dynamic date range
# ================================
start_date = "2015-01-01T00:00:00.000Z"
end_date = datetime.utcnow().strftime("%Y-%m-%dT23:00:00.000Z")

# ================================
# 🔗 Build the URL dynamically
# ================================
url = (
    "https://fems.fs2c.usda.gov/fuelmodel/sample/download"
    f"?returnAll=&responseFormat=csv"
    f"&siteId=All"
    f"&sampleId="
    f"&startDate={start_date}"
    f"&endDate={end_date}"
    f"&filterByFuelId="
    f"&filterByStatus=Submitted"
    f"&filterByCategory=All"
    f"&filterBySubCategory=All"
    f"&filterByMethod=All"
    f"&sortBy=fuel_type"
    f"&sortOrder=asc"
)

print("📥 Fetching data from:")
print(url)

# ================================
# 📊 Read and clean the data
# ================================
try:
    df = pd.read_csv(url)

    df.columns = [
        "Sample Id", "Date-Time", "Site Name", "SiteId", "Fuel Type",
        "Category", "Sub-Category", "Method", "Sample Avg Value", "Sample Status"
    ]

    df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
    df = df[df["Date-Time"].notnull()]

    # Save to CSV
    df.to_csv("field_samples_2015_present.csv", index=False)

    print("✅ Data successfully saved to 'field_samples_2015_present.csv'.")

except Exception as e:
    print("❌ Error fetching or processing data:")
    print(e)
