import re
from ingest import load_submissions

#regex for email and phone number

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$") # assembles basic email address pattern

PHONE_PATTERN = re.compile(r"\D") # strips non-digits

def clean_phone(phone: str) -> str | None:

    if not phone:
        return None

    digits = PHONE_PATTERN.sub("", phone)

    if len(digits) != 10:
        return None

    return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email))

#build key to detect duplicate submissions based on email sport and ticket type
def create_dupe_key(record: dict) -> tuple:
    return (
        record.get("email", "").strip().lower(),
        record.get("sport", "").strip().lower(),
        record.get("ticket_type", "").strip().lower(),
    )

def validate_submissions(records: list[dict]) -> tuple[list[dict], list[dict]]:

    clean_records = []
    flagged_records = []

    #track which email/sport/ticket_type combos have been seen already
    seen_keys = set()

    for record in records:
        issues = []

        email = record.get("email", "").strip()
        if not is_valid_email(email):
            issues.append("Invalid or Missing Email")


        cleaned_phone = clean_phone(record.get("phone", ""))
        if cleaned_phone is None:
            issues.append("Missing or Invalid Phone Number")

        
        dupe_key = create_dupe_key(record)
        if dupe_key in seen_keys:
            issues.append("Duplicate Submission")
        else:
            seen_keys.add(dupe_key)


        for field in ("first_name", "last_name", "sport", "ticket_type"):
            if not record.get(field, "").strip():
                issues.append(f"missing {field}")

        if issues:
            flagged_copy = record.copy()
            flagged_copy["flag_reason"] = "; ".join(issues)
            flagged_records.append(flagged_copy)
        else:
            clean_copy = record.copy()
            clean_copy["phone"] = cleaned_phone
            clean_records.append(clean_copy)

    return clean_records, flagged_records

if __name__ == "__main__":
    raw_records = load_submissions()
    clean, flagged = validate_submissions(raw_records)

    print(f"\n{len(clean)} clean records:")
    for r in clean:
        print(r)

    print(f"\n{len(flagged)} flagged records (need review):")
    for r in flagged:
        print(r)