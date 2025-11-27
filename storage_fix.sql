-- ============================================
-- FIX: Storage bucket policies
-- ============================================
-- Run this in Supabase SQL Editor after creating the bucket
-- ============================================

-- Note: First create the bucket 'loan-documents' in Storage UI
-- Then run these policies

-- Allow anyone to upload files
CREATE POLICY "Allow public uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'loan-documents');

-- Allow anyone to read files
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'loan-documents');

-- Allow anyone to update files
CREATE POLICY "Allow public updates"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'loan-documents');

-- Allow anyone to delete files
CREATE POLICY "Allow public deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'loan-documents');

-- ============================================
-- VERIFICATION
-- ============================================

-- Check storage policies
SELECT *
FROM pg_policies
WHERE schemaname = 'storage'
AND tablename = 'objects';

-- ============================================
-- DONE! Storage should work now
-- ============================================
