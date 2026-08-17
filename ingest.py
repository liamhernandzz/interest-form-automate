import csv
from pathlib import Path

DATA_FILE = Path("data/sample-submissions.csv")

def load_submissions(filepath: Path = DATA_FILE) -> list[dict]:
    """Read the CSV and return a list of submission records."""
    if not filepath.exists():
        raise FileNotFoundError(f"No submissions file found at {filepath}")

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        submissions = [row for row in reader]

    print(f"Loaded {len(submissions)} submissions from {filepath}")
    return submissions


if __name__ == "__main__":
    record = load_submissions()
    for r in record:
        print(r)