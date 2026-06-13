import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="WTO Trade Concerns Dashboard", layout="wide")

st.title("WTO Trade Concerns Dashboard")

df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# Filters
st.sidebar.header("Filters")

participants = sorted(df["Country Raising"].dropna().unique())
selected_participants = st.sidebar.multiselect(
    "Participant",
    participants,
    default=participants
)

bodies = sorted(df["Body"].dropna().unique())
selected_bodies = st.sidebar.multiselect(
    "WTO Body",
    bodies,
    default=bodies
)

tones = sorted(df["Tone"].dropna().unique())
selected_tones = st.sidebar.multiselect(
    "Tone",
    tones,
    default=tones
)

measure_groups = sorted(df["Measure Group"].dropna().unique())
selected_measure_groups = st.sidebar.multiselect(
    "Measure Group",
    measure_groups,
    default=measure_groups
)

filtered_df = df[
    (df["Country Raising"].isin(selected_participants))
    & (df["Body"].isin(selected_bodies))
    & (df["Tone"].isin(selected_tones))
    & (df["Measure Group"].isin(selected_measure_groups))
]

# Build concern dataset from Concern 1-5
concern_frames = []

for i in range(1, 6):
    col_name = f"Concern {i}"
    if col_name in filtered_df.columns:
        temp = filtered_df[["Country Raising", col_name]].copy()
        temp.columns = ["Participant", "Concern"]
        concern_frames.append(temp)

if concern_frames:
    concern_df = pd.concat(concern_frames, ignore_index=True)
    concern_df = concern_df.dropna(subset=["Concern"])
else:
    concern_df = pd.DataFrame(columns=["Participant", "Concern"])

# Overview
st.header("Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Interventions", len(filtered_df))
c2.metric("Participants", filtered_df["Country Raising"].nunique())
c3.metric("Measure Groups", filtered_df["Measure Group"].nunique())

left, right = st.columns(2)

with left:
    st.subheader("Tone Distribution")

    tone_counts = filtered_df["Tone"].value_counts().reset_index()
    tone_counts.columns = ["Tone", "Count"]

    fig = px.pie(
        tone_counts,
        names="Tone",
        values="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("WTO Bodies")

    body_counts = filtered_df["Body"].value_counts().reset_index()
    body_counts.columns = ["Body", "Count"]

    fig = px.bar(
        body_counts,
        x="Body",
        y="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Participants
st.header("Participants")

country_counts = (
    filtered_df["Country Raising"]
    .value_counts()
    .head(10)
    .reset_index()
)

country_counts.columns = ["Participant", "Count"]

fig = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Concerns
st.header("Concerns")

if not concern_df.empty:

    concern_counts = (
        concern_df["Concern"]
        .value_counts()
        .reset_index()
    )

    concern_counts.columns = ["Concern", "Count"]

    fig = px.bar(
        concern_counts.head(20),
        x="Count",
        y="Concern",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Concern Explorer")

    selected_concern = st.selectbox(
        "Select Concern",
        sorted(concern_df["Concern"].unique())
    )

    explorer_df = concern_df[
        concern_df["Concern"] == selected_concern
    ]

    st.metric(
        "Participants Raising This Concern",
        explorer_df["Participant"].nunique()
    )

    participant_counts = (
        explorer_df["Participant"]
        .value_counts()
        .reset_index()
    )

    participant_counts.columns = ["Participant", "Count"]

    fig = px.bar(
        participant_counts,
        x="Count",
        y="Participant",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(explorer_df, use_container_width=True)

st.divider()

# Measures
st.header("Measures")

measure_counts = (
    filtered_df["Measure Group"]
    .value_counts()
    .reset_index()
)

measure_counts.columns = ["Measure Group", "Count"]

fig = px.bar(
    measure_counts,
    x="Count",
    y="Measure Group",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)

specific_measure_counts = (
    filtered_df["Specific Measure"]
    .dropna()
    .value_counts()
    .head(20)
    .reset_index()
)

specific_measure_counts.columns = ["Specific Measure", "Count"]

fig = px.bar(
    specific_measure_counts,
    x="Count",
    y="Specific Measure",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Measure Explorer")

available_groups = sorted(
    filtered_df["Measure Group"].dropna().unique()
)

if available_groups:

    selected_group = st.selectbox(
        "Select Measure Group",
        available_groups
    )

    measure_explorer = filtered_df[
        filtered_df["Measure Group"] == selected_group
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

# Participant Profile
st.header("Participant Profile")

available_participants = sorted(
    filtered_df["Country Raising"].dropna().unique()
)

if available_participants:

    selected_country = st.selectbox(
        "Select Participant",
        available_participants
    )

    country_df = filtered_df[
        filtered_df["Country Raising"] == selected_country
    ]

    st.metric(
        "Interventions",
        len(country_df)
    )

    st.dataframe(
        country_df,
        use_container_width=True
    )

st.divider()

# Database
st.header("Database")

st.dataframe(
    filtered_df,
    use_container_width=True
)
