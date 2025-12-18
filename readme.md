Library Management (Streamlit)

A lightweight Library Management web app built with Streamlit and SQLite. It supports managing books, members, and loans with a simple UI. Data is stored locally in a SQLite database file (library.db).

Features
- Dashboard with key metrics: total books, members, active and overdue loans
- Books: add, edit, delete, list; tracks total and available copies
- Members: add, edit, delete, list
- Loans: borrow and return books; overdue detection
- Zero external DB setup (uses SQLite)

Tech Stack
- Python 3.10+
- Streamlit (UI)
- SQLite (storage)

Project Structure
- app.py: Streamlit UI and app logic
- db.py: SQLite schema and data-access functions
- requirement.txt: Python dependency list
- readme.md: This file
- .gitignore

Getting Started
1) Prerequisites
- Python 3.10 or newer installed and on PATH

2) Install dependencies
- Create and activate a virtual environment (recommended)
  - Windows (cmd):
    python -m venv .venv
    .venv\\Scripts\\activate
  - PowerShell:
    python -m venv .venv
    .venv\\Scripts\\Activate.ps1
- Install packages
    pip install -r requirement.txt

3) Run the app
- From the project root:
    streamlit run app.py
- Streamlit will open a browser window. If it doesn’t, visit the URL shown in the terminal (typically http://localhost:8501).

Usage Guide
- Dashboard: View counts and see recent/active loans and overdue items
- Books:
  - Add: title, author, ISBN, total copies
  - Manage: select a book to update or delete
  - Availability: computed as total copies minus active loans
- Members:
  - Add: name and email required (phone optional)
  - Manage: update or delete members
- Loans:
  - Borrow: select member and book, set a due date
  - Return: select an active loan to mark returned
  - Overdue: list of unreturned loans past due date

Data Storage
- A SQLite file named library.db is created in the project directory on first run
- Foreign keys are enforced; deleting a member or book cascades to their loans

Common Issues & Tips
- If you see "No copies available" while borrowing, either add more total copies or return existing loans
- If the app doesn’t start, ensure your virtual environment is activated and dependencies are installed
- On Windows, if Activate.ps1 execution is blocked, allow scripts temporarily:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Development Notes
- Database schema is auto-created by init_db() on app startup
- All data-access is defined in db.py for easier testing and maintenance
- Streamlit state is ephemeral; persistent data lives in library.db

Testing Locally
- Start fresh by deleting library.db (this removes all data)
- Add a few books and members, then create and return loans to validate flows

Extending
- Add search/filtering for books and members
- Add loan history views per member/book
- Export reports (CSV)
- Authentication/roles if deploying multi-user

License
- MIT (or update as appropriate)
