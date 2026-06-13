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

# Remove empty Excel artifact column if present

df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

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

# BUILD CONCERN DATASET

# ==================================================

concern_frames = []

for i in range(1, 6):

```
temp = filtered_df[
    [
        "Country Raising",
        f"Concern {i}"
    ]
].copy()

temp.columns = [
    "Participant",
    "Concern"
]

concern_frames.append(temp)
```

concern_df = pd.concat(
concern_frames,
ignore_index=True
)

concern_df = concern_df.dropna()

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

```
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
```

with right:

```
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
```

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

# CONCERNS

# ==================================================

st.header("Concerns")

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

fig_concern = px.bar(
concern_counts,
x="Count",
y="Concern",
orientation="h"
)

st.plotly_chart(
fig_concern,
use_container_width=True
)

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

participant_counts.columns = [
"Participant",
"Count"
]

fig_concern_participants = px.bar(
participant_counts,
x="Count",
y="Participant",
orientation="h"
)

st.plotly_chart(
fig_concern_participants,
use_container_width=True
)

st.dataframe(
explorer_df,
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

fig_measure = px.bar(
measure_counts,
x="Count",
y="Measure Group",
orientation="h"
)

st.plotly_chart(
fig_measure,
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

st.metric(
"Interventions",
len(country_df)
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
