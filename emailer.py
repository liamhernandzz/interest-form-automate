import argparse
import textwrap

# Maps the sport field name (from Salesforce) to the filename prefix
# used in templates/
SPORT_TO_PREFIX = {
    "Football": "football",
    "Volleyball": "vball",
    "mensBasketball": "mbasket",
    "Softball": "softball",
    "womensBasketball": "wbasket",
    "Baseball": "baseball",
}

# Maps the ticket_type field name to the filename suffix
TICKET_TYPE_TO_SUFFIX = {
    "SingleGameTickets": "single",
    "SeasonTickets": "season",
    "GroupTickets": "group",
}

TEMPLATES_DIR = "templates"

def build_subject(sports: list[str], ticket_type: str) -> str:
    """Generate a subject line based on sport(s) and ticket type."""
    sport_display = " and ".join(sports) if len(sports) == 1 else "Multi-Sport"
    ticket_display = {
        "SingleGameTickets": "Single Game Tickets",
        "SeasonTickets": "Season Tickets",
        "GroupTickets": "Group Tickets",
    }.get(ticket_type, "Ticket")

    return f"Your {sport_display} {ticket_display} Interest"

def resolve_template_filename(sports: list[str], ticket_type: str) -> str:
    """
    Given the list of interested sports and the ticket type, return the
    matching template filename.

    Multi-sport submissions always use the single generic multi_sport.txt,
    regardless of ticket type.
    """
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
    """Read the raw template file content."""
    with open(filename, encoding="utf-8") as f:
        return f.read()


def fill_template(template_text: str, fields: dict, sports: list[str]) -> str:
    """
    Fill in placeholders like {first_name}, {sport} using the parsed
    fields dict. Sport is joined into a readable string if there are
    multiple (only relevant for the multi_sport template).
    """
    sport_display = " and ".join(sports)

    return template_text.format(
        first_name=fields.get("firstName", ""),
        last_name=fields.get("lastName", ""),
        sport=sport_display,
    )


def send_email(to_address: str, subject: str, body: str, dry_run: bool = True):
    wrapped_body = textwrap.fill(body, width=70)

    if dry_run:
        print(f"--- DRY RUN: would send to {to_address} ---")
        print(f"Subject: {subject}")
        print(wrapped_body)
        print("--- END ---\n")
    else:
        raise NotImplementedError("Real sending not wired up yet")

def process_submission(fields: dict, decision: dict, dry_run: bool = True):
    if decision["action"] != "send_template":
        print(f"Skipping {fields.get('emailAddress')}: {decision.get('reason')}")
        return

    sports = decision["sports"]
    ticket_type = decision["ticket_type"]

    filename = resolve_template_filename(sports, ticket_type)
    template_text = load_template(filename)

    filled_body = fill_template(template_text, fields, sports)
    subject = build_subject(sports, ticket_type)

    send_email(
        to_address=fields.get("emailAddress"),
        subject=subject,
        body=filled_body,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    from run_sf_parser import load_and_parse

    filepath = "data/csv_scrubbed.csv"  # update to your actual filename
    parsed_rows = load_and_parse(filepath)

    for fields, decision in parsed_rows:
        process_submission(fields, decision, dry_run=args.dry_run)