import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Pension Data Dashboard", layout="wide")

# Load the database
@st.cache_data
def load_data():
    conn = sqlite3.connect("cleaned_data.db")
    df = pd.read_sql("SELECT * FROM pension_data", conn)
    conn.close()
    return df

df = load_data()
df = df[df["Year"].notnull()]
df["Year"] = df["Year"].astype(int)

# Detect numeric columns (data points)
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

# Sidebar filters
st.sidebar.title("Filter Data")
countries = sorted(df["Country"].dropna().unique())
years = sorted(df["Year"].unique())

selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:1])
selected_years = st.sidebar.multiselect("Select Years", years, default=years)
selected_indicators = st.sidebar.multiselect("Select Data Points", numeric_cols, default=numeric_cols[:1])

# Filter data
filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"].isin(selected_years))
]

# Title
st.title("📊 Pension Data Explorer")

# Show table
st.markdown(f"### Showing data for: {', '.join(selected_countries)}")
st.dataframe(filtered_df[["Country", "Year"] + selected_indicators], use_container_width=True)

# Plot if one country is selected
if len(selected_countries) == 1 and selected_indicators:
    st.markdown("### 📈 Time Series Chart (Single Country)")
    chart_df = filtered_df[["Year"] + selected_indicators].groupby("Year").mean().sort_index()
    st.line_chart(chart_df)

# Plot if one indicator is selected and multiple countries are selected
elif len(selected_countries) > 1 and len(selected_indicators) == 1:
    indicator = selected_indicators[0]
    st.markdown(f"### 📈 Compare Countries for: {indicator}")
    compare_df = filtered_df.pivot_table(index="Year", columns="Country", values=indicator)
    st.line_chart(compare_df)

# Info if too many/missing selections
elif len(selected_indicators) != 1 and len(selected_countries) > 1:
    st.warning("To compare countries, select **only one** data point.")
