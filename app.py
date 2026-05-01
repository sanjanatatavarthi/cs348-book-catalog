from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'books.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs348-stage3-demo'


def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    return conn


def fetch_genres():
    conn = get_db_connection()
    try:
        return conn.execute(
            'SELECT genre_id, name FROM genres ORDER BY name'
        ).fetchall()
    finally:
        conn.close()


def sanitize_text(value, field_name, max_length=200):
    cleaned = ' '.join((value or '').strip().split())
    if not cleaned:
        raise ValueError(f'{field_name} is required.')
    if len(cleaned) > max_length:
        raise ValueError(f'{field_name} must be at most {max_length} characters long.')
    return cleaned


def parse_int(value, field_name, min_value=None, max_value=None, required=False):
    cleaned = (value or '').strip()
    if not cleaned:
        if required:
            raise ValueError(f'{field_name} is required.')
        return None
    try:
        parsed = int(cleaned)
    except ValueError as exc:
        raise ValueError(f'{field_name} must be a whole number.') from exc
    if min_value is not None and parsed < min_value:
        raise ValueError(f'{field_name} must be at least {min_value}.')
    if max_value is not None and parsed > max_value:
        raise ValueError(f'{field_name} must be at most {max_value}.')
    return parsed


def parse_float(value, field_name, min_value=None, max_value=None, required=False):
    cleaned = (value or '').strip()
    if not cleaned:
        if required:
            raise ValueError(f'{field_name} is required.')
        return None
    try:
        parsed = float(cleaned)
    except ValueError as exc:
        raise ValueError(f'{field_name} must be a number.') from exc
    if min_value is not None and parsed < min_value:
        raise ValueError(f'{field_name} must be at least {min_value}.')
    if max_value is not None and parsed > max_value:
        raise ValueError(f'{field_name} must be at most {max_value}.')
    return parsed


def validate_genre_id(genre_id):
    conn = get_db_connection()
    try:
        row = conn.execute(
            'SELECT genre_id FROM genres WHERE genre_id = ?',
            (genre_id,)
        ).fetchone()
        if row is None:
            raise ValueError('Selected genre is invalid.')
    finally:
        conn.close()
    return genre_id


def get_book_form_data(form):
    title = sanitize_text(form.get('title'), 'Title')
    author_name = sanitize_text(form.get('author_name'), 'Author')
    genre_id = parse_int(form.get('genre_id'), 'Genre', min_value=1, required=True)
    genre_id = validate_genre_id(genre_id)
    user_rating = parse_float(form.get('user_rating'), 'User rating', min_value=0, max_value=5)
    reviews = parse_int(form.get('reviews'), 'Reviews', min_value=0)
    price = parse_float(form.get('price'), 'Price', min_value=0)
    year = parse_int(form.get('year'), 'Year', min_value=1900, max_value=2100, required=True)

    return {
        'title': title,
        'author_name': author_name,
        'genre_id': genre_id,
        'user_rating': user_rating,
        'reviews': reviews,
        'price': price,
        'year': year,
    }


def render_book_form(form_title, submit_label, book=None):
    return render_template(
        'book_form.html',
        form_title=form_title,
        submit_label=submit_label,
        book=book,
        genres=fetch_genres()
    )


def run_write_transaction(operation):
    conn = get_db_connection()
    try:
        conn.execute('BEGIN IMMEDIATE')
        result = operation(conn)
        conn.commit()
        return result
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.route('/')
def index():
    return redirect(url_for('list_books'))


@app.route('/books')
def list_books():
    conn = get_db_connection()
    try:
        books = conn.execute(
            '''
            SELECT b.book_id,
                   b.title,
                   b.author_name,
                   g.name AS genre_name,
                   b.user_rating,
                   b.reviews,
                   b.price,
                   b.year
            FROM books b
            JOIN genres g ON b.genre_id = g.genre_id
            ORDER BY b.year DESC, b.title ASC
            '''
        ).fetchall()
        return render_template('books.html', books=books)
    finally:
        conn.close()


@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            form_data = get_book_form_data(request.form)
        except ValueError as exc:
            flash(str(exc))
            return render_book_form('Add Book', 'Add Book', request.form)

        try:
            def insert_book(conn):
                conn.execute(
                    '''
                    INSERT INTO books (title, author_name, genre_id, user_rating, reviews, price, year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        form_data['title'],
                        form_data['author_name'],
                        form_data['genre_id'],
                        form_data['user_rating'],
                        form_data['reviews'],
                        form_data['price'],
                        form_data['year']
                    )
                )

            run_write_transaction(insert_book)
        except sqlite3.Error:
            flash('Could not add the book. Please try again.')
            return render_book_form('Add Book', 'Add Book', request.form)

        flash('Book added successfully.')
        return redirect(url_for('list_books'))

    return render_book_form('Add Book', 'Add Book')


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = get_db_connection()
    try:
        book = conn.execute('SELECT * FROM books WHERE book_id = ?', (book_id,)).fetchone()
    finally:
        conn.close()

    if book is None:
        flash('Book not found.')
        return redirect(url_for('list_books'))

    if request.method == 'POST':
        try:
            form_data = get_book_form_data(request.form)
        except ValueError as exc:
            flash(str(exc))
            return render_book_form('Edit Book', 'Save Changes', request.form)

        try:
            def update_book(conn):
                conn.execute(
                    '''
                    UPDATE books
                    SET title = ?,
                        author_name = ?,
                        genre_id = ?,
                        user_rating = ?,
                        reviews = ?,
                        price = ?,
                        year = ?
                    WHERE book_id = ?
                    ''',
                    (
                        form_data['title'],
                        form_data['author_name'],
                        form_data['genre_id'],
                        form_data['user_rating'],
                        form_data['reviews'],
                        form_data['price'],
                        form_data['year'],
                        book_id
                    )
                )

            run_write_transaction(update_book)
        except sqlite3.Error:
            flash('Could not update the book. Please try again.')
            return render_book_form('Edit Book', 'Save Changes', request.form)

        flash('Book updated successfully.')
        return redirect(url_for('list_books'))

    return render_book_form('Edit Book', 'Save Changes', book)


@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        def remove_book(conn):
            conn.execute('DELETE FROM books WHERE book_id = ?', (book_id,))

        run_write_transaction(remove_book)
        flash('Book deleted successfully.')
    except sqlite3.Error:
        flash('Could not delete the book. Please try again.')

    return redirect(url_for('list_books'))


@app.route('/report')
def report():
    try:
        genre_id = parse_int(request.args.get('genre_id'), 'Genre', min_value=1)
        year = parse_int(request.args.get('year'), 'Year', min_value=1900, max_value=2100)
        min_rating = parse_float(request.args.get('min_rating'), 'Minimum rating', min_value=0, max_value=5)
    except ValueError as exc:
        flash(str(exc))
        genre_id = None
        year = None
        min_rating = None

    conn = get_db_connection()
    try:
        genres = conn.execute('SELECT genre_id, name FROM genres ORDER BY name').fetchall()
        years = conn.execute('SELECT DISTINCT year FROM books ORDER BY year DESC').fetchall()

        query = '''
            SELECT b.title,
                   b.author_name,
                   g.name AS genre_name,
                   b.user_rating,
                   b.reviews,
                   b.price,
                   b.year
            FROM books b
            JOIN genres g ON b.genre_id = g.genre_id
            WHERE 1 = 1
        '''
        params = []

        if genre_id is not None:
            query += ' AND b.genre_id = ?'
            params.append(genre_id)
        if year is not None:
            query += ' AND b.year = ?'
            params.append(year)
        if min_rating is not None:
            query += ' AND b.user_rating >= ?'
            params.append(min_rating)

        query += ' ORDER BY b.year DESC, b.title ASC'
        books = conn.execute(query, params).fetchall()

        stats_query = '''
            SELECT COUNT(*) AS total_books,
                   ROUND(AVG(user_rating), 2) AS avg_rating,
                   ROUND(AVG(price), 2) AS avg_price
            FROM books
            WHERE 1 = 1
        '''
        stats_params = []

        if genre_id is not None:
            stats_query += ' AND genre_id = ?'
            stats_params.append(genre_id)
        if year is not None:
            stats_query += ' AND year = ?'
            stats_params.append(year)
        if min_rating is not None:
            stats_query += ' AND user_rating >= ?'
            stats_params.append(min_rating)

        stats = conn.execute(stats_query, stats_params).fetchone()
    finally:
        conn.close()

    selected_filters = {
        'genre_id': '' if genre_id is None else str(genre_id),
        'year': '' if year is None else str(year),
        'min_rating': '' if min_rating is None else str(min_rating),
    }

    return render_template(
        'report.html',
        books=books,
        genres=genres,
        years=years,
        stats=stats,
        selected_filters=selected_filters
    )


if __name__ == '__main__':
    app.run(debug=True)
