import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from db.connection import get_session
from db.models import Job as JobDB

st.set_page_config(page_title="DE Jobs Dashboard", layout="wide")
st.title("DE Jobs Intelligence Dashboard")


def load_jobs():
    with get_session() as session:
        jobs = session.query(JobDB).filter(
            JobDB.is_active == True
        ).order_by(JobDB.ranking_score.desc()).all()

        return pd.DataFrame([
            {
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "score": job.ranking_score,
                "experience": job.experience_level,
                "source": job.source,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "beginner_friendly": job.beginner_friendly,
                "url": job.url,
                "posted_at": job.posted_at,
            }
            for job in jobs
        ])


df = load_jobs()

# sidebar filters
st.sidebar.header("filters")

role_filter = st.sidebar.selectbox(
    "role type",
    ["all", "data engineering", "product management"]
)

score_filter = st.sidebar.slider(
    "minimum score",
    min_value=0,
    max_value=100,
    value=45,
)

experience_filter = st.sidebar.multiselect(
    "experience level",
    options=["intern", "junior", "mid", "senior", "manager"],
    default=["junior", "mid"],
)

beginner_only = st.sidebar.checkbox("beginner friendly only")

# apply filters
filtered = df[df["score"] >= score_filter]

if role_filter == "data engineering":
    filtered = filtered[filtered["title"].str.lower().str.contains(
        "data engineer|analytics engineer|etl|data platform"
    )]
elif role_filter == "product management":
    filtered = filtered[filtered["title"].str.lower().str.contains(
        "product manager"
    )]

if experience_filter:
    filtered = filtered[filtered["experience"].str.lower().isin(experience_filter)]

if beginner_only:
    filtered = filtered[filtered["beginner_friendly"] == True]

# metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("total jobs", len(df))
col2.metric("filtered jobs", len(filtered))
col3.metric("strong matches (60+)", len(df[df["score"] >= 60]))
col4.metric("beginner friendly", len(df[df["beginner_friendly"] == True]))

st.divider()

# job cards
st.subheader(f"showing {len(filtered)} jobs")

for _, job in filtered.iterrows():
    score_color = "green" if job["score"] >= 60 else "orange"
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{job['title']}**")
            st.caption(f"{job['company']} | {job['location']} | {job['experience']}")
            if job["salary_min"] and job["salary_max"]:
                st.caption(f"salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
            st.caption(f"source: {job['source']}")
            st.link_button("apply now", job["url"])
        with col2:
            st.markdown(f":{score_color}[**{int(job['score'])}/100**]")
            if job["beginner_friendly"]:
                st.caption("beginner friendly")
        st.divider()