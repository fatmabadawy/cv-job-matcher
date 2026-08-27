import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import models
from config import SMTP_HOST, SMTP_USER, SMTP_PASSWORD, MATCH_ALERT_THRESHOLD

logger = logging.getLogger(__name__)

scheduler = None


def send_weekly_digest():
    """Send job alert emails or log if SMTP not configured."""
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        for u in users:
            matches = (
                db.query(models.Match)
                .filter_by(user_id=u.id, alerted=False)
                .filter(models.Match.score >= MATCH_ALERT_THRESHOLD)
                .order_by(models.Match.score.desc())
                .limit(5)
                .all()
            )
            if not matches:
                continue

            # Get job details
            job_ids = [m.job_id for m in matches]
            jobs = db.query(models.Job).filter(models.Job.id.in_(job_ids)).all()
            job_map = {j.id: j for j in jobs}

            subject = "Your Weekly Job Matches"
            body_lines = [f"Hi {u.email},\n\nHere are your top job matches this week:\n"]
            for m in matches:
                job = job_map.get(m.job_id)
                if job:
                    body_lines.append(
                        f"• {job.title} at {job.company} — Match: {m.score:.0f}%\n"
                        f"  Reason: {m.reason}\n"
                        f"  Link: {job.link}\n"
                    )
            body_lines.append("\nGood luck!\nCV Job Matcher")
            body = "\n".join(body_lines)

            if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
                _send_email(u.email, subject, body)
            else:
                logger.info(f"[alerts] SMTP not configured — logging digest for {u.email}:\n{body}")

            # Mark as alerted
            for m in matches:
                m.alerted = True
        db.commit()
    except Exception as e:
        logger.error(f"[alerts] Error in weekly digest: {e}")
    finally:
        db.close()


def _send_email(to: str, subject: str, body: str):
    """Send an email via SMTP."""
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(SMTP_HOST, 587) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"[alerts] Email sent to {to}")
    except Exception as e:
        logger.error(f"[alerts] Failed to send email to {to}: {e}")


def scrape_and_index():
    """Periodic scrape + FAISS index update (no LLM calls)."""
    from services.scraper import run_all_scrapers
    from services.embeddings import build_index

    db = SessionLocal()
    try:
        counts = run_all_scrapers(db)
        indexed = build_index(db)
        logger.info("[scheduler] scrape=%s indexed=%s", counts, indexed)
    except Exception as e:
        logger.error("[scheduler] scrape/index failed: %s", e)
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler background scheduler."""
    global scheduler
    if scheduler is None or not scheduler.running:
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_weekly_digest, "cron", day_of_week="sun", hour=9, id="weekly_digest")
        scheduler.add_job(scrape_and_index, "interval", hours=6, id="periodic_scrape")
        scheduler.start()
        logger.info("[scheduler] Started. Digest Sunday 9am; scrape every 6 hours.")
    return scheduler
