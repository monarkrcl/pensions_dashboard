import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Pension Data Dashboard", layout="wide")

@st.cache_data
def load_data():
    conn = sqlite3.connect("cleaned_data.db")
    df = pd.read_sql("SELECT * FROM pension_data", conn)
    conn.close()
    return df

# Load and clean
df = load_data()
df = df[df["Year"].notnull()]
df["Year"] = df["Year"].astype(int)

# Detect data point columns
exclude_cols = ["Country", "Year"]
all_columns = df.columns.tolist()
data_point_cols = [col for col in all_columns if col not in exclude_cols]

# Sidebar filters
st.sidebar.title("Filter Data")

# Country filter
countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:1])

# Year filter
years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect("Select Years", years, default=years)

# Data Point filter with Select All
st.sidebar.markdown("#### Data Points")
select_all = st.sidebar.checkbox("Select All Data Points", value=True)

if select_all:
    selected_indicators = st.sidebar.multiselect("Choose Data Points", data_point_cols, default=data_point_cols)
else:
    selected_indicators = st.sidebar.multiselect("Choose Data Points", data_point_cols)

# Filter the data
filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"].isin(selected_years))
]

# Main UI
st.title("📊 Pension Data Dashboard")

if not selected_indicators:
    st.warning("Please select at least one data point to view results.")
else:
    st.markdown(f"### Filtered Data for: {', '.join(selected_countries)}")
    st.dataframe(filtered_df[["Country", "Year"] + selected_indicators], use_container_width=True)

    # Chart: If one country and multiple indicators
    if len(selected_countries) == 1 and selected_indicators:
        st.markdown("### 📈 Time Series by Indicator")
        chart_df = filtered_df[["Year"] + selected_indicators].groupby("Year").mean().sort_index()
        st.line_chart(chart_df)

    # Chart: If one indicator and multiple countries
    elif len(selected_countries) > 1 and len(selected_indicators) == 1:
        indicator = selected_indicators[0]
        st.markdown(f"### 📈 {indicator} Across Countries")
        compare_df = filtered_df.pivot_table(index="Year", columns="Country", values=indicator)
        st.line_chart(compare_df)

    # Warning for invalid chart combinations
    elif len(selected_countries) > 1 and len(selected_indicators) > 1:
        st.info("To compare multiple countries, please select only **one** data point at a time.")
