
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ClimaTrade Observatory", layout="wide")

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.block-container {max-width: 1450px; padding-top: 1rem;}
[data-testid="metric-container"]{
border:1px solid #e5e7eb;
padding:12px;
border-radius:10px;
background:#fafafa;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;">
<h1 style="color:#9A05A9;">ClimaTrade Observatory</h1>
<h3 style="font-weight:400;color:#666;">
Trade-Related Climate and Sustainability Measures Database
</h3>
<p style="max-width:1000px;margin:auto;color:#666;">
Tracking governance interactions concerning trade-related climate and sustainability measures across WTO forums.
</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
df = pd.read_excel("ClimaTrade_Observatory.xlsx")
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

dimension_cols = [c for c in df.columns if "Governance_Dimension_" in c]
topic_cols = [c for c in df.columns if "Governance_Topic_" in c]

def melt_dimensions(data):
    frames = []
    for col in dimension_cols:
        tmp = data[[col]].copy()
        tmp.columns = ["Dimension"]
        frames.append(tmp)
    return pd.concat(frames).dropna()

def melt_topics(data):
    frames = []
    for col in topic_cols:
        tmp = data[[col]].copy()
        tmp.columns = ["Topic"]
        frames.append(tmp)
    return pd.concat(frames).dropna()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Filters")

forums = st.sidebar.multiselect(
    "WTO Forum",
    sorted(df["WTO_Forum"].dropna().unique())
)

measures = st.sidebar.multiselect(
    "Measure",
    sorted(df["Measure"].dropna().unique())
)

owners = st.sidebar.multiselect(
    "Measure Owner",
    sorted(df["Measure_Owner"].dropna().unique())
)

functions = st.sidebar.multiselect(
    "Engagement Function",
    sorted(df["Engagement_Function"].dropna().unique())
)

filtered = df.copy()

if forums:
    filtered = filtered[filtered["WTO_Forum"].isin(forums)]

if measures:
    filtered = filtered[filtered["Measure"].isin(measures)]

if owners:
    filtered = filtered[filtered["Measure_Owner"].isin(owners)]

if functions:
    filtered = filtered[filtered["Engagement_Function"].isin(functions)]

if filtered.empty:
    st.warning("No records match selected filters.")
    st.stop()

dimensions_long = melt_dimensions(filtered)
topics_long = melt_topics(filtered)

# -----------------------------
# KPI
# -----------------------------
c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("Governance Interactions", len(filtered))
c2.metric("Measures", filtered["Measure"].nunique())
c3.metric("Measure Owners", filtered["Measure_Owner"].nunique())
c4.metric("WTO Forums", filtered["WTO_Forum"].nunique())
c5.metric("Governance Topics", topics_long["Topic"].nunique())
c6.metric("Governance Dimensions", dimensions_long["Dimension"].nunique())

# -----------------------------
# AI STYLE INSIGHTS
# -----------------------------
st.markdown(
    "<h2 style='color:#9A05A9;'>WTO Climate Governance Monitor</h2>",
    unsafe_allow_html=True
)

top_measure = filtered["Measure"].value_counts().idxmax()
top_forum = filtered["WTO_Forum"].value_counts().idxmax()
top_dimension = dimensions_long["Dimension"].value_counts().idxmax()
top_topic = topics_long["Topic"].value_counts().idxmax()

st.info(
    f"""
• Most discussed measure: {top_measure}

• Most active WTO forum: {top_forum}

• Dominant governance dimension: {top_dimension}

• Most recurring governance topic: {top_topic}
"""
)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Governance Landscape",
    "Governance Functions",
    "Governance Issues",
    "WTO Governance Architecture",
    "Interaction Explorer"
])

with tab1:

    left,right = st.columns(2)

    with left:
        measure_counts = filtered["Measure"].value_counts().head(15)
        fig = px.bar(
            measure_counts.sort_values(),
            orientation="h",
            title="Most Discussed Measures"
        )
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title="No. of Discussions")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        forum_counts = filtered["WTO_Forum"].value_counts()
        fig = px.pie(
            values=forum_counts.values,
            names=forum_counts.index,
            title="Distribution Across WTO Forums"
        )
        st.plotly_chart(fig, use_container_width=True)

    owner_counts = (
        filtered["Measure_Owner"]
        .value_counts()
        .reset_index()
    )
    owner_counts.columns = ["Owner","Count"]

    fig = px.bar(
        owner_counts,
        x="Count",
        y="Owner",
        orientation="h",
        title="Measure Owners"
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="No. of Discussions")
    st.plotly_chart(fig, use_container_width=True)

with tab2:

    func_counts = (
        filtered["Engagement_Function"]
        .value_counts()
        .reset_index()
    )
    func_counts.columns = ["Function","Count"]

    fig = px.bar(
        func_counts,
        x="Count",
        y="Function",
        orientation="h",
        title="Engagement Functions"
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="No. of Discussions")
    st.plotly_chart(fig, use_container_width=True)

    heat = pd.crosstab(
        filtered["WTO_Forum"],
        filtered["Engagement_Function"]
    )

    fig = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        title="Forum × Engagement Function"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:

    dim_counts = (
        dimensions_long["Dimension"]
        .value_counts()
        .reset_index()
    )
    dim_counts.columns = ["Dimension","Count"]

    fig = px.treemap(
        dim_counts,
        path=["Dimension"],
        values="Count",
        title="Governance Dimensions"
    )
    st.plotly_chart(fig, use_container_width=True)

    topic_counts = (
        topics_long["Topic"]
        .value_counts()
        .head(20)
        .reset_index()
    )
    topic_counts.columns = ["Topic","Count"]

    fig = px.bar(
        topic_counts.sort_values("Count"),
        x="Count",
        y="Topic",
        orientation="h",
        title="Top Governance Topics"
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="No. of Discussions")
    st.plotly_chart(fig, use_container_width=True)

with tab4:

    records = []

    for _, row in filtered.iterrows():
        forum = row["WTO_Forum"]

        for col in dimension_cols:
            if pd.notna(row[col]):
                records.append([forum, row[col]])

    arch = pd.DataFrame(records, columns=["Forum","Dimension"])

    heat = pd.crosstab(
        arch["Forum"],
        arch["Dimension"]
    )

    fig = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        title="Forum × Governance Dimension"
    )
    st.plotly_chart(fig, use_container_width=True)

    measure_forum = pd.crosstab(
        filtered["WTO_Forum"],
        filtered["Measure"]
    )

    fig = px.imshow(
        measure_forum,
        aspect="auto",
        title="Forum × Measure Matrix"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab5:

    search = st.text_input(
        "Search Interaction Summaries"
    )

    explorer = filtered.copy()

    if search:
        explorer = explorer[
            explorer["Interaction_Summary"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    st.dataframe(
        explorer[[
            "Interaction_ID",
            "WTO_Forum",
            "Measure",
            "Measure_Owner",
            "Engagement_Function",
            "Interaction_Summary",
            "WTO_Document"
        ]],
        use_container_width=True
    )

st.markdown("---")
st.caption("ClimaTrade Observatory v2.0 | Governance Interaction Framework")
