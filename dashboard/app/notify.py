"""SME email notifications.

When a question is escalated, the assigned SME group is emailed. Transport:
  - SMTP   if config.SMTP_HOST is set (real send)
  - outbox otherwise: the email is written to data/outbox/<id>.eml (offline mode)
A copy is always saved to the outbox for audit + the UI 'Notifications' view.
"""
from __future__ import annotations

import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from . import config


def build_message(esc: dict) -> tuple[EmailMessage, str]:
    to = config.sme_email_for(esc["assigned_sme_group"])
    product = esc.get("product") or "General"
    q = esc.get("question", "")
    msg = EmailMessage()
    msg["From"] = config.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = f"[Knowledge Agent] SME help needed — {product}: {q[:64]}"
    msg.set_content(
        "A Technical Sales question could not be answered from approved sources and "
        "has been routed to your SME group.\n\n"
        f"SME group:   {esc['assigned_sme_group']}\n"
        f"Product:     {esc.get('product') or '—'}\n"
        f"Feature:     {esc.get('feature') or '—'}\n"
        f"Reason:      {esc.get('failed_reason')}\n"
        f"Confidence:  {esc.get('confidence_score', 0)}/100\n"
        f"SLA:         {esc.get('requested_sla', '—')}\n"
        f"Escalation:  {esc['escalation_id']}\n\n"
        f"Question:\n  {q}\n\n"
        f"Sources considered: {', '.join(esc.get('retrieved_sources', [])) or 'none'}\n\n"
        f"Respond in the SME Queue:\n  {config.APP_BASE_URL}/#sme\n\n"
        "Approving your answer publishes it back into the knowledge base, so the agent "
        "can answer this for everyone next time.\n"
    )
    return msg, to


def send_escalation_email(esc: dict) -> dict:
    """Send (or stage) the notification. Returns a notification record."""
    msg, to = build_message(esc)
    transport, error = "outbox", None

    if config.SMTP_HOST:
        try:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as s:
                if config.SMTP_USER:
                    s.starttls()
                    s.login(config.SMTP_USER, config.SMTP_PASS)
                s.send_message(msg)
            transport = "smtp"
        except Exception as e:  # fall back to outbox so nothing is lost
            transport, error = "outbox (smtp failed)", str(e)

    # Always keep an audit copy in the outbox.
    (config.OUTBOX_DIR / f"{esc['escalation_id']}.eml").write_text(str(msg), encoding="utf-8")

    return {
        "to": to,
        "subject": msg["Subject"],
        "transport": transport,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "escalation_id": esc["escalation_id"],
        "error": error,
    }


def list_outbox() -> list[dict]:
    """Sent notifications, newest first (parsed from the .eml audit copies)."""
    import email
    from email import policy

    out = []
    for p in sorted(config.OUTBOX_DIR.glob("*.eml"),
                    key=lambda x: x.stat().st_mtime, reverse=True):
        m = email.message_from_string(p.read_text(encoding="utf-8"), policy=policy.default)
        out.append({
            "escalation_id": p.stem,
            "to": m["To"], "from": m["From"], "subject": str(m["Subject"]),
            "body": m.get_content(),
            "sent_at": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
        })
    return out
