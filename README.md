# interest-form-automate
Process ticket interest form data and send responses using reference email templates for sport and ticket type(season/single)

Supports Salesforce report exports in csv format

Only dry runs with personal emails are supported 

The csv_scrubbed.csv file contains Salesforce reports scrubbed of identifying information, retaining the same response format 

INSTRUCTIONS + LOGIC: 

Each submission specifies one or more sports (`Football`, `Volleyball`,
`mensBasketball`, `Softball`, `womensBasketball`, `Baseball`) and one
ticket type (`SingleGameTickets`, `SeasonTickets`, `GroupTickets`).

**Routing rules, in order:**

1. **Custom comment present** — if `additionalQuestionsorComments` is
   non-blank, the submission is flagged for `manual_review` instead of
   an automated reply, since it likely contains a specific request that
   a template can't address.

2. **Multiple sports selected** — routes to `templates/multi_sport.txt`
   regardless of ticket type.

3. **Single sport + ticket type** — routes to the matching file, named
   `{sport_prefix}_{ticket_suffix}.txt`, e.g. `football_single.txt`,
   `softball_season.txt`, `wbasket_group.txt`.

4. **Missing sport or ticket type** — flagged for `manual_review`
   rather than guessing.

Templates are static text (no placeholders/personalization currently).
Subject lines are generated in code from the sport + ticket type, not
stored in the template files.

## Setup

1. Clone the repo and install dependencies:
```bash
   pip install -r requirements.txt
```

2. Create a `.env` file in the project root (this file is gitignored
   and should never be committed):

GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password


   To get a Gmail App Password:
   - Enable 2-Step Verification: https://myaccount.google.com/security
   - Generate an app password: https://myaccount.google.com/apppasswords
   - Use the generated 16-character password, not your regular Gmail password

3. Place your (scrubbed/synthetic) CSV export in `data/` and update the
   `filepath` variable in `run_sf_parser.py` / `emailer.py` to match.

## Running

Dry-run (default, safe — prints instead of sending):
```bash
python emailer.py
```

Real send:
```bash
python emailer.py --send
```

## Data safety note

This repo is built and tested against synthetic/scrubbed data only.
Do not commit real customer PII (names, emails, phone numbers) —
`.gitignore` excludes `.env`, but always double-check `data/` contents
before committing.