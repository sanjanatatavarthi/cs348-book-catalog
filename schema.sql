DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS genres;

CREATE TABLE genres (
  genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE books (
  book_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author_name TEXT NOT NULL,
  genre_id INTEGER NOT NULL,
  user_rating REAL,
  reviews INTEGER,
  price REAL,
  year INTEGER NOT NULL,
  FOREIGN KEY (genre_id) REFERENCES genres (genre_id)
);

CREATE INDEX idx_books_year ON books(year);
CREATE INDEX idx_books_genre_year_rating ON books(genre_id, year, user_rating);
