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
DATA_PATH = "data/2020_22_sentiment_base_with_topics.csv"
#st.cache_data.clear()
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





# Assume df is loaded and filtered_df is ready from your date range code above

tab1, tab2, tab3 = st.tabs(["📉 Multi Group-By Bar Chart", "Other Tab", "🧠 Party vs Topic Explorer"])


with tab1:
    st.header("Multi Group-By Filters & Bar Chart")

    df = filtered_df.copy()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if numeric_cols and cat_cols:
        # Filters placed ABOVE the chart
        y_col = st.selectbox("📈 Value Column (Y-axis)", numeric_cols)
        group_filters = st.multiselect("Select Group-By Filters (multiple)", options=cat_cols)

        # Filter the dataframe with checkboxes for each selected group filter
        filtered_df_tab = df.copy()
        for group_col in group_filters:
            unique_vals = filtered_df_tab[group_col].dropna().unique().tolist()
            selected_vals = st.multiselect(f"Filter {group_col}", unique_vals, default=unique_vals)
            filtered_df_tab = filtered_df_tab[filtered_df_tab[group_col].isin(selected_vals)]

        facet_row = group_filters[1] if len(group_filters) > 1 else None
        facet_col = group_filters[2] if len(group_filters) > 2 else None
        color_col = group_filters[0] if group_filters else None

        fig = px.bar(
            filtered_df_tab,
            x=filtered_df_tab.index,
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
    else:
        st.warning("Your dataset must have at least one numeric and one categorical column.")

with tab2:
    st.write("This tab is reserved for other visualizations or content.")
    

with tab3:
    st.header("🧠 Sentiment Analysis by Topic and Party")

    df_tab3 = filtered_df.copy()
    
    # --- Per-column filters ---
    st.subheader("🎛️ Filter by Attributes")
    all_cat_cols = df_tab3.select_dtypes(include=["object", "category"]).columns.tolist()
    all_cat_cols = [col for col in all_cat_cols if col not in ["text", "Topic 1"]]  # Exclude long text and topic

    st.subheader("🔧 Choose Filter Columns")
    selected_filter_cols = st.multiselect("Select which features to filter by:", options=all_cat_cols)

    for col in selected_filter_cols:
        unique_vals = sorted(df_tab3[col].dropna().unique().tolist())
        selected_vals = st.multiselect(f"Filter values for `{col}`:", unique_vals, default=unique_vals, key=f"valfilter_{col}")
        df_tab3 = df_tab3[df_tab3[col].isin(selected_vals)]
        
    
    # --- Topic selection ---
    st.subheader("✅ Select Topics")

    # Initialize session state for topic selection
    if "all_topics_selected" not in st.session_state:
        st.session_state.all_topics_selected = True

    all_topics = sorted(df_tab3["Topic 1"].dropna().unique().tolist())

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("✅ Select All Topics"):
            st.session_state.all_topics_selected = True
        if st.button("❌ Deselect All Topics"):
            st.session_state.all_topics_selected = False

    # Handle topic selection logic
    default_topics = all_topics if st.session_state.all_topics_selected else []

    selected_topics = st.multiselect(
        "Choose topics to include:",
        options=all_topics,
        default=default_topics,
        key="topic_multiselect"
    )

    # Apply filter
    df_tab3 = df_tab3[df_tab3["Topic 1"].isin(selected_topics)]

    if df_tab3.empty:
        st.warning("No data available after applying filters.")
    else:
        # --- Aggregate compound_score ---
        agg_df = df_tab3.groupby(["Speaker_party", "Topic 1"])["compound_score"].agg(["min", "max", "mean"]).reset_index()

        melt_df = agg_df.melt(
            id_vars=["Speaker_party", "Topic 1"],
            value_vars=["min", "max", "mean"],
            var_name="Statistic",
            value_name="Compound Score"
        )

        st.subheader("📊 Compound Score (Min / Mean / Max) by Topic and Party")
        fig = px.bar(
            melt_df,
            x="Speaker_party",
            y="Compound Score",
            color="Statistic",
            barmode="group",
            facet_col="Topic 1",
            title="Sentiment Statistics per Topic grouped by Party",
            category_orders={"Statistic": ["min", "mean", "max"]},
            height=600
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # --- Most positive / negative speeches ---
        st.subheader("🔍 Most Positive and Most Negative Speeches")

        top_positive = df_tab3.sort_values(by="compound_score", ascending=False).head(3)
        top_negative = df_tab3.sort_values(by="compound_score", ascending=True).head(3)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 😊 Most Positive Speeches")
            for _, row in top_positive.iterrows():
                st.markdown(f"**{row['Speaker_name']} ({row['Speaker_party']})** — *{row['Topic 1']}* — `{row['compound_score']:.2f}`")
                st.markdown(f"> {row['text']}\n")

        with col2:
            st.markdown("### 😡 Most Negative Speeches")
            for _, row in top_negative.iterrows():
                st.markdown(f"**{row['Speaker_name']} ({row['Speaker_party']})** — *{row['Topic 1']}* — `{row['compound_score']:.2f}`")
                st.markdown(f"> {row['text']}\n")




