-- Supabase Storage Policies
-- RelatoRecibo - Storage Bucket Configuration
-- Created: 2025-12-08

-- =====================================================
-- STORAGE BUCKETS
-- =====================================================

-- This file contains the SQL commands to set up storage buckets and policies
-- Run these in Supabase SQL Editor OR use Supabase Dashboard UI

-- NOTE: Bucket creation is typically done via Supabase Dashboard or API
-- If using SQL, use the storage.buckets table directly:

/*
-- Create receipts bucket (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'receipts',
    'receipts',
    false, -- private bucket
    5242880, -- 5MB max file size
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
);
*/

-- Alternatively, use Supabase Dashboard:
-- 1. Go to Storage section
-- 2. Create new bucket named "receipts"
-- 3. Set as PRIVATE
-- 4. Configure file size limit: 5MB
-- 5. Allowed MIME types: image/jpeg, image/jpg, image/png, image/webp

-- =====================================================
-- STORAGE POLICIES FOR 'receipts' BUCKET
-- =====================================================

-- Policy 1: Users can upload files to their own folder
CREATE POLICY "Users can upload receipts to own folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'receipts'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 2: Users can view/download their own files
CREATE POLICY "Users can view own receipts"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'receipts'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 3: Users can update their own files
CREATE POLICY "Users can update own receipts"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id = 'receipts'
    AND (storage.foldername(name))[1] = auth.uid()::text
)
WITH CHECK (
    bucket_id = 'receipts'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 4: Users can delete their own files
CREATE POLICY "Users can delete own receipts"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'receipts'
    AND (storage.foldername(name))[1] = auth.uid()::text
);

-- =====================================================
-- SERVICE ROLE POLICIES (Backend API)
-- =====================================================

-- Service role has full access (for backend operations)
-- This is enabled by default in Supabase when using service_role key

-- The backend will use service_role to:
-- 1. Upload files on behalf of authenticated users
-- 2. Generate signed URLs for private files
-- 3. Delete files when receipts/reports are deleted

-- =====================================================
-- STORAGE PATH STRUCTURE
-- =====================================================

-- Files will be organized as:
-- receipts/
--   └── {user_id}/
--       └── {report_id}/
--           └── {receipt_id}_{timestamp}.{ext}
--
-- Example:
-- receipts/123e4567-e89b-12d3-a456-426614174000/456e7890-e89b-12d3-a456-426614174111/789abc12_1702234567890.jpg

-- This structure ensures:
-- 1. User isolation (RLS enforced)
-- 2. Easy cleanup when deleting reports
-- 3. Unique filenames (receipt_id + timestamp)
-- 4. No naming conflicts

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to generate storage path
CREATE OR REPLACE FUNCTION public.generate_receipt_storage_path(
    p_user_id UUID,
    p_report_id UUID,
    p_receipt_id UUID,
    p_extension TEXT
)
RETURNS TEXT AS $$
BEGIN
    RETURN format(
        '%s/%s/%s_%s.%s',
        p_user_id::text,
        p_report_id::text,
        p_receipt_id::text,
        extract(epoch from now())::bigint,
        p_extension
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get public URL for receipt image
CREATE OR REPLACE FUNCTION public.get_receipt_image_url(p_image_path TEXT)
RETURNS TEXT AS $$
DECLARE
    v_bucket_id TEXT := 'receipts';
    v_project_url TEXT;
BEGIN
    -- Get Supabase project URL from environment or config
    -- This should be set in your Supabase project settings
    v_project_url := current_setting('app.settings.supabase_url', true);

    IF v_project_url IS NULL THEN
        -- Fallback: construct URL (replace with your actual project URL)
        RETURN format(
            'https://your-project-ref.supabase.co/storage/v1/object/public/%s/%s',
            v_bucket_id,
            p_image_path
        );
    END IF;

    RETURN format(
        '%s/storage/v1/object/public/%s/%s',
        v_project_url,
        v_bucket_id,
        p_image_path
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CLEANUP TRIGGER
-- =====================================================

-- Automatically delete storage files when receipt is deleted
CREATE OR REPLACE FUNCTION public.delete_receipt_storage()
RETURNS TRIGGER AS $$
DECLARE
    v_response TEXT;
BEGIN
    -- Delete file from storage using storage.fdelete
    -- This requires the pg_net extension
    IF OLD.image_path IS NOT NULL THEN
        PERFORM storage.fdelete('receipts', OLD.image_path);
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_receipt_deleted
    BEFORE DELETE ON public.receipts
    FOR EACH ROW
    EXECUTE FUNCTION public.delete_receipt_storage();

-- =====================================================
-- FUTURE: THUMBNAILS BUCKET (Optional)
-- =====================================================

-- If you want to store optimized thumbnails separately:
/*
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'thumbnails',
    'thumbnails',
    true, -- public bucket for faster loading
    1048576, -- 1MB max
    ARRAY['image/jpeg', 'image/webp']
);

-- Public access for thumbnails
CREATE POLICY "Anyone can view thumbnails"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'thumbnails');

-- Only authenticated users can upload
CREATE POLICY "Users can upload thumbnails to own folder"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'thumbnails'
    AND (storage.foldername(name))[1] = auth.uid()::text
);
*/

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON POLICY "Users can upload receipts to own folder" ON storage.objects IS 'Users can only upload files to folders named with their user_id';
COMMENT ON POLICY "Users can view own receipts" ON storage.objects IS 'Users can only view/download files from their own folder';
