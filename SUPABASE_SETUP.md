# Supabase Setup Guide for Loan Verification System

This guide will help you migrate your loan verification system from SQLite + local storage to Supabase.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Python 3.7 or higher
- pip package manager

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in the project details:
   - **Name**: loan-verification (or any name you prefer)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to your users
4. Click "Create new project" and wait for it to initialize (takes ~2 minutes)

## Step 2: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (this is your API key)

## Step 3: Create Database Tables

1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy and paste the following SQL:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create loans table
CREATE TABLE IF NOT EXISTS loans (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    income INTEGER NOT NULL,
    liabilities INTEGER NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    documents TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (email) REFERENCES users(email)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_loans_email ON loans(email);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_loans_created_at ON loans(created_at DESC);
```

4. Click "Run" to execute the SQL

## Step 4: Create Storage Bucket

1. In your Supabase dashboard, go to **Storage**
2. Click "Create a new bucket"
3. Enter bucket name: `loan-documents`
4. **Important**: Uncheck "Public bucket" (keep it private for security)
5. Click "Create bucket"

### Set Storage Policies (Important for Security)

1. Click on the `loan-documents` bucket
2. Go to **Policies** tab
3. Click "New Policy"
4. Create the following policies:

**Policy 1: Allow authenticated users to upload**
```sql
-- Policy name: Allow authenticated uploads
-- Operation: INSERT
-- Policy definition:
true
```

**Policy 2: Allow users to read their own files**
```sql
-- Policy name: Allow users to read own files
-- Operation: SELECT
-- Policy definition:
(storage.foldername(name))[1] = auth.jwt() ->> 'email'::text
```

**Policy 3: Allow users to delete their own files**
```sql
-- Policy name: Allow users to delete own files
-- Operation: DELETE
-- Policy definition:
(storage.foldername(name))[1] = auth.jwt() ->> 'email'::text
```

## Step 5: Configure Your Local Environment

1. Create a `.env` file in your project root:

```bash
# In your project folder
cd "c:\Users\Acer\OneDrive\Documents\New folder\indian"
```

2. Copy the `.env.example` file:

```bash
copy .env.example .env
```

3. Edit the `.env` file and add your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this

# Storage Configuration
SUPABASE_BUCKET_NAME=loan-documents
```

**Important**: Replace the placeholder values with your actual credentials!

## Step 6: Install Dependencies

```bash
# Make sure you're in your project directory
cd "c:\Users\Acer\OneDrive\Documents\New folder\indian"

# Activate your virtual environment (if using one)
venv\Scripts\activate

# Install the new dependencies
pip install -r requirements.txt
```

## Step 7: Test the Setup

1. Run the Supabase manager test:

```bash
python supabase_manager.py
```

You should see:
- ✅ Supabase client initialized successfully
- ✅ Storage bucket 'loan-documents' already exists
- Database statistics

2. If you see errors, check:
   - Your `.env` file has correct credentials
   - Your Supabase project is active
   - Database tables are created
   - Storage bucket exists

## Step 8: Run the Application

```bash
python app.py
```

The application should start successfully. You can now:
- Sign up new users
- Login with demo account: `kit27.ad05@gmail.com` / `kit@123`
- Submit loan applications
- Files will be uploaded to Supabase Storage
- Data will be stored in Supabase Database

## Migrating Existing Data (Optional)

If you have existing data in SQLite that you want to migrate:

1. Export data from SQLite:
```python
import sqlite3
import json

conn = sqlite3.connect('loan_verification.db')
cursor = conn.cursor()

# Export users
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
with open('users_export.json', 'w') as f:
    json.dump(users, f)

# Export loans
cursor.execute('SELECT * FROM loans')
loans = cursor.fetchall()
with open('loans_export.json', 'w') as f:
    json.dump(loans, f)

conn.close()
```

2. Import into Supabase using the SQL Editor or write a migration script

## Troubleshooting

### Error: "Supabase credentials not found"
- Check that your `.env` file exists in the project root
- Verify the credentials are correct (no extra spaces)
- Make sure you're using the **anon/public** key, not the service role key

### Error: "relation 'users' does not exist"
- Go to Supabase SQL Editor and run the table creation SQL again
- Check that the tables were created successfully in the Table Editor

### Error: "Storage bucket not found"
- Go to Supabase Storage and verify the bucket name is `loan-documents`
- Check that the bucket name in `.env` matches exactly

### Files not uploading
- Check storage policies are set correctly
- Verify the bucket is created
- Check file size limits (default is 50MB)

### Cannot login with demo user
- Run `python app.py` once to create the demo user
- Or manually insert the demo user in Supabase SQL Editor:
```sql
INSERT INTO users (email, password) 
VALUES ('kit27.ad05@gmail.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3');
```

## Security Best Practices

1. **Never commit your `.env` file** - Add it to `.gitignore`
2. **Use Row Level Security (RLS)** - Enable RLS on your tables in Supabase
3. **Rotate your keys regularly** - Generate new API keys periodically
4. **Use environment-specific credentials** - Different keys for dev/prod
5. **Monitor usage** - Check Supabase dashboard for unusual activity

## Benefits of Supabase

✅ **Scalability**: Handles millions of rows without performance issues
✅ **Real-time**: Built-in real-time subscriptions (can be added later)
✅ **Security**: Row Level Security and built-in authentication
✅ **Storage**: Unlimited file storage with CDN
✅ **Backup**: Automatic daily backups
✅ **Free Tier**: Generous free tier for development and small apps

## Next Steps

- Enable Row Level Security (RLS) on your tables
- Add email verification for new users
- Implement file size and type validation
- Add real-time notifications for loan status updates
- Set up automatic backups

## Support

- Supabase Documentation: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Project Issues: Create an issue in your repository

---

**Note**: Keep your Supabase credentials secure and never share them publicly!
