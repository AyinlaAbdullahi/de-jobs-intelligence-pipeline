import smtplib
import logging
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.connection import get_session
from db.models import Job as JobDB
from config.settings import settings

logger = logging.getLogger(__name__)

min_score = 45


def get_new_jobs():
    with get_session() as session:
        jobs = session.query(JobDB).filter(
            JobDB.ranking_score >= min_score,
            JobDB.is_active == True,
        ).order_by(JobDB.ranking_score.desc()).all()

        return [
            {
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "score": job.ranking_score,
                "experience": job.experience_level,
                "salary": f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}" if job.salary_min and job.salary_max else "not listed",
                "url": job.url,
                "source": job.source,
                "beginner_friendly": job.beginner_friendly,
            }
            for job in jobs
        ]


def build_email(jobs: list, recipient_name: str) -> str:
    de_jobs = [j for j in jobs if any(
        role in j["title"].lower() for role in [
            "data engineer", "analytics engineer", "etl", "data platform"
        ]
    )]
    pm_jobs = [j for j in jobs if "product manager" in j["title"].lower()]
    other_jobs = [j for j in jobs if j not in de_jobs and j not in pm_jobs]

    date_str = datetime.now().strftime("%B %d, %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #333;">

    <h2 style="color: #2c3e50;">daily job digest - {date_str}</h2>
    <p>hi {recipient_name}, here are today's top job matches.</p>
    <p><strong>{len(jobs)} new jobs</strong> scored above {min_score}/100 in the last 24 hours.</p>

    <hr>
    """

    def render_section(title, jobs_list):
        if not jobs_list:
            return ""
        section = f"<h3 style='color: #2980b9;'>{title} ({len(jobs_list)} jobs)</h3>"
        for job in jobs_list:
            score_color = "#27ae60" if job["score"] >= 60 else "#f39c12"
            beginner_tag = " <span style='background:#27ae60;color:white;padding:2px 6px;border-radius:4px;font-size:11px;'>beginner friendly</span>" if job["beginner_friendly"] else ""
            section += f"""
            <div style="border:1px solid #ddd;border-radius:6px;padding:14px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <strong style="font-size:15px;">{job["title"]}</strong>
                    <span style="background:{score_color};color:white;padding:3px 8px;border-radius:12px;font-size:13px;">{int(job["score"])}/100</span>
                </div>
                <div style="color:#555;margin-top:4px;">{job["company"]} &nbsp;|&nbsp; {job["location"]} &nbsp;|&nbsp; {job["experience"]}{beginner_tag}</div>
                <div style="color:#888;font-size:13px;margin-top:4px;">salary: {job["salary"]} &nbsp;|&nbsp; source: {job["source"]}</div>
                <div style="margin-top:8px;">
                    <a href="{job["url"]}" style="background:#2980b9;color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-size:13px;">apply now</a>
                </div>
            </div>
            """
        return section

    html += render_section("data engineering roles", de_jobs)
    html += render_section("product management roles", pm_jobs)
    html += render_section("other roles", other_jobs)

    html += """
    <hr>
    <p style="color:#aaa;font-size:12px;">powered by de jobs intelligence pipeline</p>
    </body>
    </html>
    """
    return html


def send_email(recipient_email: str, recipient_name: str, jobs: list):
    if not jobs:
        logger.info(f"no new jobs for {recipient_email}, skipping email")
        return

    # limit to top 20 to avoid spam filters
    jobs = jobs[:20]

    msg = MIMEMultipart("alternative")
    msg["subject"] = f"daily job digest - {len(jobs)} new matches ({datetime.now().strftime('%b %d')})"
    msg["from"] = settings.gmail_user
    msg["to"] = recipient_email
    msg["Reply-To"] = settings.gmail_user

    # plain text version
    plain = f"daily job digest - {datetime.now().strftime('%B %d, %Y')}\n\n"
    plain += f"hi {recipient_name}, here are today's top {len(jobs)} job matches.\n\n"
    for job in jobs:
        plain += f"{job['title']} - {job['company']}\n"
        plain += f"location: {job['location']}\n"
        plain += f"score: {int(job['score'])}/100\n"
        plain += f"apply: {job['url']}\n\n"

    html = build_email(jobs, recipient_name)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.gmail_user, settings.gmail_app_pass)
        server.sendmail(settings.gmail_user, recipient_email, msg.as_string())

    logger.info(f"email sent to {recipient_email} with {len(jobs)} jobs")


def send_daily_alerts():
    jobs = get_new_jobs()
    logger.info(f"found {len(jobs)} new jobs above score {min_score}")

    send_email(
        recipient_email=settings.alert_email,
        recipient_name="Abdullahi",
        jobs=[j for j in jobs if any(
            role in j["title"].lower() for role in [
                "data engineer", "analytics engineer", "etl", "data platform"
            ]
        )],
    )

    if settings.alert_email_2:
        send_email(
            recipient_email=settings.alert_email_2,
            recipient_name="Azeez",
            jobs=[j for j in jobs if "product manager" in j["title"].lower()],
        )