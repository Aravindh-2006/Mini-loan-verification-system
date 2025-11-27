"""
Script to add sample users to the database
Demonstrates how user data is stored in the database
"""
import sqlite3
import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(email, password):
    """Add a new user to the database"""
    conn = sqlite3.connect('loan_verification.db')
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (email, password) 
            VALUES (?, ?)
        ''', (email, hashed_password))
        conn.commit()
        print(f"✅ Successfully added user: {email}")
        return True
    except sqlite3.IntegrityError:
        print(f"⚠️  User already exists: {email}")
        return False
    finally:
        conn.close()

def display_all_users():
    """Display all users in the database"""
    conn = sqlite3.connect('loan_verification.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*60)
    print(f"TOTAL USERS IN DATABASE: {len(users)}")
    print("="*60)
    for user in users:
        print(f"  ID: {user[0]:3d} | Email: {user[1]}")
    print("="*60 + "\n")

# Sample users to add
sample_users = [
    ("john.doe@example.com", "password123"),
    ("jane.smith@example.com", "secure456"),
    ("mike.wilson@example.com", "mypass789"),
    ("sarah.jones@example.com", "safepass321"),
]

if __name__ == '__main__':
    print("\n🔧 ADDING SAMPLE USERS TO DATABASE")
    print("="*60)
    
    for email, password in sample_users:
        add_user(email, password)
    
    # Display all users
    display_all_users()
    
    print("✅ Database operations completed!")
    print("\n💡 TIP: You can now login with any of these users through the web interface")
    print("   Example: john.doe@example.com / password123\n")
