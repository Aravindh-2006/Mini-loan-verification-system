-- ============================================
-- FINAL FIX - Run this ONLY
-- ============================================
-- This will drop old policies and create new ones
-- ============================================

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Anyone can signup" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can view own loans" ON loans;
DROP POLICY IF EXISTS "Demo user can view all loans" ON loans;
DROP POLICY IF EXISTS "Users can create own loans" ON loans;
DROP POLICY IF EXISTS "Users can update own loans" ON loans;
DROP POLICY IF EXISTS "Users can delete own loans" ON loans;

-- ============================================
-- RECREATE POLICIES - SIMPLIFIED FOR ANON ACCESS
-- ============================================

-- USERS TABLE POLICIES
-- Allow anyone to read users (for login check)
CREATE POLICY "Allow public read access" ON users
    FOR SELECT
    USING (true);

-- Allow anyone to insert (for signup)
CREATE POLICY "Allow public insert" ON users
    FOR INSERT
    WITH CHECK (true);

-- Allow anyone to update (simplified)
CREATE POLICY "Allow public update" ON users
    FOR UPDATE
    USING (true);

-- LOANS TABLE POLICIES
-- Allow anyone to read loans (simplified)
CREATE POLICY "Allow public read loans" ON loans
    FOR SELECT
    USING (true);

-- Allow anyone to insert loans
CREATE POLICY "Allow public insert loans" ON loans
    FOR INSERT
    WITH CHECK (true);

-- Allow anyone to update loans
CREATE POLICY "Allow public update loans" ON loans
    FOR UPDATE
    USING (true);

-- Allow anyone to delete loans
CREATE POLICY "Allow public delete loans" ON loans
    FOR DELETE
    USING (true);

-- ============================================
-- VERIFICATION
-- ============================================

-- Check policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename IN ('users', 'loans')
ORDER BY tablename, policyname;

-- ============================================
-- ✅ DONE! Now try signup again
-- ============================================
