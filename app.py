import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------

# PAGE CONFIG

# ------------------------------

st.set_page_config(
page_title="WTO Trade Concerns Dashboard",
layout="wide"
)

st.title("WTO Trade Concerns Dashboard")

# ------------------------------

# LOAD DATA

# ------------------------------

df = pd.read_excel("TRCM_Database.xlsx")

# ------------------------------

# SIDEBAR FILTERS

# ------------------------------

st.sidebar.header("Filters")

countries = sorted(df["Country Raising"].dropna().unique())
measure_groups = sorted(df["Measure Group"].dropna().unique())
tones = sorted(df["Tone"].dropna().unique())

selected_countries = st.sidebar.multiselect(
"Country Raising",
countries,
default=countries
)

selected_measures = st.sidebar.multiselect(
"Measure Group",
measure_groups,
default=measure_groups
)

selected_tones = st.sidebar.multiselect(
"Tone",
tones,
default=tones
)

filtered = df[
(df["Country Raising"].isin(selected_countries))
& (df["Measure Group"].isin(selected_measures))
& (df["Tone"].isin(selected_tones))
]

# ------------------------------

# KPI CARDS

# ------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
"Interventions",
len(filtered)
)

col2.metric(
"Countries",
filtered["Country Raising"].nunique()
)

col3.metric(
"Measure Groups",
filtered["Measure Group"].nunique()
)

concerns = []

    for col in [
    "Concern 1",
    "Concern 2",
    "Concern 3",
    "Concern 4",
    "Concern 5"
]:
concerns.extend(filtered[col].dropna().tolist())

col4.metric(
"Unique Concerns",
len(set(concerns))
)

st.divider()

# ------------------------------

# COUNTRY CHART

# ------------------------------

st.subheader("Countries Raising Concerns")

country_counts = (
filtered["Country Raising"]
.value_counts()
.head(15)
.reset_index()
)

country_counts.columns = [
"Country",
"Count"
]

fig_country = px.bar(
country_counts,
x="Count",
y="Country",
orientation="h"
)

st.plotly_chart(
fig_country,
use_container_width=True
)

# ------------------------------

# TWO COLUMN CHARTS

# ------------------------------

left, right = st.columns(2)

with left:

```
st.subheader("Tone Distribution")

tone_counts = (
    filtered["Tone"]
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
st.subheader("Measure Groups")

measure_counts = (
    filtered["Measure Group"]
    .value_counts()
    .head(15)
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
```

# ------------------------------

# CONCERNS ANALYSIS

# ------------------------------

st.subheader("Top Concerns")

all_concerns = pd.concat([
filtered["Concern 1"],
filtered["Concern 2"],
filtered["Concern 3"],
filtered["Concern 4"],
filtered["Concern 5"]
])

all_concerns = all_concerns.dropna()

concern_counts = (
all_concerns
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

# ------------------------------

# DATA EXPLORER

# ------------------------------

st.subheader("Data Explorer")

st.dataframe(
filtered,
use_container_width=True
)
