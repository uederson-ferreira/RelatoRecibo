-- Row Level Security (RLS) Policies
-- RelatoRecibo - Supabase Database
-- Created: 2025-12-08

-- =====================================================
-- ENABLE RLS
-- =====================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.receipts ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- PROFILES POLICIES
-- =====================================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Users can insert their own profile (handled by trigger, but allow explicit inserts)
CREATE POLICY "Users can insert own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- =====================================================
-- REPORTS POLICIES
-- =====================================================

-- Users can view their own reports
CREATE POLICY "Users can view own reports"
    ON public.reports
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can create reports for themselves
CREATE POLICY "Users can create own reports"
    ON public.reports
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own reports
CREATE POLICY "Users can update own reports"
    ON public.reports
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own reports
CREATE POLICY "Users can delete own reports"
    ON public.reports
    FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- RECEIPTS POLICIES
-- =====================================================

-- Users can view receipts from their own reports
CREATE POLICY "Users can view own receipts"
    ON public.receipts
    FOR SELECT
    USING (
        auth.uid() = user_id
        AND
        -- Ensure the receipt belongs to a report owned by the user
        EXISTS (
            SELECT 1
            FROM public.reports
            WHERE reports.id = receipts.report_id
            AND reports.user_id = auth.uid()
        )
    );

-- Users can create receipts for their own reports
CREATE POLICY "Users can create receipts"
    ON public.receipts
    FOR INSERT
    WITH CHECK (
        auth.uid() = user_id
        AND
        -- Ensure the report exists and belongs to the user
        EXISTS (
            SELECT 1
            FROM public.reports
            WHERE reports.id = report_id
            AND reports.user_id = auth.uid()
        )
    );

-- Users can update their own receipts
CREATE POLICY "Users can update own receipts"
    ON public.receipts
    FOR UPDATE
    USING (
        auth.uid() = user_id
        AND
        EXISTS (
            SELECT 1
            FROM public.reports
            WHERE reports.id = receipts.report_id
            AND reports.user_id = auth.uid()
        )
    )
    WITH CHECK (
        auth.uid() = user_id
        AND
        EXISTS (
            SELECT 1
            FROM public.reports
            WHERE reports.id = report_id
            AND reports.user_id = auth.uid()
        )
    );

-- Users can delete their own receipts
CREATE POLICY "Users can delete own receipts"
    ON public.receipts
    FOR DELETE
    USING (
        auth.uid() = user_id
        AND
        EXISTS (
            SELECT 1
            FROM public.reports
            WHERE reports.id = receipts.report_id
            AND reports.user_id = auth.uid()
        )
    );

-- =====================================================
-- HELPER FUNCTIONS FOR COMPLEX POLICIES
-- =====================================================

-- Function to check if user owns a report
CREATE OR REPLACE FUNCTION public.user_owns_report(report_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM public.reports
        WHERE id = report_id
        AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- FUTURE: SHARING POLICIES (Phase 2)
-- =====================================================

-- Uncomment when implementing sharing features:

/*
-- Table for shared reports
CREATE TABLE public.report_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    shared_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    shared_with UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    permission TEXT NOT NULL CHECK (permission IN ('view', 'edit')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(report_id, shared_with)
);

ALTER TABLE public.report_shares ENABLE ROW LEVEL SECURITY;

-- Users can view shares where they are the recipient
CREATE POLICY "Users can view shares"
    ON public.report_shares
    FOR SELECT
    USING (auth.uid() = shared_with OR auth.uid() = shared_by);

-- Only report owners can create shares
CREATE POLICY "Report owners can create shares"
    ON public.report_shares
    FOR INSERT
    WITH CHECK (
        auth.uid() = shared_by
        AND user_owns_report(report_id)
    );

-- Only report owners can delete shares
CREATE POLICY "Report owners can delete shares"
    ON public.report_shares
    FOR DELETE
    USING (auth.uid() = shared_by);

-- Update reports policy to include shared reports
CREATE POLICY "Users can view shared reports"
    ON public.reports
    FOR SELECT
    USING (
        auth.uid() = user_id
        OR
        EXISTS (
            SELECT 1
            FROM public.report_shares
            WHERE report_shares.report_id = reports.id
            AND report_shares.shared_with = auth.uid()
        )
    );

-- Update receipts policy to include shared reports (view only)
CREATE POLICY "Users can view receipts from shared reports"
    ON public.receipts
    FOR SELECT
    USING (
        auth.uid() = user_id
        OR
        EXISTS (
            SELECT 1
            FROM public.report_shares rs
            JOIN public.reports r ON r.id = rs.report_id
            WHERE rs.report_id = receipts.report_id
            AND rs.shared_with = auth.uid()
        )
    );
*/

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant access to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.profiles TO authenticated;
GRANT ALL ON public.reports TO authenticated;
GRANT ALL ON public.receipts TO authenticated;

-- Grant access to service_role (for backend)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON POLICY "Users can view own profile" ON public.profiles IS 'Users can only view their own profile';
COMMENT ON POLICY "Users can view own reports" ON public.reports IS 'Users can only view reports they created';
COMMENT ON POLICY "Users can view own receipts" ON public.receipts IS 'Users can only view receipts from their own reports';
