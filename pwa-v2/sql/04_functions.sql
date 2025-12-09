-- Database Functions and Stored Procedures
-- RelatoRecibo - Supabase Database
-- Created: 2025-12-08

-- =====================================================
-- ANALYTICS & STATISTICS FUNCTIONS
-- =====================================================

-- Get user statistics
CREATE OR REPLACE FUNCTION public.get_user_statistics(p_user_id UUID)
RETURNS TABLE (
    total_reports BIGINT,
    total_receipts BIGINT,
    total_value DECIMAL(12, 2),
    draft_reports BIGINT,
    completed_reports BIGINT,
    avg_receipts_per_report DECIMAL(10, 2),
    avg_value_per_receipt DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT r.id)::BIGINT AS total_reports,
        COUNT(DISTINCT rc.id)::BIGINT AS total_receipts,
        COALESCE(SUM(rc.value), 0)::DECIMAL(12, 2) AS total_value,
        COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'draft')::BIGINT AS draft_reports,
        COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'completed')::BIGINT AS completed_reports,
        CASE
            WHEN COUNT(DISTINCT r.id) > 0 THEN
                (COUNT(DISTINCT rc.id)::DECIMAL / COUNT(DISTINCT r.id)::DECIMAL)
            ELSE 0
        END AS avg_receipts_per_report,
        CASE
            WHEN COUNT(DISTINCT rc.id) > 0 THEN
                (COALESCE(SUM(rc.value), 0) / COUNT(DISTINCT rc.id))::DECIMAL(12, 2)
            ELSE 0
        END AS avg_value_per_receipt
    FROM public.reports r
    LEFT JOIN public.receipts rc ON r.id = rc.report_id
    WHERE r.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get report summary with receipt details
CREATE OR REPLACE FUNCTION public.get_report_summary(p_report_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    target_value DECIMAL(12, 2),
    total_value DECIMAL(12, 2),
    receipts_count INTEGER,
    status report_status,
    progress_percentage DECIMAL(5, 2),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    earliest_receipt_date DATE,
    latest_receipt_date DATE,
    avg_receipt_value DECIMAL(12, 2),
    min_receipt_value DECIMAL(12, 2),
    max_receipt_value DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        r.description,
        r.target_value,
        r.total_value,
        r.receipts_count,
        r.status,
        CASE
            WHEN r.target_value > 0 THEN
                ROUND((r.total_value / r.target_value * 100)::NUMERIC, 2)
            ELSE NULL
        END AS progress_percentage,
        r.created_at,
        r.updated_at,
        r.completed_at,
        MIN(rc.date) AS earliest_receipt_date,
        MAX(rc.date) AS latest_receipt_date,
        ROUND(AVG(rc.value)::NUMERIC, 2) AS avg_receipt_value,
        MIN(rc.value) AS min_receipt_value,
        MAX(rc.value) AS max_receipt_value
    FROM public.reports r
    LEFT JOIN public.receipts rc ON r.id = rc.report_id
    WHERE r.id = p_report_id
    GROUP BY r.id, r.name, r.description, r.target_value, r.total_value,
             r.receipts_count, r.status, r.created_at, r.updated_at, r.completed_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get receipts grouped by date (for charts/reports)
CREATE OR REPLACE FUNCTION public.get_receipts_by_date(
    p_report_id UUID,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    date DATE,
    count BIGINT,
    total_value DECIMAL(12, 2),
    avg_value DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.date,
        COUNT(*)::BIGINT AS count,
        SUM(rc.value)::DECIMAL(12, 2) AS total_value,
        ROUND(AVG(rc.value)::NUMERIC, 2) AS avg_value
    FROM public.receipts rc
    WHERE rc.report_id = p_report_id
        AND (p_start_date IS NULL OR rc.date >= p_start_date)
        AND (p_end_date IS NULL OR rc.date <= p_end_date)
    GROUP BY rc.date
    ORDER BY rc.date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- BATCH OPERATIONS
-- =====================================================

-- Bulk delete receipts by IDs
CREATE OR REPLACE FUNCTION public.bulk_delete_receipts(p_receipt_ids UUID[])
RETURNS TABLE (deleted_count INTEGER) AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    -- Delete receipts (triggers will handle storage cleanup and report updates)
    DELETE FROM public.receipts
    WHERE id = ANY(p_receipt_ids)
        AND user_id = auth.uid(); -- Security: only delete own receipts

    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;

    RETURN QUERY SELECT v_deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Duplicate a report (without receipts)
CREATE OR REPLACE FUNCTION public.duplicate_report(p_report_id UUID)
RETURNS UUID AS $$
DECLARE
    v_new_report_id UUID;
    v_report RECORD;
BEGIN
    -- Get original report
    SELECT * INTO v_report
    FROM public.reports
    WHERE id = p_report_id
        AND user_id = auth.uid(); -- Security check

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Report not found or access denied';
    END IF;

    -- Create new report
    INSERT INTO public.reports (
        user_id,
        name,
        description,
        target_value,
        status
    ) VALUES (
        auth.uid(),
        v_report.name || ' (Cópia)',
        v_report.description,
        v_report.target_value,
        'draft'
    )
    RETURNING id INTO v_new_report_id;

    RETURN v_new_report_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Archive old reports (soft delete)
CREATE OR REPLACE FUNCTION public.archive_old_reports(p_days_old INTEGER DEFAULT 90)
RETURNS TABLE (archived_count INTEGER) AS $$
DECLARE
    v_archived_count INTEGER;
BEGIN
    UPDATE public.reports
    SET status = 'archived'
    WHERE user_id = auth.uid()
        AND status = 'completed'
        AND completed_at < NOW() - INTERVAL '1 day' * p_days_old;

    GET DIAGNOSTICS v_archived_count = ROW_COUNT;

    RETURN QUERY SELECT v_archived_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- SEARCH FUNCTIONS
-- =====================================================

-- Search reports by name or description
CREATE OR REPLACE FUNCTION public.search_reports(
    p_search_term TEXT,
    p_status report_status DEFAULT NULL,
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    total_value DECIMAL(12, 2),
    receipts_count INTEGER,
    status report_status,
    created_at TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        r.description,
        r.total_value,
        r.receipts_count,
        r.status,
        r.created_at,
        ts_rank(
            to_tsvector('portuguese', COALESCE(r.name, '') || ' ' || COALESCE(r.description, '')),
            plainto_tsquery('portuguese', p_search_term)
        ) AS rank
    FROM public.reports r
    WHERE r.user_id = auth.uid()
        AND (p_status IS NULL OR r.status = p_status)
        AND (
            to_tsvector('portuguese', COALESCE(r.name, '') || ' ' || COALESCE(r.description, ''))
            @@ plainto_tsquery('portuguese', p_search_term)
        )
    ORDER BY rank DESC, r.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- VALIDATION FUNCTIONS
-- =====================================================

-- Validate if user can add more receipts (optional quota system)
CREATE OR REPLACE FUNCTION public.can_add_receipt(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_receipt_count INTEGER;
    v_max_receipts INTEGER := 1000; -- Configurable limit
BEGIN
    SELECT COUNT(*)
    INTO v_receipt_count
    FROM public.receipts
    WHERE user_id = p_user_id;

    RETURN v_receipt_count < v_max_receipts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if report can be marked as completed
CREATE OR REPLACE FUNCTION public.can_complete_report(p_report_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_receipts_count INTEGER;
BEGIN
    SELECT receipts_count
    INTO v_receipts_count
    FROM public.reports
    WHERE id = p_report_id;

    -- A report can be completed if it has at least one receipt
    RETURN v_receipts_count > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Format currency for Brazilian Real
CREATE OR REPLACE FUNCTION public.format_currency(p_value DECIMAL)
RETURNS TEXT AS $$
BEGIN
    RETURN 'R$ ' || TO_CHAR(p_value, 'FM999G999G999D00');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Calculate days until target (if applicable)
CREATE OR REPLACE FUNCTION public.days_since_report_created(p_report_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_created_at TIMESTAMPTZ;
BEGIN
    SELECT created_at
    INTO v_created_at
    FROM public.reports
    WHERE id = p_report_id;

    RETURN EXTRACT(DAY FROM NOW() - v_created_at)::INTEGER;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- INDEXES FOR FULL-TEXT SEARCH
-- =====================================================

-- Create GIN index for full-text search on reports
CREATE INDEX IF NOT EXISTS idx_reports_fts
ON public.reports
USING GIN (to_tsvector('portuguese', COALESCE(name, '') || ' ' || COALESCE(description, '')));

-- Create GIN index for full-text search on receipts
CREATE INDEX IF NOT EXISTS idx_receipts_fts
ON public.receipts
USING GIN (to_tsvector('portuguese', COALESCE(description, '') || ' ' || COALESCE(notes, '') || ' ' || COALESCE(ocr_text, '')));

-- =====================================================
-- MAINTENANCE FUNCTIONS
-- =====================================================

-- Clean up orphaned receipts (should not happen with CASCADE, but safety check)
CREATE OR REPLACE FUNCTION public.cleanup_orphaned_receipts()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM public.receipts
    WHERE report_id NOT IN (SELECT id FROM public.reports);

    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;

    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recalculate all report totals (in case of data inconsistency)
CREATE OR REPLACE FUNCTION public.recalculate_all_report_totals()
RETURNS INTEGER AS $$
DECLARE
    v_updated_count INTEGER := 0;
    v_report RECORD;
BEGIN
    FOR v_report IN SELECT id FROM public.reports
    LOOP
        UPDATE public.reports
        SET
            total_value = COALESCE((
                SELECT SUM(value)
                FROM public.receipts
                WHERE report_id = v_report.id
            ), 0),
            receipts_count = (
                SELECT COUNT(*)
                FROM public.receipts
                WHERE report_id = v_report.id
            ),
            updated_at = NOW()
        WHERE id = v_report.id;

        v_updated_count := v_updated_count + 1;
    END LOOP;

    RETURN v_updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON FUNCTION public.get_user_statistics IS 'Get comprehensive statistics for a user';
COMMENT ON FUNCTION public.get_report_summary IS 'Get detailed summary of a report including receipt statistics';
COMMENT ON FUNCTION public.search_reports IS 'Full-text search for reports using Portuguese language';
COMMENT ON FUNCTION public.bulk_delete_receipts IS 'Delete multiple receipts in a single transaction';
COMMENT ON FUNCTION public.duplicate_report IS 'Create a copy of an existing report without receipts';
