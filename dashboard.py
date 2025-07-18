import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Pension Data Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect("cleaned_data.db")
    df = pd.read_sql("SELECT * FROM pension_data", conn)
    conn.close()
    return df

df = load_data()
df = df[df["Year"].notnull()]  # Ensure Year exists
df["Year"] = df["Year"].astype(int)

# Identify numeric columns
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

# Sidebar Filters
st.sidebar.header("Filter Options")
mode = st.sidebar.radio("Choose Analysis Mode", ["Single Country", "Compare Countries"])

if mode == "Single Country":
    country = st.sidebar.selectbox("Select Country", sorted(df["Country"].dropna().unique()))
    df_country = df[df["Country"] == country].sort_values("Year")

    st.title(f"Pension Data Dashboard: {country}")
    st.markdown(f"### View data for **{country}**")

    st.dataframe(df_country, use_container_width=True)

    if numeric_cols:
        st.subheader("📊 Multi-Line Chart (Same Country)")
        selected_vars = st.multiselect("Select up to 3 numeric indicators", numeric_cols, max_selections=3)

        if selected_vars:
            chart_data = df_country[["Year"] + selected_vars].set_index("Year")
            st.line_chart(chart_data)

else:
    st.title("📈 Pension Data Comparison Across Countries")
    selected_countries = st.sidebar.multiselect("Select Countries", sorted(df["Country"].dropna().unique()), max_selections=5)
    selected_variable = st.sidebar.selectbox("Select Numeric Indicator to Compare", numeric_cols)

    if selected_countries:
        df_filtered = df[df["Country"].isin(selected_countries)][["Country", "Year", selected_variable]]
        df_pivot = df_filtered.pivot_table(index="Year", columns="Country", values=selected_variable)

        st.subheader(f"📊 {selected_variable} Across Selected Countries")
        st.line_chart(df_pivot)
