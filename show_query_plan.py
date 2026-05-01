import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / 'books.db'

QUERIES = {
    'year_dropdown': (
        'SELECT DISTINCT year FROM books ORDER BY year DESC',
        ()
    ),
    'report_genre_year_rating': (
        '''
        SELECT b.title
        FROM books b
        WHERE b.genre_id = ? AND b.year = ? AND b.user_rating >= ?
        ORDER BY b.year DESC, b.title ASC
        ''',
        (1, 2020, 4.5)
    ),
    'report_year_only': (
        '''
        SELECT b.title
        FROM books b
        WHERE b.year = ?
        ORDER BY b.year DESC, b.title ASC
        ''',
        (2020,)
    )
}


def main():
    conn = sqlite3.connect(DATABASE)
    try:
        for name, (query, params) in QUERIES.items():
            print(f'\n{name}')
            print('-' * len(name))
            rows = conn.execute('EXPLAIN QUERY PLAN ' + query, params).fetchall()
            for row in rows:
                print(row)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
