import csv
from salesforce_report_parser import parse_responses_blob, route_submission


def load_and_parse(filepath: str, responses_column: str = "Responses"):
    """
    Open the CSV and parse each row's Responses blob.

    responses_column: the header name of the column containing the
                       raw Responses text (matches your export's header).
    """
    results = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            blob = row.get(responses_column)
            if not blob:
                continue  # skip blank rows

            fields = parse_responses_blob(blob)
            decision = route_submission(fields)
            results.append((fields, decision))

    return results


if __name__ == "__main__":
    filepath = "data/csv_sensitive.csv"  # update to your actual filename
    parsed = load_and_parse(filepath)

    for fields, decision in parsed:
        print(fields.get("firstName"), fields.get("lastName"), "->", decision)