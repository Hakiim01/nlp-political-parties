import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px

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
    #df.drop(columns=["Unnamed: 0"],inplace=True)
    
    return df

# Load data with spinner (built into @st.cache_data)
df = load_data(DATA_PATH)
st.success(f"✅ Loaded data from {DATA_PATH}")

# --- Preview Data ---
st.subheader("📄 Raw Data Preview")
st.dataframe(df.head())





# Ensure datetime and session_id
df["Title"] = df["Title"].astype(str)

# Get one row per session (first timestamp)
session_starts = df.sort_values("Date").groupby("Title").first().reset_index()

# Plot: 1D time series with sessions on y-axis
fig = px.scatter(
    session_starts,
    x="Date",
    y=[""] * len(session_starts),  # blank y-axis for 1D look
    hover_name="Subcorpus",
    custom_data=["Title"],
    title="🕓 Session Timeline (Click to Select)"
)
fig.update_traces(marker=dict(size=10,symbol="diamond"), mode="markers")
fig.update_yaxes(visible=True)
fig.update_layout(height=150)

selected_session = st.plotly_chart(fig, use_container_width=True)

# NOTE: Plotly doesn't natively support click events in Streamlit.
# So next best: add a selectbox to choose session_id.
selected = st.selectbox("🎯 Select a session to explore", session_starts["Title"])
session_df = df[df["Title"] == selected]



st.subheader("📉 Drill-Down Line Chart (Index-Based with Table Sync)")

df = session_df.copy()

# --- Detect column types ---
numeric_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

if numeric_cols:
    y_col = st.selectbox("📈 Value Column (Y-axis)", numeric_cols)
    group_col = st.selectbox("🧩 Group By (Optional)", ["(None)"] + cat_cols)

    # Filter by group if selected
    if group_col != "(None)":
        group_values = df[group_col].dropna().unique().tolist()
        selected_groups = st.multiselect(f"Filter {group_col}", group_values, default=group_values)
        df = df[df[group_col].isin(selected_groups)]

    # --- Plotly line chart using index ---
    fig = px.line(
        df,
        x=df.index,
        y=y_col,
        color=group_col if group_col != "(None)" else None,
        markers=True,
        title=f"{y_col} over Index" + (f" by {group_col}" if group_col != "(None)" else "")
    )
    fig.update_layout(xaxis_title="Index", legend_title_text=group_col if group_col != "(None)" else "")

    # Display chart and capture zoom/pan range
    chart_output = st.plotly_chart(fig, use_container_width=True)
    zoom_data = st.session_state.get("zoom_data")

    # Capture zoom events (requires st.session_state + workaround below)
    zoom_event = st.plotly_chart(fig, use_container_width=True, key="chart_with_events")

    if "plotly_relayoutData" in st.session_state:
        relayout = st.session_state.plotly_relayoutData
        if "xaxis.range[0]" in relayout and "xaxis.range[1]" in relayout:
            x_min = int(float(relayout["xaxis.range[0]"]))
            x_max = int(float(relayout["xaxis.range[1]"]))
            filtered_view = df.loc[(df.index >= x_min) & (df.index <= x_max)]
        else:
            filtered_view = df
    else:
        filtered_view = df

    st.subheader("🧾 Filtered Data View (Matches Chart Zoom)")
    st.dataframe(filtered_view)

else:
    st.warning("Your dataset must have at least one numeric column.")

