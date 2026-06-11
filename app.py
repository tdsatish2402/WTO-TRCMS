import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================

# PAGE SETTINGS

# =====================================================

st.set_page_config(
page_title="WTO Trade Concerns Dashboard",
layout="wide"
)

st.title("WTO Trade Concerns Dashboard")

# =====================================================

# LOAD DATA

# =====================================================

df = pd.read_excel("TRCM_Database.xlsx")

# =====================================================

# OVERVIEW

# =====================================================

st.header("Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
"Total Interventions",
len(df)
)

col2.metric(
"Participants",
df["Country Raising"].nunique()
)

col3.metric(
"Measure Groups",
df["Measure Group"].nunique()
)

col_left, col_right = st.columns(2)

with col_left:

```
st.subheader("Tone Distribution")

tone_counts = (
    df["Tone"]
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

with col_right:

```
st.subheader("WTO Bodies")

body_counts = (
    df["Body"]
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
    y="Count",
    labels={
        "Count": "Number of Interventions"
    }
)

st.plotly_chart(
    fig_body,
    use_container_width=True
)
```

st.divider()

# =====================================================

# PARTICIPANTS

# =====================================================

st.header("Participants")

country_counts = (
df["Country Raising"]
.value_counts()
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
orientation="h",
labels={
"Count": "Number of Interventions",
"Participant": "Participant"
}
)

st.plotly_chart(
fig_country,
use_container_width=True
)

st.divider()

# =====================================================

# CONCERNS

# =====================================================

st.header("Concerns")

# Top Concern Families

st.subheader("Top Concern Families")

all_concerns = pd.concat([
df["Concern 1"],
df["Concern 2"],
df["Concern 3"],
df["Concern 4"],
df["Concern 5"]
])

all_concerns = all_concerns.dropna()

concern_counts = (
all_concerns
.value_counts()
.reset_index()
)

concern_counts.columns = [
"Concern",
"Count"
]

fig_concerns = px.bar(
concern_counts.head(20),
x="Count",
y="Concern",
orientation="h",
labels={
"Count": "Number of Mentions",
"Concern": "Concern Family"
}
)

st.plotly_chart(
fig_concerns,
use_container_width=True
)

# Top Sub-Concerns

st.subheader("Top Sub-Concerns")

all_subconcerns = pd.concat([
df["Sub-Concern 1"],
df["Sub-Concern 2"],
df["Sub-Concern 3"],
df["Sub-Concern 4"],
df["Sub-Concern 5"]
])

all_subconcerns = all_subconcerns.dropna()

subconcern_counts = (
all_subconcerns
.value_counts()
.reset_index()
)

subconcern_counts.columns = [
"SubConcern",
"Count"
]

fig_subconcerns = px.bar(
subconcern_counts.head(20),
x="Count",
y="SubConcern",
orientation="h",
labels={
"Count": "Number of Mentions",
"SubConcern": "Sub-Concern"
}
)

st.plotly_chart(
fig_subconcerns,
use_container_width=True
)

# Participant x Concern Heatmap

st.subheader("Participant × Concern Family")

heatmap_concern = pd.crosstab(
df["Country Raising"],
df["Concern 1"]
)

fig_heatmap_concern = px.imshow(
heatmap_concern,
aspect="auto",
labels=dict(
x="Concern Family",
y="Participant",
color="Count"
)
)

st.plotly_chart(
fig_heatmap_concern,
use_container_width=True
)

st.divider()

# =====================================================

# MEASURES

# =====================================================

st.header("Measures")

# Measure Groups

st.subheader("Measure Groups")

measure_counts = (
df["Measure Group"]
.value_counts()
.reset_index()
)

measure_counts.columns = [
"MeasureGroup",
"Count"
]

fig_measure_group = px.bar(
measure_counts,
x="Count",
y="MeasureGroup",
orientation="h",
labels={
"Count": "Number of Interventions",
"MeasureGroup": "Measure Group"
}
)

st.plotly_chart(
fig_measure_group,
use_container_width=True
)

# Specific Measures

st.subheader("Specific Measures")

specific_measure_counts = (
df["Specific Measure"]
.value_counts()
.head(20)
.reset_index()
)

specific_measure_counts.columns = [
"SpecificMeasure",
"Count"
]

fig_specific = px.bar(
specific_measure_counts,
x="Count",
y="SpecificMeasure",
orientation="h",
labels={
"Count": "Number of Interventions",
"SpecificMeasure": "Specific Measure"
}
)

st.plotly_chart(
fig_specific,
use_container_width=True
)

# Participant x Measure Group Heatmap

st.subheader("Participant × Measure Group")

heatmap_measure = pd.crosstab(
df["Country Raising"],
df["Measure Group"]
)

fig_heatmap_measure = px.imshow(
heatmap_measure,
aspect="auto",
labels=dict(
x="Measure Group",
y="Participant",
color="Count"
)
)

st.plotly_chart(
fig_heatmap_measure,
use_container_width=True
)

st.divider()

# =====================================================

# DATABASE

# =====================================================

st.header("Database")

st.dataframe(
df,
use_container_width=True
)
