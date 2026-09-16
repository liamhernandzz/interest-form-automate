"""
emailer.py

Takes a routing decision from salesforce_report_parser.py (sport(s) + ticket_type,
or multi-sport) and sends the matching static template email to the
recipient. Templates are static text, no personalization placeholders.

Supports --dry-run (default) and --send (real sending via Gmail SMTP).
"""

import os
import argparse
import textwrap
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

SPORT_TO_PREFIX = {
    "Football": "football",
    "Volleyball": "vball",
    "mensBasketball": "mbasket",
    "Softball": "softball",
    "womensBasketball": "wbasket",
    "Baseball": "baseball",
}

TICKET_TYPE_TO_SUFFIX = {
    "SingleGameTickets": "single",
    "SeasonTickets": "season",
    "GroupTickets": "group",
}

TICKET_TYPE_DISPLAY = {
    "SingleGameTickets": "Single Game Tickets",
    "SeasonTickets": "Season Tickets",
    "GroupTickets": "Group Tickets",
}

TEMPLATES_DIR = "templates"


def resolve_template_filename(sports: list[str], ticket_type: str) -> str:
    """Map sport(s) + ticket_type to the matching template filename."""
    if len(sports) > 1:
        return f"{TEMPLATES_DIR}/multi_sport.txt"

    sport_prefix = SPORT_TO_PREFIX.get(sports[0])
    ticket_suffix = TICKET_TYPE_TO_SUFFIX.get(ticket_type)

    if sport_prefix is None or ticket_suffix is None:
        raise ValueError(
            f"No template mapping for sport={sports[0]!r}, "
            f"ticket_type={ticket_type!r}"
        )

    return f"{TEMPLATES_DIR}/{sport_prefix}_{ticket_suffix}.txt"


def load_template(filename: str) -> str:
    """Read the raw template file content (static text, no placeholders)."""
    with open(filename, encoding="utf-8") as f:
        return f.read()


def build_subject(sports: list[str], ticket_type: str) -> str:
    """Generate a subject line based on sport(s) and ticket type."""
    sport_display = " and ".join(sports) if len(sports) == 1 else "Multi-Sport"
    ticket_display = TICKET_TYPE_DISPLAY.get(ticket_type, "Ticket")
    return f"Your {sport_display} {ticket_display} Interest"


def send_email(to_address: str, subject: str, body: str, dry_run: bool = True):
    """Send the email via Gmail SMTP, or print it if dry_run is True."""
    wrapped_body = textwrap.fill(body, width=70)

    if dry_run:
        print(f"--- DRY RUN: would send to {to_address} ---")
        print(f"Subject: {subject}")
        print(wrapped_body)
        print("--- END ---\n")
        return

    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise RuntimeError("Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env")

    msg = MIMEText(wrapped_body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [to_address], msg.as_string())

    print(f"Sent to {to_address}")


def process_submission(fields: dict, decision: dict, dry_run: bool = True):
    """Resolve the right template and send (or dry-run print) it."""
    if decision["action"] != "send_template":
        print(f"Skipping {fields.get('emailAddress')}: {decision.get('reason')}")
        return

    sports = decision["sports"]
    ticket_type = decision["ticket_type"]

    filename = resolve_template_filename(sports, ticket_type)
    body = load_template(filename)
    subject = build_subject(sports, ticket_type)

    send_email(
        to_address=fields.get("emailAddress"),
        subject=subject,
        body=body,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Actually send emails instead of dry-run")
    args = parser.parse_args()

    from run_sf_parser import load_and_parse

    filepath = "data/csv_scrubbed.csv"  # update to your actual filename
    parsed_rows = load_and_parse(filepath)

    for fields, decision in parsed_rows:
        process_submission(fields, decision, dry_run=not args.send)