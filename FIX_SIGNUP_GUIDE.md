# 🔧 Fix Signup Issue - Step by Step Guide

## Problem
Signup is not storing data to Supabase because the Row Level Security (RLS) policies are blocking anonymous inserts.

## Solution
Run the fix SQL files to update the policies.

---

## 📋 Steps to Fix

### Step 1: Run the Fix SQL (2 minutes)

1. **Go to Supabase SQL Editor:**
   ```
   https://bqvudmjhsvaiudwwlxgn.supabase.co
   ```

2. **Click "SQL Editor" → "New Query"**

3. **Copy ALL content from `supabase_fix.sql`**

4. **Paste and click "RUN"**

You should see:
```
✅ DROP POLICY
✅ CREATE POLICY
✅ Success
```

---

### Step 2: Create Storage Bucket (1 minute)

1. **Click "Storage" in left sidebar**

2. **Click "Create a new bucket"**

3. **Enter name:** `loan-documents`

4. **IMPORTANT: Uncheck "Public bucket"** (keep it private)

5. **Click "Create bucket"**

---

### Step 3: Run Storage Fix SQL (1 minute)

1. **Go back to SQL Editor**

2. **Click "New Query"**

3. **Copy ALL content from `storage_fix.sql`**

4. **Paste and click "RUN"**

---

### Step 4: Restart Your App

In terminal:
```bash
# Stop the current app (Ctrl+C)
# Then restart:
python app.py
```

---

### Step 5: Test Signup

1. **Open:** http://127.0.0.1:5000

2. **Click "Sign Up"**

3. **Enter:**
   - Email: test@example.com
   - Password: test123
   - Confirm Password: test123

4. **Click "Sign Up"**

5. **You should see:** "Account created successfully! Please login."

---

## ✅ Verification

### Check if user was created in Supabase:

1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Click "users" table
4. You should see your new user!

---

## 🔍 What Was Wrong?

### Original Problem:
The RLS policies were checking for JWT authentication:
```sql
USING (email = current_setting('request.jwt.claims', true)::json->>'email')
```

But your app uses the **anon key** (not authenticated users), so the policies blocked all inserts.

### The Fix:
Changed policies to allow public access:
```sql
CREATE POLICY "Allow public insert" ON users
    FOR INSERT
    WITH CHECK (true);
```

---

## 📊 Files Created

| File | Purpose |
|------|---------|
| `supabase_fix.sql` | Fix RLS policies for users and loans |
| `storage_fix.sql` | Fix storage bucket policies |
| `FIX_SIGNUP_GUIDE.md` | This guide |

---

## 🎯 Quick Commands

```bash
# 1. Go to Supabase
https://bqvudmjhsvaiudwwlxgn.supabase.co

# 2. SQL Editor → Run supabase_fix.sql

# 3. Create bucket: loan-documents

# 4. SQL Editor → Run storage_fix.sql

# 5. Restart app
python app.py

# 6. Test signup
http://127.0.0.1:5000/signup
```

---

## ⚠️ Important Notes

### Security Consideration:
The current setup allows **public access** to make signup work easily. For production, you should:

1. Implement proper authentication (Supabase Auth)
2. Add stricter RLS policies
3. Validate user permissions

### For Development:
The current setup is **perfect for testing and development**. It allows:
- ✅ Anyone can signup
- ✅ Anyone can login
- ✅ Anyone can submit loans
- ✅ Anyone can upload files

---

## 🆘 Troubleshooting

### Issue: "Error creating account"
**Solution:** Run `supabase_fix.sql` in Supabase SQL Editor

### Issue: "Storage bucket not found"
**Solution:** 
1. Create bucket `loan-documents` in Storage
2. Run `storage_fix.sql`

### Issue: Still not working
**Check:**
1. Is your app running? (`python app.py`)
2. Is `.env` file configured correctly?
3. Did you run both SQL fix files?
4. Check browser console for errors (F12)

---

## 📞 Need More Help?

If signup still doesn't work after following these steps:

1. Check the terminal output for error messages
2. Check Supabase logs in the dashboard
3. Verify the `.env` file has correct credentials
4. Make sure both SQL fix files were executed successfully

---

## ✅ Success Checklist

- [ ] Ran `supabase_fix.sql` in Supabase SQL Editor
- [ ] Created storage bucket `loan-documents`
- [ ] Ran `storage_fix.sql` in Supabase SQL Editor
- [ ] Restarted the app (`python app.py`)
- [ ] Tested signup with a new email
- [ ] Verified user appears in Supabase users table
- [ ] Tested login with new account
- [ ] Tested loan application submission

---

**Once all steps are complete, your signup should work perfectly!** 🎉
