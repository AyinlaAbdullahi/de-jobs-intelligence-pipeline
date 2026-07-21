import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from datetime import datetime
from db.connection import get_session
from db.models import Job as JobDB, RawJob as RawJobDB
from app_config.role_skills import role_skills, get_role_type

st.set_page_config(page_title="Job Dossier", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.toggle("Dark mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

if dark_mode:
    bg = "#1C1814"
    sidebar_bg = "#151210"
    card_bg = "#241F19"
    text_primary = "#EDE6D6"
    text_secondary = "#A89A87"
    border = "#3A322A"
    accent = "#C4453F"
    accent_bg = "#3A211E"
else:
    bg = "#F2ECDD"
    sidebar_bg = "#EAE1CB"
    card_bg = "#F8F3E7"
    text_primary = "#1F1B16"
    text_secondary = "#6B5D4F"
    border = "#C9BFA8"
    accent = "#9A2B2B"
    accent_bg = "#F5E4E1"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    .stApp {{
        background-color: {bg};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border};
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="select"] span {{
        color: {text_primary} !important;
    }}
    ul[data-baseweb="menu"] {{
        background-color: {card_bg} !important;
    }}
    ul[data-baseweb="menu"] li {{
        color: {text_primary} !important;
    }}
    ul[data-baseweb="menu"] li:hover {{
        background-color: {bg} !important;
    }}
    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', sans-serif;
        color: {text_primary};
    }}
    .file-header {{
        border: 1px solid {border};
        border-bottom: 3px double {accent};
        padding: 22px 26px;
        margin-bottom: 22px;
        background-color: {card_bg};
    }}
    .file-title {{
        font-family: 'Source Serif 4', serif;
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.2px;
        color: {text_primary};
        margin-bottom: 6px;
    }}
    .file-sub {{
        font-size: 12px;
        color: {text_secondary};
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}
    .readout-strip {{
        display: flex;
        border-top: 1px solid {border};
        border-bottom: 1px solid {border};
        margin-bottom: 22px;
    }}
    .readout-cell {{
        flex: 1;
        padding: 14px 18px;
        border-right: 1px solid {border};
    }}
    .readout-cell:last-child {{ border-right: none; }}
    .readout-label {{
        font-size: 10px;
        color: {text_secondary};
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .readout-value {{
        font-family: 'Source Serif 4', serif;
        font-size: 26px;
        font-weight: 700;
        color: {text_primary};
    }}
    .signals-panel {{
        border: 1px solid {border};
        background-color: {card_bg};
        padding: 16px 20px;
        height: 100%;
    }}
    .signals-title {{
        font-family: 'Source Serif 4', serif;
        font-size: 14px;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .signal-row {{
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
    }}
    .signal-name {{
        width: 110px;
        flex-shrink: 0;
        color: {text_primary};
    }}
    .signal-bar-bg {{
        flex: 1;
        background-color: {bg};
        border: 1px solid {border};
        height: 10px;
        margin: 0 8px;
    }}
    .signal-bar-fill {{
        background-color: {accent};
        height: 100%;
    }}
    .signal-count {{
        width: 34px;
        text-align: right;
        color: {text_secondary};
        font-family: 'Source Serif 4', serif;
        font-weight: 600;
    }}
    .signals-empty {{
        color: {text_secondary};
        font-size: 12px;
        font-style: italic;
    }}
    .job-card {{
        background-color: {card_bg};
        border: 1px solid {border};
        padding: 18px 20px;
        margin-bottom: 14px;
        position: relative;
        transition: border-color 180ms ease, box-shadow 180ms ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.12);
    }}
    .job-card:hover {{
        border-color: {accent};
        box-shadow: 0 4px 16px rgba(154,43,43,0.14);
    }}
    .job-card.featured {{
        border-left: 4px solid {accent};
    }}
    .job-title {{
        font-family: 'Source Serif 4', serif;
        font-size: 17px;
        font-weight: 600;
        color: {text_primary};
        margin-bottom: 3px;
        padding-right: 78px;
    }}
    .job-meta {{
        font-size: 12px;
        color: {text_secondary};
        margin-bottom: 9px;
    }}
    .tag {{
        display: inline-block;
        font-size: 10px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        padding: 2px 8px;
        margin-right: 5px;
        margin-bottom: 5px;
        border: 1px solid {border};
        color: {text_secondary};
        background-color: {bg};
    }}
    .tag-accent {{
        border-color: {accent};
        color: {accent};
        background-color: {accent_bg};
    }}
    .tag-flag {{
        border-style: dashed;
    }}
    .stamp {{
        position: absolute;
        top: 16px;
        right: 18px;
        width: 62px;
        height: 62px;
        border: 2px solid {accent};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transform: rotate(-8deg);
        color: {accent};
    }}
    .stamp::before {{
        content: "";
        position: absolute;
        inset: 4px;
        border: 1px solid {accent};
        border-radius: 50%;
    }}
    .stamp-score {{
        font-family: 'Source Serif 4', serif;
        font-size: 15px;
        font-weight: 700;
    }}
    .empty-state {{
        border: 1px dashed {border};
        padding: 40px 24px;
        text-align: center;
        color: {text_secondary};
    }}
    .empty-state-title {{
        font-family: 'Source Serif 4', serif;
        font-size: 16px;
        color: {text_primary};
        margin-bottom: 6px;
    }}
    div[data-testid="stLinkButton"] a {{
        background-color: {text_primary} !important;
        color: {bg} !important;
        transition: transform 150ms ease, opacity 150ms ease;
    }}
    div[data-testid="stLinkButton"] a:hover {{
        transform: translateY(-1px);
        opacity: 0.85;
    }}
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


def load_skills_demand(role_type_filter):
    with get_session() as session:
        jobs = session.query(JobDB).filter(JobDB.is_active == True).all()

        skill_counts = {}
        for job in jobs:
            job_role = get_role_type(job.title or "")

            if role_type_filter == "data engineering" and job_role != "data engineering":
                continue
            if role_type_filter == "product management" and job_role != "product management":
                continue

            raw = session.query(RawJobDB).filter(RawJobDB.job_hash == job.job_hash).first()
            description = (raw.description if raw else "") or ""
            text = f"{job.title or ''} {description}".lower()

            skills = role_skills[job_role]["skills"]
            for skill in skills:
                if skill in text:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        return [{"skill": s, "job_count": c} for s, c in sorted_skills]


def load_top_companies(filtered_df):
    if filtered_df.empty:
        return []

    company_counts = (
        filtered_df[filtered_df["company"] != "unknown"]
        .groupby("company")
        .agg(job_count=("company", "count"), avg_score=("score", "mean"))
        .sort_values("job_count", ascending=False)
        .head(8)
        .reset_index()
    )
    return [
        {"company_name": row["company"], "job_count": row["job_count"], "avg_score": row["avg_score"]}
        for _, row in company_counts.iterrows()
    ]


df = load_jobs()
df["unrestricted"] = df["location"].apply(is_genuinely_unrestricted)
df["has_warning"] = df["description"].apply(has_visa_warning)

now_str = datetime.now().strftime("%H:%M")

st.markdown(
    f'<div class="file-header">'
    f'<div class="file-title">Job Intelligence Dossier</div>'
    f'<div class="file-sub">Sources {len(df["company"].unique())} &nbsp;·&nbsp; '
    f'Entries {len(df)} &nbsp;·&nbsp; Filed {now_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

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

skills = load_skills_demand(role_filter)
companies = load_top_companies(filtered)

max_skill_count = max([s["job_count"] for s in skills], default=1)
max_company_count = max([c["job_count"] for c in companies], default=1)

if skills:
    skills_rows = "".join(
        f'<div class="signal-row">'
        f'<div class="signal-name">{s["skill"]}</div>'
        f'<div class="signal-bar-bg"><div class="signal-bar-fill" '
        f'style="width:{(s["job_count"] / max_skill_count) * 100:.0f}%;"></div></div>'
        f'<div class="signal-count">{s["job_count"]}</div>'
        f'</div>'
        for s in skills
    )
else:
    skills_rows = '<div class="signals-empty">no data for this filter</div>'

if companies:
    companies_rows = "".join(
        f'<div class="signal-row">'
        f'<div class="signal-name">{c["company_name"]}</div>'
        f'<div class="signal-bar-bg"><div class="signal-bar-fill" '
        f'style="width:{(c["job_count"] / max_company_count) * 100:.0f}%;"></div></div>'
        f'<div class="signal-count">{c["job_count"]}</div>'
        f'</div>'
        for c in companies
    )
else:
    companies_rows = '<div class="signals-empty">no data for this filter</div>'

sig_col1, sig_col2 = st.columns(2)
with sig_col1:
    st.markdown(
        f'<div class="signals-panel">'
        f'<div class="signals-title">Skills in Demand</div>'
        f'{skills_rows}'
        f'</div>',
        unsafe_allow_html=True
    )
with sig_col2:
    st.markdown(
        f'<div class="signals-panel">'
        f'<div class="signals-title">Top Hiring Companies</div>'
        f'{companies_rows}'
        f'</div>',
        unsafe_allow_html=True
    )

st.write("")

if filtered.empty:
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-state-title">No entries match this filter</div>'
        '<div>try lowering the minimum score or widening experience level</div>'
        '</div>',
        unsafe_allow_html=True
    )
else:
    rows = [filtered.iloc[i:i + 2] for i in range(0, len(filtered), 2)]
    for row in rows:
        cols = st.columns(2)
        for col, (_, job) in zip(cols, row.iterrows()):
            with col:
                tags_html = f'<span class="tag">{(job["experience"] or "N/A")}</span>'
                if job["unrestricted"]:
                    tags_html += '<span class="tag tag-accent">Unrestricted</span>'
                if job["beginner_friendly"]:
                    tags_html += '<span class="tag">Entry-level</span>'
                if job["has_warning"]:
                    tags_html += '<span class="tag tag-flag">Verify</span>'

                salary_line = ""
                if job["salary_min"] and job["salary_max"]:
                    salary_line = (
                        f'<div class="job-meta">${job["salary_min"]:,.0f} - ${job["salary_max"]:,.0f}</div>'
                    )

                featured_class = " featured" if job["score"] >= 80 else ""

                card_html = (
                    f'<div class="job-card{featured_class}">'
                    f'<div class="stamp"><span class="stamp-score">{int(job["score"])}</span></div>'
                    f'<div class="job-title">{job["title"]}</div>'
                    f'<div class="job-meta">{job["company"]} &nbsp;·&nbsp; {job["location"]} &nbsp;·&nbsp; {job["source"]}</div>'
                    f'<div>{tags_html}</div>'
                    f'{salary_line}'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                st.link_button("Apply Now", job["url"], use_container_width=True)
                st.write("")