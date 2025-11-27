# Quick Start Guide - Supabase Migration

## 🚀 Quick Setup (5 Minutes)

### 1. Create Supabase Project
- Go to https://supabase.com
- Create new project
- Copy your **Project URL** and **anon key**

### 2. Setup Database
In Supabase SQL Editor, run:

```sql
-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loans table
CREATE TABLE loans (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    income INTEGER NOT NULL,
    liabilities INTEGER NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    documents TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_loans_email ON loans(email);
CREATE INDEX idx_loans_status ON loans(status);
```

### 3. Create Storage Bucket
- Go to **Storage** in Supabase
- Create bucket: `loan-documents`
- Keep it **private** (unchecked public)

### 4. Configure Environment
Create `.env` file:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=change-this-secret-key
SUPABASE_BUCKET_NAME=loan-documents
```

### 5. Install & Run

```bash
pip install -r requirements.txt
python app.py
```

### 6. Test Login
- **Email**: kit27.ad05@gmail.com
- **Password**: kit@123

## ✅ Done!

Your app is now using Supabase for:
- ✅ Database (PostgreSQL)
- ✅ File Storage (Cloud Storage)
- ✅ Scalable infrastructure

## 📚 Full Documentation
See `SUPABASE_SETUP.md` for detailed instructions.

## 🔧 Troubleshooting

**Error: Credentials not found**
→ Check your `.env` file exists and has correct values

**Error: Table doesn't exist**
→ Run the SQL commands in Supabase SQL Editor

**Files not uploading**
→ Verify storage bucket name is `loan-documents`
