# How to View Submitted Loan Details

## 📋 Overview
There are **3 ways** to view submitted loan application details in your system:

---

## ✅ Method 1: Through Web Interface (Recommended)

### For Regular Users:
1. **Login** to your account at http://127.0.0.1:5000/login
2. Click on **"My Applications"** in the navigation bar
3. You will see all YOUR loan applications with:
   - Loan ID
   - Loan Type (Agriculture, Home, Education, Business)
   - Amount requested
   - Income
   - Number of liabilities
   - Status (Approved/Rejected)
   - Reason for approval/rejection
   - Uploaded documents count
   - Application date

### For Demo User (kit27.ad05@gmail.com):
1. **Login** with: kit27.ad05@gmail.com / kit@123
2. Click on **"View All Data"** in the navigation bar
3. You will see **ALL** loan applications from all users
4. Additional statistics displayed:
   - Total approved/rejected applications
   - Total loan amount
   - Average loan amount
   - Breakdown by loan type

### Direct URL:
- Navigate to: **http://127.0.0.1:5000/loan_data**

---

## ✅ Method 2: Using Python Scripts

### Option A: View Database Script
```bash
python view_database.py
```

**Shows:**
- Complete list of all users
- All loan applications with details
- Summary statistics
- Loan type breakdown
- Total approved amount

### Option B: Database Manager Script
```bash
python database_manager.py
```

**Shows:**
- All registered users
- All loan applications
- Detailed statistics
- Approval/rejection breakdown

---

## ✅ Method 3: Direct Database Query

### Using SQLite Command Line:
```bash
sqlite3 loan_verification.db
```

Then run queries:
```sql
-- View all loans
SELECT * FROM loans ORDER BY created_at DESC;

-- View loans for specific user
SELECT * FROM loans WHERE email = 'user@example.com';

-- View only approved loans
SELECT * FROM loans WHERE status = 'approved';

-- Count loans by type
SELECT loan_type, COUNT(*) FROM loans GROUP BY loan_type;
```

### Using Python:
```python
import sqlite3

conn = sqlite3.connect('loan_verification.db')
cursor = conn.cursor()

# Get all loans
cursor.execute('SELECT * FROM loans')
loans = cursor.fetchall()

for loan in loans:
    print(loan)

conn.close()
```

---

## 📊 What Information is Displayed?

Each loan application shows:

| Field | Description |
|-------|-------------|
| **ID** | Unique loan application ID |
| **Email** | User's email address |
| **Loan Type** | Agriculture, Home, Education, or Business |
| **Amount** | Requested loan amount in ₹ |
| **Income** | Monthly income in ₹ |
| **Liabilities** | Number of existing loans |
| **Status** | Approved or Rejected |
| **Reason** | Reason for approval/rejection |
| **Documents** | List of uploaded document filenames |
| **Date** | Application submission timestamp |

---

## 🎯 Quick Access Steps

### To View Your Own Applications:
1. Login → Click "My Applications" → View your loans

### To View All Applications (Demo User Only):
1. Login as kit27.ad05@gmail.com → Click "View All Data" → View all loans

### To View via Terminal:
1. Open terminal in project folder
2. Run: `python view_database.py`
3. See complete database contents

---

## 💡 Tips

- **Regular users** can only see their own loan applications
- **Demo user** (kit27.ad05@gmail.com) can see ALL applications
- Applications are sorted by **newest first**
- **Color coding**:
  - 🟢 Green = Approved
  - 🔴 Red = Rejected
  - 🟡 Yellow = Warning (high liabilities)
- Click on document count to see filenames

---

## 🔍 Example Queries

### Check if your loan was approved:
1. Login to web interface
2. Go to "My Applications"
3. Look at the **Status** column

### See total approved amount:
1. Login as demo user
2. Go to "View All Data"
3. Check the **Total Amount** card

### Export loan data:
```bash
python view_database.py > loan_report.txt
```

---

## ✅ Current Database Status

- **Total Users**: 15
- **Total Applications**: 16
- **Approved**: 8
- **Rejected**: 8
- **Total Approved Amount**: ₹4,950,000

---

## 🚀 Quick Commands

```bash
# View all data
python view_database.py

# View with management options
python database_manager.py

# Check database status
python check_db.py

# Start web application
python app.py
# Then visit: http://127.0.0.1:5000/loan_data
```

---

**Your loan data is safely stored in `loan_verification.db` and can be viewed anytime!** ✅
