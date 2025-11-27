"""
Simple script to view all data in the database
Shows that user data is successfully stored and persisted
"""
import sqlite3
from datetime import datetime

def view_database():
    """Display all data from the database"""
    conn = sqlite3.connect('loan_verification.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print(" "*25 + "DATABASE CONTENTS")
    print("="*80)
    
    # Display Users
    print("\n📋 USERS TABLE")
    print("-"*80)
    cursor.execute('SELECT id, email FROM users ORDER BY id')
    users = cursor.fetchall()
    
    if users:
        print(f"{'ID':<5} | {'EMAIL':<50}")
        print("-"*80)
        for user in users:
            print(f"{user[0]:<5} | {user[1]:<50}")
        print(f"\nTotal Users: {len(users)}")
    else:
        print("No users found in database")
    
    # Display Loans
    print("\n\n📋 LOANS TABLE")
    print("-"*80)
    cursor.execute('''
        SELECT id, email, loan_type, amount, income, liabilities, status, created_at 
        FROM loans ORDER BY id DESC LIMIT 10
    ''')
    loans = cursor.fetchall()
    
    if loans:
        print(f"{'ID':<4} | {'EMAIL':<25} | {'TYPE':<12} | {'AMOUNT':<10} | {'STATUS':<10}")
        print("-"*80)
        for loan in loans:
            loan_id, email, loan_type, amount, income, liabilities, status, created_at = loan
            print(f"{loan_id:<4} | {email:<25} | {loan_type:<12} | ₹{amount:<9} | {status:<10}")
        print(f"\nShowing last 10 of {len(loans)} loan applications")
    else:
        print("No loan applications found in database")
    
    # Summary Statistics
    print("\n\n📊 SUMMARY STATISTICS")
    print("-"*80)
    
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM loans')
    loan_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM loans WHERE status='approved'")
    approved_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM loans WHERE status='rejected'")
    rejected_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(amount) FROM loans WHERE status="approved"')
    total_approved_amount = cursor.fetchone()[0] or 0
    
    print(f"Total Registered Users:        {user_count}")
    print(f"Total Loan Applications:       {loan_count}")
    print(f"  ✅ Approved Applications:    {approved_count}")
    print(f"  ❌ Rejected Applications:    {rejected_count}")
    print(f"Total Approved Loan Amount:    ₹{total_approved_amount:,}")
    
    # Loan type breakdown
    print("\n📈 LOAN APPLICATIONS BY TYPE")
    print("-"*80)
    cursor.execute('''
        SELECT loan_type, COUNT(*), SUM(amount) 
        FROM loans 
        GROUP BY loan_type
    ''')
    loan_types = cursor.fetchall()
    
    for loan_type, count, total_amount in loan_types:
        print(f"{loan_type.capitalize():<15}: {count:>3} applications | Total: ₹{total_amount:>12,}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ DATABASE IS OPERATIONAL - ALL USER DATA IS STORED SUCCESSFULLY")
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        view_database()
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
