import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Trade-Related Climate and Sustainability Measures Database",
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

st.title("Trade-Related Climate and Sustainability Measures Database")

# LOAD DATA
df = pd.read_excel("TRCM_Database.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}

CHART_FONT = {"family": "Arial", "size": 14, "color": "black"}

def style_chart(fig):
    fig.update_layout(
        font=CHART_FONT,
        dragmode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def build_concern_df(dataframe):
    frames = []
    for i in range(1, 6):
        col = f"Concern {i}"
        if col in dataframe.columns:
            temp = dataframe[["Country Raising", col]].copy()
            temp.columns = ["Participant", "Concern"]
            frames.append(temp)

    if not frames:
        return pd.DataFrame(columns=["Participant", "Concern"])

    return pd.concat(frames, ignore_index=True).dropna(subset=["Concern"])

concern_df = build_concern_df(df)

# SIDEBAR FILTERS
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

# FILTER DATA
dashboard_df = df.copy()

if countries:
    dashboard_df = dashboard_df[dashboard_df["Country Raising"].isin(countries)]

if measures:
    dashboard_df = dashboard_df[dashboard_df["Measure Group"].isin(measures)]

if tones:
    dashboard_df = dashboard_df[dashboard_df["Tone"].isin(tones)]

if bodies:
    dashboard_df = dashboard_df[dashboard_df["Body"].isin(bodies)]

if concerns:
    masks = []
    for i in range(1, 6):
        col = f"Concern {i}"
        if col in dashboard_df.columns:
            masks.append(dashboard_df[col].isin(concerns))

    if masks:
        mask = masks[0]
        for m in masks[1:]:
            mask = mask | m
        dashboard_df = dashboard_df[mask]

dashboard_concern_df = build_concern_df(dashboard_df)

# ACTIVE FILTERS
active_filters = []
if countries:
    active_filters.append(f"Countries: {', '.join(countries)}")
if measures:
    active_filters.append(f"Measure Groups: {', '.join(measures)}")
if tones:
    active_filters.append(f"Tones: {', '.join(tones)}")
if bodies:
    active_filters.append(f"Bodies: {', '.join(bodies)}")
if concerns:
    active_filters.append(f"Concerns: {', '.join(concerns)}")

if active_filters:
    st.info(" | ".join(active_filters))

# DOWNLOAD BUTTON
csv = dashboard_df.to_csv(index=False)
st.download_button(
    "Download Filtered Dataset",
    csv,
    file_name="TRCSM_Filtered_Data.csv",
    mime="text/csv"
)

if dashboard_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# KPI CARDS
st.markdown("<h2>Overview</h2>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Interventions", len(dashboard_df))
c2.metric("Participants", dashboard_df["Country Raising"].nunique())
c3.metric("Measure Groups", dashboard_df["Measure Group"].nunique())
c4.metric("WTO Bodies", dashboard_df["Body"].nunique())

top_body = dashboard_df["Body"].value_counts().idxmax()
c5.metric("Most Active Body", top_body)

# KEY INSIGHTS
st.markdown("<h2>Key Insights</h2>", unsafe_allow_html=True)

dominant_tone = dashboard_df["Tone"].value_counts().idxmax()
dominant_body = dashboard_df["Body"].value_counts().idxmax()
dominant_measure = dashboard_df["Measure Group"].value_counts().idxmax()

insights = []

if len(countries) == 1:
    insights.append(f"{len(dashboard_df)} interventions by {countries[0]} during the period.")
elif len(countries) > 1:
    insights.append(f"{len(dashboard_df)} interventions by selected participants during the period.")
else:
    insights.append(f"{len(dashboard_df)} interventions during the period.")

tone_share = round(
    dashboard_df["Tone"].value_counts(normalize=True).iloc[0] * 100
)

insights.append(
    f"{dominant_tone} is the dominant intervention tone ({tone_share}% of interventions)."
)
insights.append(f"Most discussions occur in {dominant_body}.")
insights.append(f"The most discussed measure group is {dominant_measure}.")

if not dashboard_concern_df.empty:
    top_concern = dashboard_concern_df["Concern"].value_counts().idxmax()
    insights.append(f"The most frequently raised concern is {top_concern}.")

for item in insights:
    st.markdown(f"• {item}")

# TONES + WTO BODIES
left, spacer, right = st.columns([1, 0.15, 1])

with left:

    st.markdown("<h3>Intervention Tones</h3>", unsafe_allow_html=True)

    tone_counts = dashboard_df["Tone"].value_counts().reset_index()
    tone_counts.columns = ["Tone", "Number of Interventions"]

    color_map = {
        "Support": "#2E8B57",
        "Concern": "#B85C5C",
        "Mixed": "#FF8C00",
        "Neutral": "#808080"
    }

    fig = px.bar(
        tone_counts.sort_values("Number of Interventions"),
        x="Number of Interventions",
        y="Tone",
        orientation="h",
        color="Tone",
        color_discrete_map=color_map,
        text="Number of Interventions"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(style_chart(fig),
                    use_container_width=True,
                    config=PLOTLY_CONFIG)

with right:

    st.markdown("<h3>WTO Bodies</h3>", unsafe_allow_html=True)

    body_counts = dashboard_df["Body"].value_counts().reset_index()
    body_counts.columns = ["Body", "Number of Interventions"]

    fig = px.bar(
        body_counts.sort_values("Number of Interventions"),
        x="Number of Interventions",
        y="Body",
        orientation="h",
        text="Number of Interventions"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(style_chart(fig),
                    use_container_width=True,
                    config=PLOTLY_CONFIG)

# PARTICIPANTS
st.markdown("<h2>Leading Participants</h2>", unsafe_allow_html=True)

country_counts = (
    dashboard_df["Country Raising"]
    .value_counts()
    .head(10)
    .sort_values(ascending=True)
    .reset_index()
)

country_counts.columns = ["Participant", "Number of Interventions"]

fig = px.bar(
    country_counts,
    x="Number of Interventions",
    y="Participant",
    orientation="h",
    text="Number of Interventions"
)

fig.update_traces(textposition="outside")

st.plotly_chart(style_chart(fig),
                use_container_width=True,
                config=PLOTLY_CONFIG)

# CONCERNS + MEASURE GROUPS
left, spacer, right = st.columns([1, 0.15, 1])

with left:

    st.markdown("<h2>Top Concerns</h2>", unsafe_allow_html=True)

    if not dashboard_concern_df.empty:

        concern_counts = (
            dashboard_concern_df["Concern"]
            .value_counts()
            .head(20)
            .reset_index()
        )

        concern_counts.columns = ["Concern", "Number of Interventions"]

        fig = px.bar(
            concern_counts.sort_values("Number of Interventions"),
            x="Number of Interventions",
            y="Concern",
            orientation="h",
            text="Number of Interventions"
        )

        fig.update_traces(textposition="outside")

        st.plotly_chart(style_chart(fig),
                        use_container_width=True,
                        config=PLOTLY_CONFIG)

with right:

    st.markdown("<h2>Measure Groups</h2>", unsafe_allow_html=True)

    measure_counts = (
        dashboard_df["Measure Group"]
        .value_counts()
        .reset_index()
    )

    measure_counts.columns = ["Measure Group", "Number of Interventions"]

    fig = px.bar(
        measure_counts.sort_values("Number of Interventions"),
        x="Number of Interventions",
        y="Measure Group",
        orientation="h",
        text="Number of Interventions"
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(style_chart(fig),
                    use_container_width=True,
                    config=PLOTLY_CONFIG)

# DATA TABLE
with st.expander("View Filtered Data", expanded=False):
    st.dataframe(dashboard_df, use_container_width=True)

st.caption(
    "Trade-Related Climate and Sustainability Measures Database | Updated: 13 June 2026"
)
