# Database Information - Loan Verification System

## ✅ Database Successfully Created and Operational

### Database File
- **Name**: `loan_verification.db`
- **Type**: SQLite3
- **Location**: Project root directory

---

## 📊 Database Schema

### 1. **Users Table**
Stores all registered user accounts.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

**Fields:**
- `id`: Auto-incrementing unique identifier
- `email`: User's email address (unique)
- `password`: SHA256 hashed password

### 2. **Loans Table**
Stores all loan applications submitted by users.

```sql
CREATE TABLE loans (
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
);
```

**Fields:**
- `id`: Auto-incrementing unique identifier
- `email`: User's email (foreign key reference)
- `loan_type`: Type of loan (agriculture, home, education, business)
- `amount`: Loan amount requested
- `income`: User's monthly income
- `liabilities`: Number of existing loans
- `status`: Application status (approved/rejected)
- `reason`: Reason for approval/rejection
- `documents`: Comma-separated list of uploaded documents
- `created_at`: Timestamp of application

---

## 🔧 Database Operations

### User Registration
When a user signs up through the web interface:
1. Email and password are collected
2. Password is hashed using SHA256
3. User data is stored in the `users` table
4. Duplicate emails are prevented by UNIQUE constraint

### Loan Application
When a user submits a loan application:
1. All form data is collected
2. Documents are uploaded to the `uploads/` folder
3. Application is validated based on loan type rules
4. Application data is stored in the `loans` table
5. Status (approved/rejected) is determined and stored

---

## 📈 Current Database Statistics

**Total Users**: 15 registered users
**Total Loan Applications**: 16 applications

### Sample Users in Database:
- kit27.ad05@gmail.com (Demo user - Password: kit@123)
- john.doe@example.com (Password: password123)
- jane.smith@example.com (Password: secure456)
- mike.wilson@example.com (Password: mypass789)
- sarah.jones@example.com (Password: safepass321)
- And 10 more users...

### Loan Statistics:
- ✅ Approved: 7 applications
- ❌ Rejected: 9 applications

### Loan Types:
- Agriculture: 11 applications
- Education: 2 applications
- Home: 2 applications
- Business: 1 application

---

## 🛠️ Database Management Scripts

### 1. `database_manager.py`
Comprehensive database management tool with:
- User creation
- Loan application creation
- Database statistics display
- Query operations

**Usage:**
```bash
python database_manager.py
```

### 2. `add_sample_users.py`
Add sample users to the database for testing.

**Usage:**
```bash
python add_sample_users.py
```

### 3. `check_db.py`
Check database status and verify tables.

**Usage:**
```bash
python check_db.py
```

---

## 🔐 Security Features

1. **Password Hashing**: All passwords are hashed using SHA256 before storage
2. **SQL Injection Prevention**: Using parameterized queries
3. **Unique Email Constraint**: Prevents duplicate user accounts
4. **Session Management**: User sessions are managed securely

---

## 💾 Data Persistence

All user data and loan applications are **permanently stored** in the SQLite database file (`loan_verification.db`). This means:

- ✅ User accounts persist across server restarts
- ✅ Loan applications are permanently saved
- ✅ Login credentials are maintained
- ✅ Application history is preserved
- ✅ No data loss on application restart

---

## 🚀 How to Use

### Through Web Interface:
1. **Sign Up**: Visit `/signup` to create a new account
2. **Login**: Visit `/login` to access your account
3. **Apply for Loan**: Select loan type and fill the form
4. **View Data**: Demo user can view all applications at `/loan_data`

### Through Python Scripts:
```python
from database_manager import DatabaseManager

db = DatabaseManager()

# Create a new user
db.create_user('newuser@example.com', 'password123')

# Get all users
users = db.get_all_users()

# Create loan application
db.create_loan_application(
    email='newuser@example.com',
    loan_type='education',
    amount=300000,
    income=50000,
    liabilities=2,
    status='approved',
    reason='All conditions satisfied',
    documents='admission.pdf,income.pdf'
)
```

---

## ✅ Verification

To verify the database is working:

1. Run the Flask app: `python app.py`
2. Visit: http://127.0.0.1:5000/signup
3. Create a new account
4. Login with your credentials
5. Submit a loan application
6. Run `python database_manager.py` to see your data stored

---

## 📝 Notes

- Database is automatically initialized when `app.py` runs
- All user passwords are securely hashed
- Database file can be backed up by copying `loan_verification.db`
- To reset database, delete `loan_verification.db` and restart the app

---

**Database Status**: ✅ **FULLY OPERATIONAL**
**User Data Storage**: ✅ **WORKING**
**Loan Data Storage**: ✅ **WORKING**
