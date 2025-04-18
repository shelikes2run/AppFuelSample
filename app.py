import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st
from datetime import datetime
import io

# --- Load Data ---
@st.cache_data
def load_data():
    url1 = "https://raw.githubusercontent.com/shelikes2run/AppFuelSample/main/field_samples_2005_2014.csv"
    url2 = "https://raw.githubusercontent.com/shelikes2run/AppFuelSample/main/field_samples_2015_present.csv"
    df1 = pd.read_csv(url1)
    df2 = pd.read_csv(url2)
    df = pd.concat([df1, df2])
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")
    df = df[df["Date-Time"].notnull()]
    df["Date-Time"] = df["Date-Time"].dt.tz_localize(None)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")
sites = st.sidebar.multiselect("Select Sites", options=sorted(df['Site Name'].dropna().unique()))
categories = st.sidebar.multiselect("Select Categories", options=sorted(df['Category'].dropna().unique()))
fuel_types = st.sidebar.multiselect("Select Fuel Types", options=sorted(df['Fuel Type'].dropna().unique()))

years = sorted(df['Date-Time'].dt.year.unique())
current_year = st.sidebar.selectbox("Current Year", options=years[::-1])
historical_years = st.sidebar.multiselect("Historical Years", options=years, default=[y for y in years if y != current_year])
months = st.sidebar.multiselect("Months", options=range(1, 13), default=list(range(1, 13)))

# --- Filter Data ---
filtered_df = df.copy()
if sites:
    filtered_df = filtered_df[filtered_df['Site Name'].isin(sites)]
if categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
if fuel_types:
    filtered_df = filtered_df[filtered_df['Fuel Type'].isin(fuel_types)]

filtered_df["Month"] = filtered_df["Date-Time"].dt.month
filtered_df["Year"] = filtered_df["Date-Time"].dt.year
filtered_df = filtered_df[filtered_df["Month"].isin(months)]

def to_half_month(dt):
    return datetime(2000, dt.month, 1 if dt.day <= 14 else 15)
filtered_df["AlignDate"] = filtered_df["Date-Time"].apply(to_half_month)

# --- Plotting ---
st.title("📊 Field Sample Comparison Dashboard")

if filtered_df.empty:
    st.warning("No data matches your filter selections.")
else:
    current = filtered_df[filtered_df["Year"] == current_year]
    historical = filtered_df[filtered_df["Year"].isin(historical_years)]

    cur_summary = current.groupby(["AlignDate", "Category"])["Sample Avg Value"].mean().reset_index(name="Current")
    if len(historical_years) == 1:
        hist_summary = historical.groupby(["AlignDate", "Category"])["Sample Avg Value"].mean().reset_index(name="SingleYear")
    else:
        hist_summary = historical.groupby(["AlignDate", "Category"])["Sample Avg Value"].agg(Avg="mean", Min="min", Max="max").reset_index()

    categories_used = cur_summary["Category"].unique()
    for i, cat in enumerate(categories_used):
        st.subheader(f"Category: {cat}")
        fig, ax = plt.subplots(figsize=(10, 5))
        color = sns.color_palette("tab10")[i % 10]

        cat_current = cur_summary[cur_summary["Category"] == cat]
        ax.plot(cat_current["AlignDate"], cat_current["Current"], marker='o', linestyle='-', label=f"{current_year} Current", color=color)

        if len(historical_years) == 1 and "SingleYear" in hist_summary.columns:
            cat_hist = hist_summary[hist_summary["Category"] == cat]
            ax.plot(cat_hist["AlignDate"], cat_hist["SingleYear"], linestyle='--', marker='s', color='purple', label=f"{historical_years[0]}")
        elif not historical.empty:
            cat_hist = hist_summary[hist_summary["Category"] == cat]
            ax.plot(cat_hist["AlignDate"], cat_hist["Avg"], linestyle='--', color='orange', label="Hist Avg")
            ax.plot(cat_hist["AlignDate"], cat_hist["Min"], linestyle=':', color='red', label="Hist Min")
            ax.plot(cat_hist["AlignDate"], cat_hist["Max"], linestyle=':', color='green', label="Hist Max")

        ax.set_xlabel("Month")
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b')) #
        fig.autofmt_xdate()
        ax.set_ylabel("Sample Avg Value")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # --- Export Buttons ---
    st.markdown("### 📤 Export Options")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data (CSV)", csv, "filtered_samples.csv", "text/csv")

    for i, cat in enumerate(categories_used):
        fig, ax = plt.subplots(figsize=(10, 5))
        color = sns.color_palette("tab10", len(categories_used))[i % len(categories_used)]

        cat_current = cur_summary[cur_summary["Category"] == cat]
        ax.plot(cat_current["AlignDate"], cat_current["Current"], marker='o', linestyle='-', label=f"{current_year} Current", color=color)
        ax.set_title(f"Export View – {cat}")
        ax.legend()

        png_buf = io.BytesIO()
        pdf_buf = io.BytesIO()
        fig.savefig(png_buf, format="png")
        fig.savefig(pdf_buf, format="pdf")

        st.download_button(f"Download {cat} PNG", png_buf.getvalue(), file_name=f"{cat}_plot.png", mime="image/png")
        st.download_button(f"Download {cat} PDF", pdf_buf.getvalue(), file_name=f"{cat}_plot.pdf", mime="application/pdf")
