# Stage 3 Notes

## SQL injection protection
This app uses parameterized SQL queries everywhere user input is involved. SQLite placeholders use `?` and the data values are passed separately from the SQL string.

Examples:
- Insert in `add_book()`
- Update in `edit_book()`
- Delete in `delete_book()`
- Filtered report in `report()`

The app also validates and sanitizes input before sending it to the database:
- trims and normalizes text
- checks required fields
- converts numbers safely
- enforces ranges like rating 0-5 and year 1900-2100
- checks that the selected genre actually exists

## Indexes
This app adds two indexes in `schema.sql`.

### 1. `idx_books_year`
Supports:
- `SELECT DISTINCT year FROM books ORDER BY year DESC`
- report filters when the user filters by year only

### 2. `idx_books_genre_year_rating`
Supports:
- report filters on genre
- report filters on genre + year
- report filters on genre + year + minimum rating

These are meaningful because the report page is one of the most frequently used queries in the app, and the year dropdown is also built from database data.

## Transactions and isolation
All writes are wrapped in `run_write_transaction()`.

That helper:
- opens a database connection
- starts `BEGIN IMMEDIATE`
- executes the write query
- commits on success
- rolls back on failure

Reason:
- it makes each add, edit, or delete operation atomic
- if something fails in the middle, the database is rolled back instead of being left half-updated
- `BEGIN IMMEDIATE` is a clear way to reserve the write lock at the start of the transaction

SQLite uses serializable transactions by default unless changed, and this project keeps the default. WAL mode is enabled to improve concurrency because readers can continue while a writer is active.
