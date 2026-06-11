import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="WTO Trade Concerns Dashboard",
    layout="wide"
)

st.title("WTO Trade Concerns Dashboard")

# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_excel("TRCM_Database.xlsx")

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Filters")

participants = sorted(
    df["Country Raising"].dropna().unique()
)

selected_participants = st.sidebar.multiselect(
    "Participant",
    participants,
    default=participants
)

bodies = sorted(
    df["Body"].dropna().unique()
)

selected_bodies = st.sidebar.multiselect(
    "WTO Body",
    bodies,
    default=bodies
)

tones = sorted(
    df["Tone"].dropna().unique()
)

selected_tones = st.sidebar.multiselect(
    "Tone",
    tones,
    default=tones
)

measure_groups = sorted(
    df["Measure Group"].dropna().unique()
)

selected_measure_groups = st.sidebar.multiselect(
    "Measure Group",
    measure_groups,
    default=measure_groups
)

filtered_df = df[
    (df["Country Raising"].isin(selected_participants))
    &
    (df["Body"].isin(selected_bodies))
    &
    (df["Tone"].isin(selected_tones))
    &
    (df["Measure Group"].isin(selected_measure_groups))
]

# ==================================================
# OVERVIEW
# ==================================================

st.header("Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Interventions",
    len(filtered_df)
)

col2.metric(
    "Participants",
    filtered_df["Country Raising"].nunique()
)

col3.metric(
    "Measure Groups",
    filtered_df["Measure Group"].nunique()
)

left, right = st.columns(2)

with left:

    st.subheader("Tone Distribution")

    tone_counts = (
        filtered_df["Tone"]
        .value_counts()
        .reset_index()
    )

    tone_counts.columns = [
        "Tone",
        "Count"
    ]

    fig_tone = px.pie(
        tone_counts,
        names="Tone",
        values="Count"
    )

    st.plotly_chart(
        fig_tone,
        use_container_width=True
    )

with right:

    st.subheader("WTO Bodies")

    body_counts = (
        filtered_df["Body"]
        .value_counts()
        .reset_index()
    )

    body_counts.columns = [
        "Body",
        "Count"
    ]

    fig_body = px.bar(
        body_counts,
        x="Body",
        y="Count"
    )

    st.plotly_chart(
        fig_body,
        use_container_width=True
    )

st.divider()

# ==================================================
# PARTICIPANTS
# ==================================================

st.header("Participants")

country_counts = (
    filtered_df["Country Raising"]
    .value_counts()
    .head(10)
    .reset_index()
)

country_counts.columns = [
    "Participant",
    "Count"
]

fig_country = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h"
)

st.plotly_chart(
    fig_country,
    use_container_width=True
)

st.divider()

# ==================================================
# BUILD CONCERN DATASET
# ==================================================

concern_records = []

for i in range(1, 6):

    temp = filtered_df[
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

    concern_records.append(temp)

concern_df = pd.concat(
    concern_records,
    ignore_index=True
)

concern_df = concern_df.dropna(subset=["Concern"])

# ==================================================
# CONCERNS
# ==================================================

st.header("Concerns")

st.subheader("Top Concern Families")

concern_counts = (
    concern_df["Concern"]
    .value_counts()
    .head(20)
    .reset_index()
)

concern_counts.columns = [
    "Concern",
    "Count"
]

fig_concerns = px.bar(
    concern_counts,
    x="Count",
    y="Concern",
    orientation="h"
)

st.plotly_chart(
    fig_concerns,
    use_container_width=True
)

st.subheader("Top Sub-Concerns")

subconcern_counts = (
    concern_df["SubConcern"]
    .dropna()
    .value_counts()
    .head(20)
    .reset_index()
)

subconcern_counts.columns = [
    "SubConcern",
    "Count"
]

fig_subconcerns = px.bar(
    subconcern_counts,
    x="Count",
    y="SubConcern",
    orientation="h"
)

st.plotly_chart(
    fig_subconcerns,
    use_container_width=True
)

st.subheader("Concern Explorer")

selected_concern = st.selectbox(
    "Select Concern Family",
    sorted(concern_df["Concern"].dropna().unique())
)

selected_concern_df = concern_df[
    concern_df["Concern"] == selected_concern
]

st.write(
    "Participants raising this concern:",
    selected_concern_df["Participant"].nunique()
)

st.dataframe(
    selected_concern_df,
    use_container_width=True
)

st.divider()

# ==================================================
# MEASURES
# ==================================================

st.header("Measures")

measure_counts = (
    filtered_df["Measure Group"]
    .value_counts()
    .reset_index()
)

measure_counts.columns = [
    "Measure Group",
    "Count"
]

st.subheader("Measure Groups")

fig_measure_group = px.bar(
    measure_counts,
    x="Count",
    y="Measure Group",
    orientation="h"
)

st.plotly_chart(
    fig_measure_group,
    use_container_width=True
)

specific_measure_counts = (
    filtered_df["Specific Measure"]
    .value_counts()
    .head(20)
    .reset_index()
)

specific_measure_counts.columns = [
    "Specific Measure",
    "Count"
]

st.subheader("Specific Measures")

fig_specific = px.bar(
    specific_measure_counts,
    x="Count",
    y="Specific Measure",
    orientation="h"
)

st.plotly_chart(
    fig_specific,
    use_container_width=True
)

st.subheader("Measure Explorer")

selected_measure_group = st.selectbox(
    "Select Measure Group",
    sorted(
        filtered_df["Measure Group"]
        .dropna()
        .unique()
    )
)

measure_explorer = filtered_df[
    filtered_df["Measure Group"]
    == selected_measure_group
]

st.dataframe(
    measure_explorer[
        [
            "Country Raising",
            "Measure Group",
            "Specific Measure",
            "Tone"
        ]
    ],
    use_container_width=True
)

st.divider()

# ==================================================
# PARTICIPANT PROFILE
# ==================================================

st.header("Participant Profile")

selected_country = st.selectbox(
    "Select Participant",
    sorted(
        filtered_df["Country Raising"]
        .dropna()
        .unique()
    )
)

country_df = filtered_df[
    filtered_df["Country Raising"]
    == selected_country
]

col1, col2 = st.columns(2)

col1.metric(
    "Interventions",
    len(country_df)
)

col2.metric(
    "Measure Groups",
    country_df["Measure Group"].nunique()
)

st.dataframe(
    country_df,
    use_container_width=True
)

st.divider()

# ==================================================
# DATABASE
# ==================================================

st.header("Database")

st.dataframe(
    filtered_df,
    use_container_width=True
)
