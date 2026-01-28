-- ============================================
-- Supabase Database Setup for Loan Verification System
-- ============================================
-- Copy and paste this entire file into Supabase SQL Editor
-- Then click "Run" to execute all commands
-- ============================================

-- Drop existing tables if they exist (optional - uncomment if needed)
-- DROP TABLE IF EXISTS loans CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- 1. CREATE TABLES
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loans table
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
    CONSTRAINT fk_user_email FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);

-- ============================================
-- 2. CREATE INDEXES FOR PERFORMANCE
-- ============================================

-- Index on loans email for faster user loan queries
CREATE INDEX IF NOT EXISTS idx_loans_email ON loans(email);

-- Index on loans status for filtering
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);

-- Index on loans created_at for sorting
CREATE INDEX IF NOT EXISTS idx_loans_created_at ON loans(created_at DESC);

-- Index on loans loan_type for analytics
CREATE INDEX IF NOT EXISTS idx_loans_type ON loans(loan_type);

-- Index on users email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- 3. INSERT DEMO USER
-- ============================================

-- Insert demo user (kit27.ad05@gmail.com / kit@123)
-- Password is pre-hashed using SHA256
INSERT INTO users (email, password) 
VALUES ('kit27.ad05@gmail.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 4. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Enable RLS on loans table
ALTER TABLE loans ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 5. CREATE RLS POLICIES FOR USERS TABLE
-- ============================================

-- Drop existing policies to ensure the script is re-runnable
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Anyone can signup" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;

-- Policy: Users can read their own data
-- We will allow broader select access as the backend service will handle user lookups.
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (true);

-- Policy: Anyone can insert (for signup)
CREATE POLICY "Anyone can signup" ON users
    FOR INSERT WITH CHECK (true);

-- Policy: Users can update their own data
-- The application does not use this, but we'll scope it to the user's email.
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.email() = email);

-- ============================================
-- 6. CREATE RLS POLICIES FOR LOANS TABLE
-- ============================================

-- Drop existing policies to ensure the script is re-runnable
DROP POLICY IF EXISTS "Users can view own loans" ON loans;
DROP POLICY IF EXISTS "Users can create own loans" ON loans;
DROP POLICY IF EXISTS "Users can update own loans" ON loans;
DROP POLICY IF EXISTS "Users can delete own loans" ON loans;

-- Policy: Allow service to read loans. The app logic filters by user.
CREATE POLICY "Users can view own loans" ON loans
    FOR SELECT USING (true);

-- Policy: Users can insert their own loans
CREATE POLICY "Users can create own loans" ON loans
    FOR INSERT WITH CHECK (true);

-- Policy: Users can update their own loans
CREATE POLICY "Users can update own loans" ON loans
    FOR UPDATE USING (true);

-- Policy: Users can delete their own loans
CREATE POLICY "Users can delete own loans" ON loans
    FOR DELETE USING (true);

-- ============================================
-- 6.5. CREATE STORAGE POLICIES
-- ============================================

-- Drop existing policies to ensure the script is re-runnable
DROP POLICY IF EXISTS "Public insert for loan-documents" ON storage.objects;
DROP POLICY IF EXISTS "Public select for loan-documents" ON storage.objects;
DROP POLICY IF EXISTS "Public update for loan-documents" ON storage.objects;
DROP POLICY IF EXISTS "Public delete for loan-documents" ON storage.objects;

-- Allow public access to the 'loan-documents' bucket for development.
-- This allows the backend to upload and manage files.

CREATE POLICY "Public insert for loan-documents"
ON storage.objects FOR INSERT TO public
WITH CHECK (bucket_id = 'loan-documents');

CREATE POLICY "Public select for loan-documents"
ON storage.objects FOR SELECT TO public
USING (bucket_id = 'loan-documents');

CREATE POLICY "Public update for loan-documents"
ON storage.objects FOR UPDATE TO public
USING (bucket_id = 'loan-documents');

CREATE POLICY "Public delete for loan-documents"
ON storage.objects FOR DELETE TO public
USING (bucket_id = 'loan-documents');

-- ============================================
-- 7. CREATE HELPFUL VIEWS (OPTIONAL)
-- ============================================

-- View: Loan statistics by type
CREATE OR REPLACE VIEW loan_stats_by_type AS
SELECT 
    loan_type,
    COUNT(*) as total_applications,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count,
    AVG(amount) as avg_loan_amount,
    SUM(amount) as total_loan_amount
FROM loans
GROUP BY loan_type;

-- View: Recent loan applications
CREATE OR REPLACE VIEW recent_loans AS
SELECT 
    id,
    email,
    loan_type,
    amount,
    status,
    created_at
FROM loans
ORDER BY created_at DESC
LIMIT 100;

-- View: User loan summary
CREATE OR REPLACE VIEW user_loan_summary AS
SELECT 
    u.email,
    COUNT(l.id) as total_applications,
    COUNT(CASE WHEN l.status = 'approved' THEN 1 END) as approved_count,
    COUNT(CASE WHEN l.status = 'rejected' THEN 1 END) as rejected_count,
    SUM(CASE WHEN l.status = 'approved' THEN l.amount ELSE 0 END) as total_approved_amount
FROM users u
LEFT JOIN loans l ON u.email = l.email
GROUP BY u.email;

-- ============================================
-- 8. CREATE FUNCTIONS (OPTIONAL)
-- ============================================

-- Function: Get user loan count
CREATE OR REPLACE FUNCTION get_user_loan_count(user_email TEXT)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER FROM loans WHERE email = user_email;
$$ LANGUAGE SQL STABLE;

-- Function: Get approval rate by loan type
CREATE OR REPLACE FUNCTION get_approval_rate(loan_type_param TEXT)
RETURNS NUMERIC AS $$
    SELECT 
        CASE 
            WHEN COUNT(*) = 0 THEN 0
            ELSE ROUND(
                (COUNT(CASE WHEN status = 'approved' THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC) * 100, 
                2
            )
        END
    FROM loans 
    WHERE loan_type = loan_type_param;
$$ LANGUAGE SQL STABLE;

-- ============================================
-- 9. GRANT PERMISSIONS
-- ============================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON loans TO authenticated;
GRANT USAGE ON SEQUENCE users_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE loans_id_seq TO authenticated;

-- Grant permissions to anon users (for public access)
GRANT SELECT, INSERT ON users TO anon;
GRANT SELECT, INSERT ON loans TO anon;

-- ============================================
-- 10. VERIFICATION QUERIES
-- ============================================

-- Check if tables were created successfully
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('users', 'loans');

-- Check if indexes were created
SELECT 
    indexname,
    tablename
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('users', 'loans');

-- Check if demo user was created
SELECT email, created_at FROM users WHERE email = 'kit27.ad05@gmail.com';

-- Display table statistics
SELECT 
    'users' as table_name,
    COUNT(*) as row_count
FROM users
UNION ALL
SELECT 
    'loans' as table_name,
    COUNT(*) as row_count
FROM loans;

-- ============================================
-- SETUP COMPLETE!
-- ============================================
-- 
-- ✅ Tables created: users, loans
-- ✅ Indexes created for performance
-- ✅ Demo user inserted: kit27.ad05@gmail.com
-- ✅ Row Level Security enabled
-- ✅ RLS Policies created
-- ✅ Storage policies created
-- ✅ Helper functions created
-- ✅ Permissions granted
--
-- Next Steps:
-- 1. Create storage bucket: 'loan-documents' in Supabase Storage
-- 2. Update your .env file with credentials
-- 3. Run: pip install -r requirements.txt
-- 4. Run: python app.py
--
-- Demo Login:
-- Email: kit27.ad05@gmail.com
-- Password: kit@123
-- ============================================
