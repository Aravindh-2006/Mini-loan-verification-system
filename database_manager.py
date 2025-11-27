import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    """Manage loan verification database operations"""
    
    def __init__(self, db_name='loan_verification.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create loans table
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully!")
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email, password):
        """Create a new user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password) 
                VALUES (?, ?)
            ''', (email, hashed_password))
            conn.commit()
            print(f"✅ User created: {email}")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ User already exists: {email}")
            return False
        finally:
            conn.close()
    
    def get_all_users(self):
        """Get all registered users"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id, email FROM users ORDER BY id')
        users = cursor.fetchall()
        conn.close()
        return users
    
    def create_loan_application(self, email, loan_type, amount, income, liabilities, status, reason, documents):
        """Create a new loan application"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO loans (email, loan_type, amount, income, liabilities, status, reason, documents)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, loan_type, amount, income, liabilities, status, reason, documents))
        
        conn.commit()
        loan_id = cursor.lastrowid
        conn.close()
        print(f"✅ Loan application created with ID: {loan_id}")
        return loan_id
    
    def get_user_loans(self, email):
        """Get all loans for a specific user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, loan_type, amount, income, liabilities, status, reason, created_at
            FROM loans WHERE email = ? ORDER BY created_at DESC
        ''', (email,))
        loans = cursor.fetchall()
        conn.close()
        return loans
    
    def get_all_loans(self):
        """Get all loan applications"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, loan_type, amount, income, liabilities, status, reason, created_at
            FROM loans ORDER BY created_at DESC
        ''')
        loans = cursor.fetchall()
        conn.close()
        return loans
    
    def display_database_stats(self):
        """Display database statistics"""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        # Users
        users = self.get_all_users()
        print(f"\n📊 Total Registered Users: {len(users)}")
        print("\nUser List:")
        for user in users:
            print(f"  • ID: {user[0]}, Email: {user[1]}")
        
        # Loans
        loans = self.get_all_loans()
        print(f"\n📊 Total Loan Applications: {len(loans)}")
        
        # Loan status breakdown
        approved = sum(1 for loan in loans if loan[6] == 'approved')
        rejected = sum(1 for loan in loans if loan[6] == 'rejected')
        print(f"  ✅ Approved: {approved}")
        print(f"  ❌ Rejected: {rejected}")
        
        # Loan type breakdown
        loan_types = {}
        for loan in loans:
            loan_type = loan[2]
            loan_types[loan_type] = loan_types.get(loan_type, 0) + 1
        
        print("\n📈 Loan Applications by Type:")
        for loan_type, count in loan_types.items():
            print(f"  • {loan_type.capitalize()}: {count}")
        
        print("\n" + "="*60)

# Demo usage
if __name__ == '__main__':
    db = DatabaseManager()
    
    # Display current database stats
    db.display_database_stats()
    
    # Example: Create a new user
    print("\n\n🔧 DEMO: Creating a new test user...")
    db.create_user('testuser@example.com', 'testpass123')
    
    # Example: Create a loan application
    print("\n🔧 DEMO: Creating a test loan application...")
    db.create_loan_application(
        email='testuser@example.com',
        loan_type='education',
        amount=300000,
        income=50000,
        liabilities=2,
        status='approved',
        reason='All conditions satisfied',
        documents='admission_letter.pdf,income_proof.pdf'
    )
    
    print("\n\n✅ Database operations completed successfully!")
    print("="*60)
