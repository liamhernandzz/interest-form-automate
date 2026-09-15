import csv
from salesforce_report_parser import parse_responses_blob

with open("data/csv_sensitive.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    first_row = next(reader)
    print("RAW BLOB:")
    print(repr(first_row.get("Responses")))
    print("\nPARSED FIELDS:")
    print(parse_responses_blob(first_row.get("Responses")))
