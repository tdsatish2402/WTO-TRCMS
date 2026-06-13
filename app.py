
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Trade-Related Climate and Sustainability Measures Database",
    layout="wide"
)

st.title("Trade-Related Climate and Sustainability Measures Database")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# --------------------------------------------------
# STYLING
# --------------------------------------------------

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False
}

CHART_FONT = {
    "family": "Arial",
    "size": 14,
    "color": "black"
}

def style_chart(fig):

    fig.update_layout(
        font=CHART_FONT,
        dragmode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    fig.update_xaxes(
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        showgrid=False
    )

    fig.update_yaxes(
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        showgrid=False
    )

    return fig

# --------------------------------------------------
# CONCERNS
# --------------------------------------------------

def build_concern_df(dataframe):

    frames = []

    for i in range(1, 6):

        col = f"Concern {i}"

        if col in dataframe.columns:

            temp = dataframe[["Country Raising", col]].copy()

            temp.columns = [
                "Participant",
                "Concern"
            ]

            frames.append(temp)

    if not frames:
        return pd.DataFrame(
            columns=["Participant", "Concern"]
        )

    return (
        pd.concat(frames, ignore_index=True)
        .dropna(subset=["Concern"])
    )

concern_df = build_concern_df(df)

# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

st.header("Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Interventions", len(df))
c2.metric("Participants", df["Country Raising"].nunique())
c3.metric("Measure Groups", df["Measure Group"].nunique())

# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.divider()

with st.expander("Filters", expanded=True):

    st.caption(
        "Select one or more filters to update all visualisations."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        countries = st.multiselect(
            "Countries",
            sorted(
                df["Country Raising"]
                .dropna()
                .unique()
            )
        )

    with col2:

        measures = st.multiselect(
            "Measure Groups",
            sorted(
                df["Measure Group"]
                .dropna()
                .unique()
            )
        )

    with col3:

        tones = st.multiselect(
            "Tones",
            sorted(
                df["Tone"]
                .dropna()
                .unique()
            )
        )

    col4, col5 = st.columns(2)

    with col4:

        bodies = st.multiselect(
            "WTO Bodies",
            sorted(
                df["Body"]
                .dropna()
                .unique()
            )
        )

    with col5:

        concerns = st.multiselect(
            "Concerns",
            sorted(
                concern_df["Concern"]
                .dropna()
                .unique()
            )
        )

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

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

dashboard_concern_df = build_concern_df(
    dashboard_df
)

# --------------------------------------------------
# TONE DISTRIBUTION + WTO BODIES
# --------------------------------------------------

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("Tone Distribution")

    tone_counts = (
        dashboard_df["Tone"]
        .value_counts()
        .reset_index()
    )

    tone_counts.columns = ["Tone", "Count"]

    fig = px.pie(
        tone_counts,
        names="Tone",
        values="Count",
        hole=0.55
    )

    fig = style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

with right:

    st.subheader("WTO Bodies")

    body_counts = (
        dashboard_df["Body"]
        .value_counts()
        .reset_index()
    )

    body_counts.columns = ["Body", "Count"]

    fig = px.bar(
        body_counts,
        x="Body",
        y="Count"
    )

    fig = style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# --------------------------------------------------
# PARTICIPANTS
# --------------------------------------------------

st.divider()

st.header("Leading Participants")

country_counts = (
    dashboard_df["Country Raising"]
    .value_counts()
    .head(10)
    .sort_values(ascending=True)
    .reset_index()
)

country_counts.columns = [
    "Participant",
    "Count"
]

fig = px.bar(
    country_counts,
    x="Count",
    y="Participant",
    orientation="h"
)

fig = style_chart(fig)

st.plotly_chart(
    fig,
    use_container_width=True,
    config=PLOTLY_CONFIG
)

# --------------------------------------------------
# CONCERNS
# --------------------------------------------------

st.divider()

st.header("Top Concerns")

if not dashboard_concern_df.empty:

    concern_counts = (
        dashboard_concern_df["Concern"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    concern_counts.columns = [
        "Concern",
        "Count"
    ]

    fig = px.bar(
        concern_counts.sort_values("Count"),
        x="Count",
        y="Concern",
        orientation="h"
    )

    fig = style_chart(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

# --------------------------------------------------
# MEASURE GROUPS
# --------------------------------------------------

st.divider()

st.header("Measure Groups")

measure_counts = (
    dashboard_df["Measure Group"]
    .value_counts()
    .reset_index()
)

measure_counts.columns = [
    "Measure Group",
    "Count"
]

fig = px.bar(
    measure_counts.sort_values("Count"),
    x="Count",
    y="Measure Group",
    orientation="h"
)

fig = style_chart(fig)

st.plotly_chart(
    fig,
    use_container_width=True,
    config=PLOTLY_CONFIG
)

# --------------------------------------------------
# DOWNLOAD DATA
# --------------------------------------------------

st.divider()

with st.expander(
    "View and Download Filtered Data",
    expanded=False
):

    st.dataframe(
        dashboard_df,
        use_container_width=True
    )

    csv = dashboard_df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )
