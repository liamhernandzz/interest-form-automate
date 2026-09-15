import re
from urllib.parse import unquote_plus

# The fixed set of field names that appear in every export.
# Order doesn't matter here - the regex handles that.
KNOWN_FIELDS = [
    "emailAddress", "firstName", "lastName", "mobilePhone", "zipPostal",
    "Football", "Volleyball", "mensBasketball", "Softball",
    "womensBasketball", "Baseball", "PremiumSeating",
    "SingleGameTickets", "SeasonTickets", "GroupTickets",
    "additionalQuestionsorComments", "submit",
]

# Build a regex that matches: FIELDNAME=VALUE, where VALUE is
# "everything up to the next known fieldname= or the end of string"
_field_alternation = "|".join(KNOWN_FIELDS)
FIELD_PATTERN = re.compile(
    rf"({_field_alternation})=(.*?)(?=(?:{_field_alternation})=|$)"
)

SPORT_FIELDS = [
    "Football", "Volleyball", "mensBasketball", "Softball",
    "womensBasketball", "Baseball",
]

TICKET_TYPE_FIELDS = ["SingleGameTickets", "SeasonTickets", "GroupTickets"]


def parse_responses_blob(blob: str) -> dict:
    """Turn the raw Responses string into a clean dict of field values."""
    matches = FIELD_PATTERN.findall(blob)
    fields = {key: value.strip() for key, value in matches}

    # The comments field uses "+" for spaces (URL-encoded form style),
    # so decode it into readable text.
    if "additionalQuestionsorComments" in fields:
        fields["additionalQuestionsorComments"] = unquote_plus(
            fields["additionalQuestionsorComments"]
        )

    return fields


def get_interested_sports(fields: dict) -> list[str]:
    """Return list of sport field names that were marked 'on'."""
    return [sport for sport in SPORT_FIELDS if fields.get(sport) == "on"]


def get_ticket_type(fields: dict) -> str | None:
    """Return the ticket type marked 'on', or None if none set."""
    for ticket_type in TICKET_TYPE_FIELDS:
        if fields.get(ticket_type) == "on":
            return ticket_type
    return None


def has_custom_comments(fields: dict) -> bool:
    """True if the submitter wrote a specific request/comment."""
    comment = fields.get("additionalQuestionsorComments", "").strip()
    return bool(comment)


def route_submission(fields: dict) -> dict:
    """
    Decide how this submission should be handled:
    - flagged for manual reply if there's a custom comment
    - otherwise routed to a template based on sport(s) + ticket type
    """
    if has_custom_comments(fields):
        return {"action": "manual_review", "reason": "custom comment present"}

    sports = get_interested_sports(fields)
    ticket_type = get_ticket_type(fields)

    if not sports or not ticket_type:
        return {"action": "manual_review", "reason": "missing sport or ticket type"}

    # Multiple sports selected -> route to the combined/multi-sport template
    # instead of trying to pick just one
    if len(sports) > 1:
        template_key = ("multi_sport", ticket_type)
    else:
        template_key = (sports[0], ticket_type)

    return {
        "action": "send_template",
        "sports": sports,
        "ticket_type": ticket_type,
        "template_key": template_key,
    }

if __name__ == "__main__":
    # Synthetic test row shaped like the real export, no real PII
    sample_blob = (
        "Submitted a Form. Data Submitted: emailAddress=test@example.com "
        "firstName=Alex lastName=Rivera mobilePhone=5125550142 "
        "zipPostal=78701Football=on Volleyball= mensBasketball= Softball= "
        "womensBasketball= Baseball= PremiumSeating= SingleGameTickets=on "
        "SeasonTickets= GroupTickets= additionalQuestionsorComments= submit="
    )

    parsed = parse_responses_blob(sample_blob)
    print(parsed)
    print(route_submission(parsed))

    