
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Trade-Related Climate and Sustainability Measures Database",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1400px;
}
[data-testid="metric-container"] {
    border: 1px solid #E6E6E6;
    padding: 15px;
    border-radius: 8px;
    background-color: #fafafa;
}
</style>
""", unsafe_allow_html=True)

st.title("Trade-Related Climate and Sustainability Measures Database")

# LOAD DATA
df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

if "Date" in df.columns:
    df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}

CHART_FONT = {"family": "Arial", "size": 14, "color": "black"}

def style_chart(fig):
    fig.update_layout(
        font=CHART_FONT,
        dragmode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def build_concern_df(dataframe):
    frames = []
    for i in range(1, 6):
        col = f"Concern {i}"
        if col in dataframe.columns:
            temp = dataframe[["Country Raising", "Measure Group", col]].copy()
            temp.columns = ["Participant", "Measure Group", "Concern"]
            frames.append(temp)

    if not frames:
        return pd.DataFrame(columns=["Participant", "Measure Group", "Concern"])

    return pd.concat(frames, ignore_index=True).dropna(subset=["Concern"])

concern_df = build_concern_df(df)

# FILTERS
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Countries",
    sorted(df["Country Raising"].dropna().unique())
)

measures = st.sidebar.multiselect(
    "Measure Groups",
    sorted(df["Measure Group"].dropna().unique())
)

tones = st.sidebar.multiselect(
    "Tones",
    sorted(df["Tone"].dropna().unique())
)

bodies = st.sidebar.multiselect(
    "WTO Bodies",
    sorted(df["Body"].dropna().unique())
)

concerns = st.sidebar.multiselect(
    "Concerns",
    sorted(concern_df["Concern"].dropna().unique())
)

dashboard_df = df.copy()

if countries:
    dashboard_df = dashboard_df[dashboard_df["Country Raising"].isin(countries)]

if measures:
    dashboard_df = dashboard_df[dashboard_df["Measure Group"].isin(measures)]

if tones:
    dashboard_df = dashboard_df[dashboard_df["Tone"].isin(tones)]

if bodies:
    dashboard_df = dashboard_df[dashboard_df["Body"].isin(bodies)]

if concerns:
    masks = []
    for i in range(1, 6):
        col = f"Concern {i}"
        if col in dashboard_df.columns:
            masks.append(dashboard_df[col].isin(concerns))
    if masks:
        mask = masks[0]
        for m in masks[1:]:
            mask = mask | m
        dashboard_df = dashboard_df[mask]

dashboard_concern_df = build_concern_df(dashboard_df)

if dashboard_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# DOWNLOAD
csv = dashboard_df.to_csv(index=False)
st.download_button(
    "Download Filtered Dataset",
    csv,
    file_name="TRCSM_Filtered_Data.csv",
    mime="text/csv"
)

# OVERVIEW
st.markdown("## Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Interventions", len(dashboard_df))
c2.metric("Participants", dashboard_df["Country Raising"].nunique())
c3.metric("Measure Groups", dashboard_df["Measure Group"].nunique())
c4.metric("WTO Bodies", dashboard_df["Body"].nunique())
c5.metric("Most Active Body", dashboard_df["Body"].value_counts().idxmax())

# INSIGHTS
st.markdown("## Key Insights")

insights = []
insights.append(f"{len(dashboard_df)} interventions in the filtered dataset.")
insights.append(f"Most active WTO body: {dashboard_df['Body'].value_counts().idxmax()}.")
insights.append(f"Most discussed measure group: {dashboard_df['Measure Group'].value_counts().idxmax()}.")
insights.append(f"Dominant tone: {dashboard_df['Tone'].value_counts().idxmax()}.")

for item in insights:
    st.markdown(f"• {item}")

# DISTRIBUTION
left, right = st.columns(2)

with left:
    st.markdown("### Intervention Tones")
    tone_counts = dashboard_df["Tone"].value_counts().reset_index()
    tone_counts.columns = ["Tone", "Count"]

    fig = px.bar(
        tone_counts.sort_values("Count"),
        x="Count",
        y="Tone",
        orientation="h",
        color="Tone"
    )
    st.plotly_chart(style_chart(fig), use_container_width=True, config=PLOTLY_CONFIG)

with right:
    st.markdown("### WTO Bodies")
    body_counts = dashboard_df["Body"].value_counts().reset_index()
    body_counts.columns = ["Body", "Count"]

    fig = px.bar(
        body_counts.sort_values("Count"),
        x="Count",
        y="Body",
        orientation="h"
    )
    st.plotly_chart(style_chart(fig), use_container_width=True, config=PLOTLY_CONFIG)

# PARTICIPANTS
st.markdown("## Leading Participants")

country_counts = dashboard_df["Country Raising"].value_counts().head(10).sort_values().reset_index()
country_counts.columns = ["Participant", "Count"]

fig = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h"
)

st.plotly_chart(style_chart(fig), use_container_width=True, config=PLOTLY_CONFIG)

# CONCERNS
st.markdown("## Top Concerns")

if not dashboard_concern_df.empty:
    concern_counts = dashboard_concern_df["Concern"].value_counts().head(20).reset_index()
    concern_counts.columns = ["Concern", "Count"]

    fig = px.bar(
        concern_counts.sort_values("Count"),
        x="Count",
        y="Concern",
        orientation="h"
    )

    st.plotly_chart(style_chart(fig), use_container_width=True, config=PLOTLY_CONFIG)

# MEASURES & RELATIONSHIPS
st.markdown("## Measures & Relationships")

left, right = st.columns(2)

with left:
    if "Specific Measure" in dashboard_df.columns:

        treemap_df = (
            dashboard_df[["Measure Group", "Specific Measure"]]
            .dropna()
            .assign(Count=1)
        )

        fig = px.treemap(
            treemap_df,
            path=["Measure Group", "Specific Measure"],
            values="Count",
            title="Measure Group → Specific Measure"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

with right:

    heatmap_df = pd.crosstab(
        dashboard_df["Country Raising"],
        dashboard_df["Measure Group"]
    )

    fig = px.imshow(
        heatmap_df,
        aspect="auto",
        title="Country × Measure Group"
    )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# CONCERN × MEASURE GROUP

if not dashboard_concern_df.empty:

    concern_measure = pd.crosstab(
        dashboard_concern_df["Concern"],
        dashboard_concern_df["Measure Group"]
    )

    fig = px.imshow(
        concern_measure,
        aspect="auto",
        title="Concern × Measure Group"
    )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# DATA TABLE
with st.expander("View Filtered Data", expanded=False):
    st.dataframe(dashboard_df, use_container_width=True)

st.caption(
    "Trade-Related Climate and Sustainability Measures Database | Last updated: 13 June 2026"
)
