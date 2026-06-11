import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="WTO Trade Concerns Dashboard",
    layout="wide"
)

# Title
st.title("WTO Trade Concerns Dashboard")

# Load data
df = pd.read_excel("TRCM_Database.xlsx")

# Summary statistics
st.header("Summary (2026)")

col1, col2, col3 = st.columns(3)

col1.metric("Total Interventions", len(df))
col2.metric("Countries", df["Country Raising"].nunique())
col3.metric("Measure Groups", df["Measure Group"].nunique())

# --------------------------------------------------
# INTERVENTIONS BY PARTICIPANT
# --------------------------------------------------

st.header("Interventions by Participants")

country_counts = (
    df["Country Raising"]
    .value_counts()
    .reset_index()
)

country_counts.columns = ["Country", "Count"]

fig_country = px.bar(
    country_counts.head(15),
    x="Count",
    y="Country",
    orientation="h",
    labels={
        "Country": "Participant",
        "Count": "Number of Interventions"
    }
)

st.plotly_chart(fig_country, use_container_width=True)

# --------------------------------------------------
# TONE DISTRIBUTION
# --------------------------------------------------

st.header("Tone Distribution")

tone_counts = (
    df["Tone"]
    .value_counts()
    .reset_index()
)

tone_counts.columns = ["Tone", "Count"]

fig_tone = px.pie(
    tone_counts,
    names="Tone",
    values="Count"
)

st.plotly_chart(fig_tone, use_container_width=True)

# --------------------------------------------------
# WTO BODY CHART
# --------------------------------------------------

st.header("WTO Bodies")

body_counts = (
    df["Body"]
    .value_counts()
    .reset_index()
)

body_counts.columns = ["Body", "Count"]

fig_body = px.bar(
    body_counts,
    x="Body",
    y="Count"
)

st.plotly_chart(fig_body, use_container_width=True)

# --------------------------------------------------
# CONCERN HIERARCHY SUNBURST
# --------------------------------------------------

st.header("Concern Hierarchy")

concern_frames = []

for i in range(1, 6):

    temp = df[
        [
            "Country Raising",
            f"Concern {i}",
            f"Sub-Concern {i}"
        ]
    ].copy()

    temp.columns = [
        "Participant",
        "Concern",
        "SubConcern"
    ]

    concern_frames.append(temp)

concern_df = pd.concat(
    concern_frames,
    ignore_index=True
)

concern_df = concern_df.dropna()

fig_concern_sunburst = px.sunburst(
    concern_df,
    path=[
        "Participant",
        "Concern",
        "SubConcern"
    ],
    title="Participant → Concern → Sub-Concern"
)

st.plotly_chart(
    fig_concern_sunburst,
    use_container_width=True
)

# --------------------------------------------------
# MEASURE HIERARCHY SUNBURST
# --------------------------------------------------

st.header("Measure Hierarchy")

measure_df = df[
    [
        "Country Raising",
        "Measure Group",
        "Specific Measure"
    ]
].copy()

measure_df.columns = [
    "Participant",
    "MeasureGroup",
    "SpecificMeasure"
]

measure_df = measure_df.dropna()

fig_measure_sunburst = px.sunburst(
    measure_df,
    path=[
        "Participant",
        "MeasureGroup",
        "SpecificMeasure"
    ],
    title="Participant → Measure Group → Specific Measure"
)

st.plotly_chart(
    fig_measure_sunburst,
    use_container_width=True
)

# --------------------------------------------------
# COUNTRY × MEASURE GROUP HEATMAP
# --------------------------------------------------

st.header("Participant × Measure Group")

heatmap_df = pd.crosstab(
    df["Country Raising"],
    df["Measure Group"]
)

fig_heatmap = px.imshow(
    heatmap_df,
    aspect="auto",
    title="Interventions by Participant and Measure Group"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

st.header("Database")

st.dataframe(
    df,
    use_container_width=True
)
