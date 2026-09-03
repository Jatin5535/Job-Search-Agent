from __future__ import annotations
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .config import min_score
from .db import shortlist


def render_text(rows):
    if not rows:
        return "No jobs crossed the configured score threshold today."
    lines = [f"Top job matches (score >= {min_score()})", ""]
    for r in rows:
        lines += [
            f"{r['score']}/100 — {r['title']} — {r['company']}",
            f"Location: {r['location']} | Work mode: {r['workplace_type']}",
            f"Apply: {r['apply_url'] or r['url']}",
            f"Why: {r['reasons']}",
            "",
        ]
    return "\n".join(lines)


def send_digest():
    rows = shortlist(min_score(), 20)
    body = render_text(rows)
    host = os.getenv("SMTP_HOST")
    to = os.getenv("DIGEST_TO")
    if not host or not to:
        return {"sent": False, "reason": "SMTP_HOST or DIGEST_TO not configured", "body": body}
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", user)
    msg = MIMEMultipart()
    msg["Subject"] = "Job Search Agent — Daily Shortlist"
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP(host, port, timeout=30) as server:
        if os.getenv("SMTP_STARTTLS", "true").lower() == "true":
            server.starttls()
        if user:
            server.login(user, password)
        server.sendmail(sender, [to], msg.as_string())
    return {"sent": True, "count": len(rows)}
