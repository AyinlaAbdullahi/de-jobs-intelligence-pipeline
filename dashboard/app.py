import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import math
import streamlit as st
import pandas as pd
from datetime import datetime
from db.connection import get_session
from db.models import Job as JobDB, RawJob as RawJobDB

st.set_page_config(page_title="Job Intelligence", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    .stApp {
        background-color: #12283F;
        background-image:
            repeating-linear-gradient(0deg, rgba(244,237,225,0.05) 0px, rgba(244,237,225,0.05) 1px, transparent 1px, transparent 32px),
            repeating-linear-gradient(90deg, rgba(244,237,225,0.05) 0px, rgba(244,237,225,0.05) 1px, transparent 1px, transparent 32px);
    }
    section[data-testid="stSidebar"] {
        background-color: #0E1E30;
        border-right: 1px solid rgba(244,237,225,0.15);
    }
    section[data-testid="stSidebar"] * {
        color: #F4EDE1 !important;
    }
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        color: #F4EDE1;
    }
    .spec {
        font-family: 'Space Mono', monospace;
    }
    .title-block {
        border: 1px solid rgba(244,237,225,0.3);
        border-left: 3px solid #D98953;
        padding: 20px 24px;
        margin-bottom: 26px;
        background-color: rgba(18,40,63,0.6);
    }
    .title-block-main {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .title-block-sub {
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        color: rgba(244,237,225,0.6);
        letter-spacing: 0.5px;
    }
    .readout-strip {
        display: flex;
        border: 1px solid rgba(244,237,225,0.25);
        margin-bottom: 24px;
    }
    .readout-cell {
        flex: 1;
        padding: 14px 18px;
        border-right: 1px solid rgba(244,237,225,0.25);
    }
    .readout-cell:last-child { border-right: none; }
    .readout-label {
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        color: rgba(244,237,225,0.55);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .readout-value {
        font-family: 'Space Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: #F4EDE1;
    }
    .job-card {
        background-color: rgba(22,50,77,0.55);
        border: 1px solid rgba(244,237,225,0.2);
        padding: 18px 20px;
        margin-bottom: 14px;
        position: relative;
    }
    .job-title {
        font-size: 16px;
        font-weight: 600;
        color: #F4EDE1;
        margin-bottom: 3px;
    }
    .job-meta {
        font-size: 13px;
        color: rgba(244,237,225,0.6);
        margin-bottom: 10px;
    }
    .job-meta .spec-inline {
        font-family: 'Space Mono', monospace;
        font-size: 12px;
    }
    .tag {
        display: inline-block;
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.5px;
        padding: 2px 8px;
        margin-right: 5px;
        border: 1px solid rgba(244,237,225,0.3);
        color: rgba(244,237,225,0.7);
    }
    .tag-accent {
        border-color: #D98953;
        color: #D98953;
    }
    .tag-flag {
        border-style: dashed;
        border-color: rgba(244,237,225,0.4);
    }
    .card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-left {
        flex: 1;
    }
    .gauge-wrap {
        text-align: center;
        width: 90px;
    }
    .gauge-score {
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        color: #F4EDE1;
        margin-top: -6px;
    }
</style>
""", unsafe_allow_html=True)


def is_genuinely_unrestricted(location):
    if not location:
        return False
    location_lower = location.lower()
    if location_lower == "remote":
        return True
    if "africa friendly" in location_lower:
        return True
    if "worldwide" in location_lower:
        return True
    if "anywhere" in location_lower:
        return True
    if "global" in location_lower:
        return True
    return False


def has_visa_warning(description):
    if not description:
        return False
    description_lower = description.lower()
    warning_phrases = [
        "visa sponsorship", "sponsor visa", "no sponsorship",
        "authorized to work in", "work authorization",
        "must be based in", "must reside in",
        "on-site", "in-office", "hybrid",
    ]
    return any(phrase in description_lower for phrase in warning_phrases)


def load_jobs():
    with get_session() as session:
        jobs = session.query(JobDB).filter(
            JobDB.is_active == True
        ).order_by(JobDB.ranking_score.desc()).all()

        job_list = []
        for job in jobs:
            raw = session.query(RawJobDB).filter(
                RawJobDB.job_hash == job.job_hash
            ).first()
            description = raw.description if raw else ""

            job_list.append({
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
                "description": description,
            })

        return pd.DataFrame(job_list)


def gauge_svg(score):
    radius = 50
    arc_length = math.pi * radius
    filled = arc_length * (score / 100)
    return f"""
    <svg viewBox="0 0 120 68" width="90" height="52">
        <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none"
              stroke="rgba(244,237,225,0.18)" stroke-width="7" stroke-linecap="round"/>
        <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none"
              stroke="#D98953" stroke-width="7" stroke-linecap="round"
              stroke-dasharray="{filled:.1f} {arc_length:.1f}"/>
    </svg>
    """


df = load_jobs()
df["unrestricted"] = df["location"].apply(is_genuinely_unrestricted)
df["has_warning"] = df["description"].apply(has_visa_warning)

now_str = datetime.now().strftime("%H:%M")

st.markdown(
    f'<div class="title-block">'
    f'<div class="title-block-main">JOB INTELLIGENCE SCAN LOG</div>'
    f'<div class="title-block-sub">SOURCES {len(df["company"].unique())} &nbsp;·&nbsp; '
    f'SIGNALS {len(df)} &nbsp;·&nbsp; LAST SYNC {now_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# sidebar filters
st.sidebar.header("Filters")

role_filter = st.sidebar.selectbox(
    "Role Type",
    ["all", "data engineering", "product management"]
)

score_filter = st.sidebar.slider(
    "Minimum Score",
    min_value=0,
    max_value=100,
    value=45,
)

experience_filter = st.sidebar.multiselect(
    "Experience Level",
    options=["intern", "junior", "mid", "senior", "manager"],
    default=["junior", "mid"],
)

beginner_only = st.sidebar.checkbox("Beginner friendly only")
unrestricted_only = st.sidebar.checkbox(
    "Genuinely unrestricted only",
    help="only show jobs with no country restriction - accessible from anywhere including Lagos"
)

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

if unrestricted_only:
    filtered = filtered[filtered["unrestricted"] == True]

readouts = [
    ("Total", len(df)),
    ("Matched", len(filtered)),
    ("Strong (60+)", len(df[df["score"] >= 60])),
    ("Entry-level", len(df[df["beginner_friendly"] == True])),
    ("Unrestricted", len(df[df["unrestricted"] == True])),
]

cells_html = "".join(
    f'<div class="readout-cell"><div class="readout-label">{label}</div>'
    f'<div class="readout-value">{value}</div></div>'
    for label, value in readouts
)
st.markdown(f'<div class="readout-strip">{cells_html}</div>', unsafe_allow_html=True)

st.write("")

for _, job in filtered.iterrows():
    tags_html = f'<span class="tag">{(job["experience"] or "N/A").upper()}</span>'
    if job["unrestricted"]:
        tags_html += '<span class="tag tag-accent">UNRESTRICTED</span>'
    if job["beginner_friendly"]:
        tags_html += '<span class="tag">ENTRY-LEVEL</span>'
    if job["has_warning"]:
        tags_html += '<span class="tag tag-flag">FLAG: VERIFY</span>'

    salary_line = ""
    if job["salary_min"] and job["salary_max"]:
        salary_line = (
            f'<div class="job-meta">'
            f'<span class="spec-inline">${job["salary_min"]:,.0f} - ${job["salary_max"]:,.0f}</span></div>'
        )

    gauge = gauge_svg(job["score"])

    card_html = (
        '<div class="job-card"><div class="card-row"><div class="card-left">'
        f'<div class="job-title">{job["title"]}</div>'
        f'<div class="job-meta">{job["company"]} &nbsp;·&nbsp; {job["location"]} &nbsp;·&nbsp; '
        f'<span class="spec-inline">{job["source"]}</span></div>'
        f'<div>{tags_html}</div>'
        f'{salary_line}'
        '</div>'
        f'<div class="gauge-wrap">{gauge}<div class="gauge-score">{int(job["score"])}/100</div></div>'
        '</div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
    st.link_button("Apply Now", job["url"])
    st.write("")