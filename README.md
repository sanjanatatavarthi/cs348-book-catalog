# CS348 Stage 3 - Minimal Book Catalog App

This is a minimal Flask + SQLite app that satisfies Stage 2 and adds the pieces needed to explain Stage 3.

## What the project shows
- Requirement 1: add, edit, and delete books
- Requirement 2: filter books and generate a report
- Dynamic UI from DB: genre dropdowns and year dropdown are loaded from the database
- SQL injection protection: parameterized queries and input validation
- Indexes: report and dropdown queries are supported by indexes
- Transactions: all write operations run inside an explicit transaction helper
- AI Usage section: see `AI_USAGE.md`

## Files for Stage 3
- `app.py` - Flask app with input validation and transaction helper
- `schema.sql` - tables and indexes
- `init_db.py` - creates and seeds the database
- `show_query_plan.py` - prints SQLite query plans for the indexed queries
- `AI_USAGE.md` - AI usage section you can discuss in your demo
- `STAGE3_NOTES.md` - concise explanations for the Stage 3 topics
- `Procfile` and `Dockerfile` - optional deployment helpers
- `deploy/` - Compute Engine helper files for the extra credit path

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Open the app at `http://127.0.0.1:5000`.

## Stage 3 demo preparation
To show the query plans for indexes:
```bash
python show_query_plan.py
```

## Suggested Stage 3 talking points
1. Show `AI_USAGE.md`
2. Show `schema.sql` and point out the indexes
3. Show `show_query_plan.py` output and connect each index to a query
4. Show `app.py` placeholders `?` in the SQL for injection protection
5. Show `sanitize_text`, `parse_int`, `parse_float`, and `validate_genre_id`
6. Show `run_write_transaction()` and explain `BEGIN IMMEDIATE`, commit, and rollback
7. Open the app and quickly prove CRUD and report still work

## Cloud extra credit note
The app includes a `Dockerfile`, but SQLite is not the best choice for managed serverless deployment when graders need to test live writes. For extra credit on a major cloud provider, a single VM is the simplest path if you want to keep SQLite.

## Optional VM deployment helper
If you deploy to a single Ubuntu VM on Google Compute Engine, copy the project folder to the VM and run:
```bash
bash deploy/deploy_vm_setup.sh
```
This sets up Python, installs dependencies, initializes the database, configures gunicorn, and configures nginx.
