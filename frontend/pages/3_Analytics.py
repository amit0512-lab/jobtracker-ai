import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.api import get_dashboard, get_timeline
from components.auth import show_logout_button

if not st.session_state.get("logged_in"):
    st.warning("Pehle login karo"); st.stop()

show_logout_button()
st.markdown("## 📊 Analytics Dashboard")

# ─── Data Fetch ───────────────────────────────────────────────
with st.spinner("Dashboard load ho raha hai..."):
    res = get_dashboard()

if res.status_code != 200:
    st.error("Dashboard load nahi hua"); st.stop()

data = res.json()
summary = data["summary"]

# ─── Summary Cards ────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💼 Total Jobs",    summary["total_jobs"])
c2.metric("📄 Resumes",       summary["total_resumes"])
c3.metric("📬 Applied (30d)", summary["recent_applications_30d"])
c4.metric("🎯 Avg Score",     f"{summary['avg_resume_match_score']}%")
c5.metric("🏆 Best Score",    f"{summary['best_resume_score']}%")

st.divider()

# ─── Row 1: Status + Priority ─────────────────────────────────
row1_c1, row1_c2 = st.columns(2)

with row1_c1:
    st.markdown("#### Application Status Breakdown")
    status_data = data["status_breakdown"]
    if status_data:
        fig = px.pie(
            values=list(status_data.values()),
            names=list(status_data.keys()),
            hole=0.5,
            color_discrete_sequence=["#6C63FF","#FFA500","#00D4AA","#FF4B4B","#4ECDC4"]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            showlegend=True,
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Abhi koi data nahi")

with row1_c2:
    st.markdown("#### Priority Breakdown")
    priority_data = data["priority_breakdown"]
    if priority_data:
        fig2 = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            color=list(priority_data.keys()),
            color_discrete_map={"high": "#FF4B4B", "medium": "#FFA500", "low": "#00D4AA"}
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            showlegend=False,
            margin=dict(t=10, b=10),
            xaxis_title="Priority",
            yaxis_title="Count"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Abhi koi data nahi")

# ─── Row 2: Weekly Activity ───────────────────────────────────
st.markdown("#### 📅 Last 7 Days Activity")
weekly = data.get("weekly_activity", [])
if weekly:
    df = pd.DataFrame(weekly)
    fig3 = px.area(
        df, x="date", y="jobs_added",
        color_discrete_sequence=["#6C63FF"]
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        margin=dict(t=10, b=10),
        xaxis_title="", yaxis_title="Jobs Added"
    )
    fig3.update_traces(fill='tozeroy', line_color='#6C63FF')
    st.plotly_chart(fig3, use_container_width=True)

# ─── Row 3: Conversion Rates + Top Companies ──────────────────
row3_c1, row3_c2 = st.columns(2)

with row3_c1:
    st.markdown("#### 🔄 Conversion Funnel")
    conv = data["conversion_rates"]
    funnel_data = {
        "Stage": ["Applied", "Got Interview", "Got Offer"],
        "Rate %": [
            conv["applied_rate"],
            conv["interview_rate"],
            conv["offer_rate"]
        ]
    }
    fig4 = go.Figure(go.Funnel(
        y=funnel_data["Stage"],
        x=funnel_data["Rate %"],
        marker_color=["#6C63FF", "#00D4AA", "#FFA500"]
    ))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig4, use_container_width=True)

with row3_c2:
    st.markdown("#### 🏢 Top Companies")
    companies = data.get("top_companies", [])
    if companies:
        df_comp = pd.DataFrame(companies)
        fig5 = px.bar(
            df_comp, x="count", y="company",
            orientation="h",
            color="count",
            color_continuous_scale=["#1A1D27", "#6C63FF"]
        )
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            showlegend=False,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
            xaxis_title="Applications",
            yaxis_title=""
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Abhi koi data nahi")

# ─── Timeline ─────────────────────────────────────────────────
st.divider()
st.markdown("#### 🕒 Application Timeline")
tl_res = get_timeline()
if tl_res.status_code == 200:
    timeline = tl_res.json()
    if timeline:
        df_tl = pd.DataFrame(timeline)
        df_tl = df_tl[["title", "company", "status", "applied_at"]]
        df_tl.columns = ["Title", "Company", "Status", "Applied On"]
        df_tl["Applied On"] = df_tl["Applied On"].str[:10]
        st.dataframe(df_tl, use_container_width=True, hide_index=True)
    else:
        st.info("Abhi koi applications nahi hain")