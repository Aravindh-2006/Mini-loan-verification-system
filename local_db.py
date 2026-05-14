"""
Local SQLite fallback database manager for Mini Loan Verification System.
Used when Supabase is unreachable (e.g., project paused / no internet).
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'local_loan_db.sqlite')

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    income INTEGER NOT NULL,
    liabilities INTEGER NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    documents TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

ADMIN_EMAIL = 'kit27.ad05@gmail.com'
ADMIN_PASSWORD_HASH = hashlib.sha256('kit@123'.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_local_db():
    """Create tables and seed admin user."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        # Seed admin user
        conn.execute(
            "INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)",
            (ADMIN_EMAIL, ADMIN_PASSWORD_HASH)
        )
        conn.commit()
        print("✅ Local SQLite database initialized.")
        print(f"   DB file: {DB_PATH}")
    except Exception as e:
        print(f"❌ Error initializing local DB: {e}")
    finally:
        conn.close()


class LocalDBManager:
    """Drop-in replacement for SupabaseManager using local SQLite."""

    def __init__(self):
        self.last_error = None
        init_local_db()
        print("✅ LocalDBManager ready (SQLite mode)")

    def _row_to_dict(self, row):
        if row is None:
            return None
        return dict(row)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email, password):
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, self.hash_password(password))
            )
            conn.commit()
            conn.close()
            print(f"✅ [LocalDB] User created: {email}")
            return True
        except Exception as e:
            print(f"❌ [LocalDB] Error creating user: {e}")
            return False

    def verify_user(self, email, password):
        try:
            conn = get_connection()
            row = conn.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, self.hash_password(password))
            ).fetchone()
            conn.close()
            return (row is not None), None
        except Exception as e:
            print(f"❌ [LocalDB] Error verifying user: {e}")
            return False, str(e)

    def get_user_by_email(self, email):
        try:
            conn = get_connection()
            row = conn.execute(
                "SELECT * FROM users WHERE email=?", (email,)
            ).fetchone()
            conn.close()
            return self._row_to_dict(row), None
        except Exception as e:
            print(f"❌ [LocalDB] Error getting user: {e}")
            return None, str(e)

    def create_loan_application(self, email, loan_type, amount, income, liabilities, status, reason, documents):
        try:
            conn = get_connection()
            cursor = conn.execute(
                """INSERT INTO loans (email, loan_type, amount, income, liabilities, status, reason, documents)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (email, loan_type, amount, income, liabilities, status, reason, documents)
            )
            loan_id = cursor.lastrowid
            conn.commit()
            conn.close()
            print(f"✅ [LocalDB] Loan application created with ID: {loan_id}")
            return loan_id
        except Exception as e:
            print(f"❌ [LocalDB] Error creating loan application: {e}")
            return None

    def update_loan_status(self, loan_id, status, remarks):
        try:
            conn = get_connection()
            result = conn.execute(
                "UPDATE loans SET status=?, reason=? WHERE id=?",
                (status, remarks, loan_id)
            )
            conn.commit()
            conn.close()
            if result.rowcount == 0:
                print(f"⚠️  [LocalDB] No rows updated for loan {loan_id}")
                return False
            print(f"✅ [LocalDB] Loan {loan_id} status updated to {status}")
            return True
        except Exception as e:
            print(f"❌ [LocalDB] Error updating loan status: {e}")
            return False

    def get_user_loans(self, email):
        try:
            conn = get_connection()
            rows = conn.execute(
                "SELECT * FROM loans WHERE email=? ORDER BY created_at DESC", (email,)
            ).fetchall()
            conn.close()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"❌ [LocalDB] Error getting user loans: {e}")
            return []

    def get_all_loans(self):
        try:
            conn = get_connection()
            rows = conn.execute(
                "SELECT * FROM loans ORDER BY created_at DESC"
            ).fetchall()
            conn.close()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"❌ [LocalDB] Error getting all loans: {e}")
            return []

    def get_loan_by_id(self, loan_id):
        try:
            conn = get_connection()
            row = conn.execute(
                "SELECT * FROM loans WHERE id=?", (loan_id,)
            ).fetchone()
            conn.close()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"❌ [LocalDB] Error getting loan by ID: {e}")
            return None

    def upload_file(self, file_data, filename, folder=''):
        """Save file locally instead of Supabase Storage."""
        try:
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', folder or '')
            os.makedirs(upload_dir, exist_ok=True)
            file_path_local = os.path.join(upload_dir, filename)
            with open(file_path_local, 'wb') as f:
                f.write(file_data)
            # Return a relative path similar to Supabase storage paths
            rel_path = os.path.join(folder or '', filename).replace('\\', '/')
            print(f"✅ [LocalDB] File saved locally: {rel_path}")
            self.last_error = None
            return rel_path
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ [LocalDB] Error saving file: {e}")
            return None

    def get_file_url(self, file_path):
        """Return a local URL for the file."""
        return f"/local_file/{file_path}"

    def init_storage(self):
        """No-op for local mode."""
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ [LocalDB] Local uploads folder ready.")
