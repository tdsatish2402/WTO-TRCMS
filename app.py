
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Trade-Related Climate and Sustainability Measures Database",
    layout="wide"
)

st.title("Trade-Related Climate and Sustainability Measures Database")

df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# -----------------------------
# Sidebar filters (database level)
# -----------------------------

st.sidebar.header("Database Filters")

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

# -----------------------------
# Concern dataset
# -----------------------------

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

# -----------------------------
# Overview
# -----------------------------

st.header("Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Interventions", len(filtered_df))
c2.metric("Participants", filtered_df["Country Raising"].nunique())
c3.metric("Measure Groups", filtered_df["Measure Group"].nunique())

# -----------------------------
# NEW ANALYSIS PANEL
# -----------------------------

st.divider()
st.header("Interactive Analysis Filters")

available_concerns = []

if not concern_df.empty:
    available_concerns = sorted(concern_df["Concern"].dropna().unique())

with st.expander("Filter Dashboard Visualisations", expanded=True):

    a1, a2, a3 = st.columns(3)

    with a1:
        analysis_countries = st.multiselect(
            "Countries",
            sorted(filtered_df["Country Raising"].dropna().unique())
        )

    with a2:
        analysis_measures = st.multiselect(
            "Measure Groups",
            sorted(filtered_df["Measure Group"].dropna().unique())
        )

    with a3:
        analysis_tones = st.multiselect(
            "Tones",
            sorted(filtered_df["Tone"].dropna().unique())
        )

    b1, b2 = st.columns(2)

    with b1:
        analysis_bodies = st.multiselect(
            "WTO Bodies",
            sorted(filtered_df["Body"].dropna().unique())
        )

    with b2:
        analysis_concerns = st.multiselect(
            "Concerns",
            available_concerns
        )

dashboard_df = filtered_df.copy()

if analysis_countries:
    dashboard_df = dashboard_df[
        dashboard_df["Country Raising"].isin(analysis_countries)
    ]

if analysis_measures:
    dashboard_df = dashboard_df[
        dashboard_df["Measure Group"].isin(analysis_measures)
    ]

if analysis_tones:
    dashboard_df = dashboard_df[
        dashboard_df["Tone"].isin(analysis_tones)
    ]

if analysis_bodies:
    dashboard_df = dashboard_df[
        dashboard_df["Body"].isin(analysis_bodies)
    ]

# rebuild concern dataframe for dashboard filters

dashboard_concern_frames = []

for i in range(1, 6):
    col_name = f"Concern {i}"

    if col_name in dashboard_df.columns:
        temp = dashboard_df[["Country Raising", col_name]].copy()
        temp.columns = ["Participant", "Concern"]
        dashboard_concern_frames.append(temp)

if dashboard_concern_frames:
    dashboard_concern_df = pd.concat(
        dashboard_concern_frames,
        ignore_index=True
    ).dropna(subset=["Concern"])
else:
    dashboard_concern_df = pd.DataFrame(
        columns=["Participant", "Concern"]
    )

if analysis_concerns and not dashboard_concern_df.empty:

    valid_rows = set()

    for idx, row in dashboard_df.iterrows():
        for i in range(1, 6):
            col = f"Concern {i}"

            if (
                col in dashboard_df.columns
                and row.get(col) in analysis_concerns
            ):
                valid_rows.add(idx)

    dashboard_df = dashboard_df.loc[list(valid_rows)]

# -----------------------------
# Charts use dashboard_df
# -----------------------------

left, right = st.columns(2)

with left:

    st.subheader("Tone Distribution")

    tone_counts = dashboard_df["Tone"].value_counts().reset_index()
    tone_counts.columns = ["Tone", "Count"]

    fig = px.pie(
        tone_counts,
        names="Tone",
        values="Count",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

with right:

    st.subheader("WTO Bodies")

    body_counts = dashboard_df["Body"].value_counts().reset_index()
    body_counts.columns = ["Body", "Count"]

    fig = px.bar(
        body_counts,
        x="Body",
        y="Count",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.header("Participants")

country_counts = (
    dashboard_df["Country Raising"]
    .value_counts()
    .head(15)
    .reset_index()
)

country_counts.columns = ["Participant", "Count"]

fig = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.header("Concerns")

if not dashboard_concern_df.empty:

    concern_counts = (
        dashboard_concern_df["Concern"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    concern_counts.columns = ["Concern", "Count"]

    fig = px.bar(
        concern_counts,
        x="Count",
        y="Concern",
        orientation="h",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.header("Measures")

measure_counts = (
    dashboard_df["Measure Group"]
    .value_counts()
    .reset_index()
)

measure_counts.columns = ["Measure Group", "Count"]

fig = px.bar(
    measure_counts,
    x="Count",
    y="Measure Group",
    orientation="h",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.header("Database")

st.dataframe(
    dashboard_df,
    use_container_width=True
)
