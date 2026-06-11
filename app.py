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

# Countries chart
st.header("Inteventions by Participants")

country_counts = (
    df["Country Raising"]
    .value_counts()
    .reset_index()
)

country_counts.columns = ["Country", "Count"]

fig_country = px.bar(
    country_counts.head(15),
    x="Count",
    y="Participant",
    orientation="h"
    labels={
        "Country": "Participant",
        "Count": "Number of Interventions"
)

st.plotly_chart(fig_country, use_container_width=True)

# Tone chart
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

# WTO Body chart
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

# Data table
st.header("Database")

st.dataframe(df, use_container_width=True)
