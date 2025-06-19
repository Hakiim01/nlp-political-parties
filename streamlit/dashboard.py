import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px
from streamlit_plotly_events import plotly_events

st.markdown("""
    <link rel="stylesheet" href="https://unpkg.com/carbon-components/css/carbon-components.min.css">
    <style>
    body {
        font-family: "IBM Plex Sans", sans-serif;
    }
    </style>
""", unsafe_allow_html=True)



st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("🔍 Interactive Data Explorer for Political speech Analyisis")

# --- Config ---
DATA_PATH = "data/2022_sentiment_base.csv"
st.cache_data.clear()
@st.cache_data(show_spinner=True)
def load_data(path):
    df = pd.read_csv(path)
    df.rename(columns={"Unnamed: 0": "Index"},inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Speaker_name"] = df["Speaker_name"].astype("category")
    df["Speaker_gender"] = df["Speaker_gender"].astype("category")
    df["Speaker_party"] = df["Speaker_party"].astype("category")
    df["Title"] = df["Title"].astype(str)
    #df.drop(columns=["Unnamed: 0"],inplace=True)
    
    return df

# Load data with spinner (built into @st.cache_data)
df = load_data(DATA_PATH)
st.success(f"✅ Loaded data from {DATA_PATH}")

# --- Preview Data ---
st.subheader("📄 Raw Data Preview")
st.dataframe(df.head())


# Extract and sort unique dates
available_dates = sorted(df["Date"].dt.date.unique().tolist())

# --- Select a date range from available dates only ---
st.subheader("📆 Select Date Range")
date_range = st.select_slider(
    "Select session date range",
    options=available_dates,
    value=(available_dates[0], available_dates[-1])
)

# --- Filter DataFrame based on selected range ---
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]




import streamlit as st
import pandas as pd
import plotly.express as px

# Assume df is loaded

st.subheader("📉 Multi Group-By Filters")
df = filtered_df.copy()
numeric_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

if numeric_cols and cat_cols:
    y_col = st.sidebar.selectbox("📈 Value Column (Y-axis)", numeric_cols)
    group_filters = st.sidebar.multiselect("Select Group-By Filters (multiple)", options=cat_cols)

    filtered_df = df.copy()
    for group_col in group_filters:
        unique_vals = filtered_df[group_col].dropna().unique().tolist()
        selected_vals = st.sidebar.multiselect(f"Filter {group_col}", unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[group_col].isin(selected_vals)]

    facet_row = group_filters[1] if len(group_filters) > 1 else None
    facet_col = group_filters[2] if len(group_filters) > 2 else None
    color_col = group_filters[0] if group_filters else None

    fig = px.bar(
        filtered_df,
        x=filtered_df.index,
        y=y_col,
        color=color_col,
        facet_row=facet_row,
        facet_col=facet_col,
        title=f"{y_col} over Index"
    )
    fig.update_layout(
        xaxis_title="Index",
        legend_title_text=color_col if color_col else "",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
    st.subheader("🧾 Filtered Data")
    st.dataframe(filtered_df)

else:
    st.warning("Your dataset must have at least one numeric and one categorical column.")


