import smtplib
import logging
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.connection import get_session
from db.models import Job as JobDB
from app_config.settings import settings

logger = logging.getLogger(__name__)

min_score = 45


def get_new_jobs():
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    with get_session() as session:
        jobs = session.query(JobDB).filter(
            JobDB.created_at >= since,
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
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "url": job.url,
                "source": job.source,
                "beginner_friendly": job.beginner_friendly,
            }
            for job in jobs
        ]


def build_email(jobs: list, recipient_name: str, role_type: str) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")

    rows_html = ""
    for job in jobs:
        salary_line = ""
        if job.get("salary_min") and job.get("salary_max"):
            salary_line = (
                f'<div style="font-family:\'Courier New\',monospace;font-size:12px;'
                f'color:#8a9bb0;margin-top:4px;">'
                f'${job["salary_min"]:,.0f} - ${job["salary_max"]:,.0f}</div>'
            )

        rows_html += f"""
        <tr>
          <td style="padding:0 0 14px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                   style="background-color:#16324d;border:1px solid #2a4058;border-left:3px solid #d98953;border-radius:4px;">
              <tr>
                <td style="padding:16px 20px;">
                  <div style="font-family:Arial,sans-serif;font-size:15px;font-weight:bold;color:#f4ede1;">
                    {job['title']}
                  </div>
                  <div style="font-family:Arial,sans-serif;font-size:13px;color:#9fb0c3;margin-top:3px;">
                    {job['company']} &middot; {job['location']} &middot;
                    <span style="font-family:'Courier New',monospace;">{job['source']}</span>
                  </div>
                  {salary_line}
                  <table role="presentation" cellpadding="0" cellspacing="0" style="margin-top:10px;">
                    <tr>
                      <td style="font-family:'Courier New',monospace;font-size:11px;color:#d98953;
                                 border:1px solid #4a3520;border-radius:3px;padding:2px 8px;">
                        {int(job['score'])}/100
                      </td>
                      <td style="width:8px;"></td>
                      <td style="font-family:'Courier New',monospace;font-size:11px;color:#9fb0c3;
                                 border:1px solid #2a4058;border-radius:3px;padding:2px 8px;">
                        {(job['experience'] or 'N/A').upper()}
                      </td>
                    </tr>
                  </table>
                  <div style="margin-top:12px;">
                    <a href="{job['url']}"
                       style="display:inline-block;background-color:#d98953;color:#12283f;
                              font-family:Arial,sans-serif;font-size:13px;font-weight:bold;
                              text-decoration:none;padding:8px 18px;border-radius:3px;">
                      Apply Now
                    </a>
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    html = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#0e1e30;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#0e1e30;">
      <tr>
        <td align="center" style="padding:24px 16px;">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0">
            <tr>
              <td style="border:1px solid #2a4058;border-left:3px solid #d98953;
                         background-color:#12283f;padding:20px 24px;border-radius:4px;">
                <div style="font-family:Arial,sans-serif;font-size:22px;font-weight:bold;color:#f4ede1;">
                  Job Digest &middot; {date_str}
                </div>
                <div style="font-family:'Courier New',monospace;font-size:12px;color:#8a9bb0;margin-top:6px;">
                  {len(jobs)} {role_type} matches &middot; scoring above {min_score}/100
                </div>
              </td>
            </tr>
            <tr><td style="height:20px;"></td></tr>
            {rows_html}
            <tr>
              <td style="padding-top:10px;">
                <div style="font-family:'Courier New',monospace;font-size:11px;color:#5a6a7e;">
                  DE Jobs Intelligence Pipeline
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    """
    return html


def send_email(recipient_email: str, recipient_name: str, jobs: list, role_type: str, subject: str):
    if not jobs:
        logger.info(f"no new {role_type} jobs for {recipient_email}, skipping")
        return

    jobs = jobs[:20]

    msg = MIMEMultipart("alternative")
    msg["subject"] = subject
    msg["from"] = settings.gmail_user
    msg["to"] = recipient_email
    msg["Reply-To"] = settings.gmail_user

    plain = f"job digest - {datetime.now().strftime('%B %d, %Y')}\n\n"
    plain += f"hi {recipient_name}, here are today's top {role_type} matches.\n\n"
    for job in jobs:
        plain += f"{job['title']} - {job['company']}\n"
        plain += f"location: {job['location']}\n"
        plain += f"score: {int(job['score'])}/100\n"
        plain += f"apply: {job['url']}\n\n"

    html = build_email(jobs, recipient_name, role_type)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.gmail_user, settings.gmail_app_pass)
        server.sendmail(settings.gmail_user, recipient_email, msg.as_string())

    logger.info(f"email sent to {recipient_email} with {len(jobs)} {role_type} jobs")


def send_daily_alerts():
    jobs = get_new_jobs()
    logger.info(f"found {len(jobs)} new jobs above score {min_score}")

    de_jobs = [j for j in jobs if any(
        role in j["title"].lower() for role in [
            "data engineer", "analytics engineer", "etl", "data platform"
        ]
    )]

    pm_jobs = [j for j in jobs if "product manager" in j["title"].lower()]

    send_email(
        recipient_email=settings.alert_email,
        recipient_name="Abdullahi",
        jobs=de_jobs,
        role_type="data engineering",
        subject=f"{len(de_jobs)} data engineering jobs found today ({datetime.now().strftime('%b %d')})",
    )

    if settings.alert_email_2:
        send_email(
            recipient_email=settings.alert_email_2,
            recipient_name="Azeez",
            jobs=pm_jobs,
            role_type="product management",
            subject=f"{len(pm_jobs)} product management jobs found today ({datetime.now().strftime('%b %d')})",
        )