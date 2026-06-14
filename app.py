
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="ClimaTrade Observatory",
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

st.markdown(
    """
    <div style="text-align:center; padding-bottom:20px;">
        <h1 style="margin-bottom:0;">ClimaTrade Observatory</h1>
        <h3 style="margin-top:5px; color:#555555; font-weight:400;">
            Trade-Related Climate and Sustainability Measures Database
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

if "Date" in df.columns:
    df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": False
}

CHART_FONT = {
    "family": "Arial",
    "size": 14,
    "color": "black"
}


def style_chart(fig, title=None):
    fig.update_layout(
        title={
            "text": title if title else "",
            "x": 0.5,
            "xanchor": "center"
        },
        font=CHART_FONT,
        dragmode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
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
        return pd.DataFrame(
            columns=["Participant", "Measure Group", "Concern"]
        )

    return pd.concat(
        frames,
        ignore_index=True
    ).dropna(subset=["Concern"])


concern_df = build_concern_df(df)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

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

# -----------------------------
# FILTER DATA
# -----------------------------

dashboard_df = df.copy()

if countries:
    dashboard_df = dashboard_df[
        dashboard_df["Country Raising"].isin(countries)
    ]

if measures:
    dashboard_df = dashboard_df[
        dashboard_df["Measure Group"].isin(measures)
    ]

if tones:
    dashboard_df = dashboard_df[
        dashboard_df["Tone"].isin(tones)
    ]

if bodies:
    dashboard_df = dashboard_df[
        dashboard_df["Body"].isin(bodies)
    ]

if concerns:

    masks = []

    for i in range(1, 6):
        col = f"Concern {i}"

        if col in dashboard_df.columns:
            masks.append(
                dashboard_df[col].isin(concerns)
            )

    if masks:
        mask = masks[0]

        for m in masks[1:]:
            mask = mask | m

        dashboard_df = dashboard_df[mask]

dashboard_concern_df = build_concern_df(dashboard_df)

if dashboard_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# -----------------------------
# DOWNLOAD
# -----------------------------

csv = dashboard_df.to_csv(index=False)

st.download_button(
    "Download Filtered Dataset",
    csv,
    file_name="TRCSM_Filtered_Data.csv",
    mime="text/csv"
)

# -----------------------------
# OVERVIEW
# -----------------------------

st.markdown("<h2>Overview</h2>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Interventions", len(dashboard_df))
c2.metric("Participants", dashboard_df["Country Raising"].nunique())
c3.metric("Measure Groups", dashboard_df["Measure Group"].nunique())
c4.metric("WTO Bodies", dashboard_df["Body"].nunique())
c5.metric(
    "Most Active Body",
    dashboard_df["Body"].value_counts().idxmax()
)

# -----------------------------
# KEY INSIGHTS
# -----------------------------

st.markdown("<h2>Key Insights</h2>", unsafe_allow_html=True)

insights = [
    f"{len(dashboard_df)} interventions in the filtered dataset.",
    f"Most active WTO body: {dashboard_df['Body'].value_counts().idxmax()}.",
    f"Most discussed measure group: {dashboard_df['Measure Group'].value_counts().idxmax()}.",
    f"Dominant tone: {dashboard_df['Tone'].value_counts().idxmax()}."
]

for item in insights:
    st.markdown(f"• {item}")

# -----------------------------
# DISTRIBUTION
# -----------------------------

left, right = st.columns(2)

with left:

    st.markdown("<h3>Intervention Tones</h3>", unsafe_allow_html=True)

    tone_counts = (
        dashboard_df["Tone"]
        .value_counts()
        .reset_index()
    )

    tone_counts.columns = ["Tone", "Count"]

    tone_colors = {
        "Support": "#2E8B57",
        "Supportive": "#2E8B57",
        "Concern": "#C0392B",
        "Concerns": "#C0392B",
        "Mixed": "#808080"
    }

    fig = px.bar(
        tone_counts.sort_values("Count"),
        x="Count",
        y="Tone",
        orientation="h",
        color="Tone",
        color_discrete_map=tone_colors
    )

    st.plotly_chart(
        style_chart(fig, "Intervention Tones"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

with right:

    st.markdown("<h3>WTO Bodies</h3>", unsafe_allow_html=True)

    body_counts = (
        dashboard_df["Body"]
        .value_counts()
        .reset_index()
    )

    body_counts.columns = ["Body", "Count"]

    fig = px.bar(
        body_counts.sort_values("Count"),
        x="Count",
        y="Body",
        orientation="h"
    )

    st.plotly_chart(
        style_chart(fig, "WTO Bodies"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# -----------------------------
# PARTICIPANTS
# -----------------------------

st.markdown("<h2>Leading Participants</h2>", unsafe_allow_html=True)

country_counts = (
    dashboard_df["Country Raising"]
    .value_counts()
    .head(10)
    .sort_values()
    .reset_index()
)

country_counts.columns = ["Participant", "Count"]

fig = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h"
)

st.plotly_chart(
    style_chart(fig, "Leading Participants"),
    use_container_width=True,
    config=PLOTLY_CONFIG
)

# -----------------------------
# CONCERNS
# -----------------------------

st.markdown("<h2>Top Concerns</h2>", unsafe_allow_html=True)

if not dashboard_concern_df.empty:

    concern_counts = (
        dashboard_concern_df["Concern"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    concern_counts.columns = ["Concern", "Count"]

    fig = px.bar(
        concern_counts.sort_values("Count"),
        x="Count",
        y="Concern",
        orientation="h"
    )

    st.plotly_chart(
        style_chart(fig, "Top Concerns"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# -----------------------------
# MEASURES & RELATIONSHIPS
# -----------------------------

st.markdown("<h2>Measures & Relationships</h2>", unsafe_allow_html=True)

left, spacer, right = st.columns([1, 0.30, 1])

with left:

    st.markdown("<h3>Specific Measure Explorer</h3>", unsafe_allow_html=True)

    selected_group = st.selectbox(
        "Measure Group",
        sorted(dashboard_df["Measure Group"].dropna().unique())
    )

    measure_df = dashboard_df[
        dashboard_df["Measure Group"] == selected_group
    ]

    specific_counts = (
        measure_df["Specific Measure"]
        .value_counts()
        .head(15)
        .reset_index()
    )

    specific_counts.columns = [
        "Specific Measure",
        "Count"
    ]

    fig = px.bar(
        specific_counts.sort_values("Count"),
        x="Count",
        y="Specific Measure",
        orientation="h"
    )

    st.plotly_chart(
        style_chart(fig, "Specific Measures"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

with right:

    st.markdown("<h3>Participants by Measure Group</h3>", unsafe_allow_html=True)

    country_measure = pd.crosstab(
        dashboard_df["Country Raising"],
        dashboard_df["Measure Group"]
    )

    country_measure = country_measure.sort_values(
        by=country_measure.columns.tolist(),
        ascending=False
    ).head(15)

    fig = px.bar(
        country_measure.reset_index(),
        y="Country Raising",
        x=country_measure.columns,
        orientation="h"
    )

    st.plotly_chart(
        style_chart(fig, "Participants by Measure Group"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

st.markdown("---")
st.markdown("<h3>Concerns by Measure Group</h3>", unsafe_allow_html=True)

if not dashboard_concern_df.empty:

    concern_measure = pd.crosstab(
        dashboard_concern_df["Concern"],
        dashboard_concern_df["Measure Group"]
    )

    concern_measure = concern_measure.head(15)

    fig = px.bar(
        concern_measure.reset_index(),
        y="Concern",
        x=concern_measure.columns,
        orientation="h"
    )

    st.plotly_chart(
        style_chart(fig, "Concerns by Measure Group"),
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# -----------------------------
# DATA TABLE
# -----------------------------

with st.expander(
    "View Filtered Data",
    expanded=False
):
    st.dataframe(
        dashboard_df,
        use_container_width=True
    )

# -----------------------------
# FOOTER
# -----------------------------

st.caption(
    "ClimaTrade Observatory | Last updated: 13 June 2026"
)
