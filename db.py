import sqlite3
from pathlib import Path
from datetime import datetime, date

DB_PATH = Path("library.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                total_copies INTEGER NOT NULL CHECK(total_copies >= 0),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrowed_at TEXT NOT NULL,
                due_date TEXT NOT NULL,
                returned_at TEXT,
                FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE,
                FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
            );
            """
        )

def add_book(title: str, author: str, isbn: str, total_copies: int):
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO books(title, author, isbn, total_copies, created_at) VALUES(?,?,?,?,?)",
            (title.strip(), author.strip(), isbn.strip(), int(total_copies), now),
        )

def update_book(book_id: int, title: str, author: str, isbn: str, total_copies: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE books SET title=?, author=?, isbn=?, total_copies=? WHERE id=?",
            (title.strip(), author.strip(), isbn.strip(), int(total_copies), int(book_id)),
        )

def delete_book(book_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM books WHERE id=?", (int(book_id),))

def get_books():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books ORDER BY title COLLATE NOCASE")
        return [dict(row) for row in cur.fetchall()]

def get_book_by_id(book_id: int):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM books WHERE id=?", (int(book_id),))
        row = cur.fetchone()
        return dict(row) if row else None

def get_active_loans_count(book_id: int):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) AS c FROM loans WHERE book_id=? AND returned_at IS NULL",
            (int(book_id),),
        )
        return int(cur.fetchone()["c"])

def get_available_copies(book_id: int):
    book = get_book_by_id(book_id)
    if not book:
        return 0
    active = get_active_loans_count(book_id)
    return max(0, int(book["total_copies"]) - active)

def add_member(name: str, email: str, phone: str | None = None):
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO members(name, email, phone, created_at) VALUES(?,?,?,?)",
            (name.strip(), email.strip(), (phone or "").strip(), now),
        )

def update_member(member_id: int, name: str, email: str, phone: str | None = None):
    with get_connection() as conn:
        conn.execute(
            "UPDATE members SET name=?, email=?, phone=? WHERE id=?",
            (name.strip(), email.strip(), (phone or "").strip(), int(member_id)),
        )

def delete_member(member_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM members WHERE id=?", (int(member_id),))

def get_members():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM members ORDER BY name COLLATE NOCASE")
        return [dict(row) for row in cur.fetchall()]

def get_member_by_id(member_id: int):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM members WHERE id=?", (int(member_id),))
        row = cur.fetchone()
        return dict(row) if row else None

def borrow_book(member_id: int, book_id: int, due: date):
    if get_available_copies(book_id) <= 0:
        raise ValueError("No copies available")
    borrowed_at = datetime.utcnow().isoformat()
    due_date = due.isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO loans(member_id, book_id, borrowed_at, due_date) VALUES(?,?,?,?)",
            (int(member_id), int(book_id), borrowed_at, due_date),
        )

def return_book(loan_id: int):
    returned_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE loans SET returned_at=? WHERE id=? AND returned_at IS NULL",
            (returned_at, int(loan_id)),
        )

def get_loans(active_only: bool = False):
    q = "SELECT * FROM loans"
    if active_only:
        q += " WHERE returned_at IS NULL"
    q += " ORDER BY borrowed_at DESC"
    with get_connection() as conn:
        cur = conn.execute(q)
        return [dict(row) for row in cur.fetchall()]

def get_overdue(today: date | None = None):
    t = (today or date.today()).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM loans WHERE returned_at IS NULL AND due_date < ? ORDER BY due_date ASC",
            (t,),
        )
        return [dict(row) for row in cur.fetchall()]

