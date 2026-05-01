import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'books.db'
SCHEMA = BASE_DIR / 'schema.sql'

GENRES = ['Fiction', 'Non Fiction']

BOOKS = [
    ('Becoming', 'Michelle Obama', 'Non Fiction', 4.8, 61133, 11.89, 2019),
    ('Educated', 'Tara Westover', 'Non Fiction', 4.7, 28729, 13.99, 2018),
    ('The Silent Patient', 'Alex Michaelides', 'Fiction', 4.5, 27536, 14.49, 2019),
    ('Where the Crawdads Sing', 'Delia Owens', 'Fiction', 4.8, 87841, 9.98, 2019),
    ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Non Fiction', 4.6, 26490, 14.99, 2017),
    ('The Four Agreements', 'Don Miguel Ruiz', 'Non Fiction', 4.7, 23308, 6.78, 2018),
    ('The Alchemist', 'Paulo Coelho', 'Fiction', 4.7, 35799, 8.39, 2017),
    ('The Great Alone', 'Kristin Hannah', 'Fiction', 4.8, 30358, 14.40, 2018),
    ('Atomic Habits', 'James Clear', 'Non Fiction', 4.8, 29636, 11.98, 2019),
    ('Little Fires Everywhere', 'Celeste Ng', 'Fiction', 4.5, 25706, 12.37, 2018),
    ('The Midnight Library', 'Matt Haig', 'Fiction', 4.6, 18500, 13.25, 2020),
    ('Greenlights', 'Matthew McConaughey', 'Non Fiction', 4.7, 24100, 15.20, 2020),
    ('Project Hail Mary', 'Andy Weir', 'Fiction', 4.9, 19000, 16.99, 2021),
    ('The Psychology of Money', 'Morgan Housel', 'Non Fiction', 4.8, 21200, 12.99, 2021),
]


def main():
    if DATABASE.exists():
        DATABASE.unlink()
    wal_file = DATABASE.with_suffix('.db-wal')
    shm_file = DATABASE.with_suffix('.db-shm')
    if wal_file.exists():
        wal_file.unlink()
    if shm_file.exists():
        shm_file.unlink()

    conn = sqlite3.connect(DATABASE)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')

    with open(SCHEMA, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    conn.executemany('INSERT INTO genres (name) VALUES (?)', [(g,) for g in GENRES])

    genre_lookup = {
        row[1]: row[0]
        for row in conn.execute('SELECT genre_id, name FROM genres').fetchall()
    }

    conn.executemany(
        '''
        INSERT INTO books (title, author_name, genre_id, user_rating, reviews, price, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (title, author, genre_lookup[genre_name], rating, reviews, price, year)
            for title, author, genre_name, rating, reviews, price, year in BOOKS
        ]
    )

    conn.commit()
    conn.close()
    print('Database initialized: books.db')


if __name__ == '__main__':
    main()
