import sqlite3
import hashlib

def check_and_init_database():
    """Check database status and initialize if needed"""
    conn = sqlite3.connect('loan_verification.db')
    cursor = conn.cursor()
    
    # Check existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Existing tables:", tables)
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create loans table if not exists
    cursor.execute('''
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert demo user if not exists
    demo_password = hashlib.sha256('kit@123'.encode()).hexdigest()
    try:
        cursor.execute('''
            INSERT INTO users (email, password) 
            VALUES (?, ?)
        ''', ('kit27.ad05@gmail.com', demo_password))
        print("Demo user created successfully!")
    except sqlite3.IntegrityError:
        print("Demo user already exists")
    
    conn.commit()
    
    # Show all users
    cursor.execute('SELECT id, email FROM users')
    users = cursor.fetchall()
    print("\nRegistered Users:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}")
    
    # Show all loans
    cursor.execute('SELECT COUNT(*) FROM loans')
    loan_count = cursor.fetchone()[0]
    print(f"\nTotal Loan Applications: {loan_count}")
    
    conn.close()
    print("\n✅ Database initialized successfully!")

if __name__ == '__main__':
    check_and_init_database()
