-- RelatoRecibo Database Schema
-- PostgreSQL 15+ (Supabase)
-- Created: 2025-12-08

-- =====================================================
-- EXTENSIONS
-- =====================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for additional crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- ENUM TYPES
-- =====================================================

-- Report status
CREATE TYPE report_status AS ENUM ('draft', 'completed', 'archived');

-- Receipt status
CREATE TYPE receipt_status AS ENUM ('pending', 'processed', 'error');

-- =====================================================
-- TABLES
-- =====================================================

-- ========== USERS (provided by Supabase Auth) ==========
-- Table: auth.users (managed by Supabase)
-- We'll reference auth.uid() in our RLS policies

-- ========== PROFILES ==========
-- Extended user profile information
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add trigger to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ========== REPORTS ==========
-- Main reports table
CREATE TABLE public.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Report details
    name TEXT NOT NULL,
    description TEXT,
    target_value DECIMAL(12, 2), -- Meta de valor (opcional)

    -- Calculated fields (denormalized for performance)
    total_value DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    receipts_count INTEGER NOT NULL DEFAULT 0,

    -- Status
    status report_status NOT NULL DEFAULT 'draft',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT positive_target_value CHECK (target_value IS NULL OR target_value >= 0),
    CONSTRAINT positive_total_value CHECK (total_value >= 0),
    CONSTRAINT non_negative_count CHECK (receipts_count >= 0)
);

-- Indexes for reports
CREATE INDEX idx_reports_user_id ON public.reports(user_id);
CREATE INDEX idx_reports_status ON public.reports(status);
CREATE INDEX idx_reports_created_at ON public.reports(created_at DESC);
CREATE INDEX idx_reports_user_status ON public.reports(user_id, status);

-- ========== RECEIPTS ==========
-- Receipts/despesas associated with reports
CREATE TABLE public.receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Receipt details
    value DECIMAL(12, 2) NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT,
    notes TEXT,

    -- Image/file information
    image_url TEXT, -- Supabase Storage URL
    image_path TEXT, -- Storage path for deletion
    thumbnail_url TEXT, -- Optional: optimized thumbnail

    -- OCR data
    ocr_text TEXT, -- Raw OCR output
    ocr_confidence DECIMAL(5, 2), -- 0-100 confidence score
    ocr_processed_at TIMESTAMPTZ,
    ocr_status receipt_status DEFAULT 'pending',

    -- Metadata
    file_size INTEGER, -- in bytes
    mime_type TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT positive_value CHECK (value > 0),
    CONSTRAINT valid_confidence CHECK (ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 100))
);

-- Indexes for receipts
CREATE INDEX idx_receipts_report_id ON public.receipts(report_id);
CREATE INDEX idx_receipts_user_id ON public.receipts(user_id);
CREATE INDEX idx_receipts_date ON public.receipts(date DESC);
CREATE INDEX idx_receipts_created_at ON public.receipts(created_at DESC);
CREATE INDEX idx_receipts_report_date ON public.receipts(report_id, date DESC);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- ========== Auto-update updated_at timestamp ==========
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Apply to reports
CREATE TRIGGER update_reports_updated_at
    BEFORE UPDATE ON public.reports
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Apply to receipts
CREATE TRIGGER update_receipts_updated_at
    BEFORE UPDATE ON public.receipts
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- ========== Auto-update report totals ==========
CREATE OR REPLACE FUNCTION public.update_report_totals()
RETURNS TRIGGER AS $$
DECLARE
    v_report_id UUID;
BEGIN
    -- Determine which report to update
    IF TG_OP = 'DELETE' THEN
        v_report_id := OLD.report_id;
    ELSE
        v_report_id := NEW.report_id;
    END IF;

    -- Update report totals
    UPDATE public.reports
    SET
        total_value = COALESCE((
            SELECT SUM(value)
            FROM public.receipts
            WHERE report_id = v_report_id
        ), 0),
        receipts_count = (
            SELECT COUNT(*)
            FROM public.receipts
            WHERE report_id = v_report_id
        ),
        updated_at = NOW()
    WHERE id = v_report_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger on receipt insert/update/delete
CREATE TRIGGER update_report_totals_on_receipt_change
    AFTER INSERT OR UPDATE OF value OR DELETE ON public.receipts
    FOR EACH ROW
    EXECUTE FUNCTION public.update_report_totals();

-- ========== Auto-update completed_at ==========
CREATE OR REPLACE FUNCTION public.update_report_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    -- If status changed to completed, set completed_at
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        NEW.completed_at = NOW();
    END IF;

    -- If status changed from completed, clear completed_at
    IF OLD.status = 'completed' AND NEW.status != 'completed' THEN
        NEW.completed_at = NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_report_completed_at_trigger
    BEFORE UPDATE OF status ON public.reports
    FOR EACH ROW
    EXECUTE FUNCTION public.update_report_completed_at();

-- =====================================================
-- VIEWS
-- =====================================================

-- ========== Reports with user info ==========
CREATE VIEW public.reports_with_user AS
SELECT
    r.*,
    p.email,
    p.full_name,
    p.avatar_url,
    -- Calculate progress percentage
    CASE
        WHEN r.target_value > 0 THEN
            ROUND((r.total_value / r.target_value * 100)::numeric, 2)
        ELSE NULL
    END AS progress_percentage
FROM public.reports r
LEFT JOIN public.profiles p ON r.user_id = p.id;

-- ========== Receipts with report info ==========
CREATE VIEW public.receipts_with_report AS
SELECT
    rc.*,
    rp.name AS report_name,
    rp.status AS report_status,
    p.email AS user_email,
    p.full_name AS user_name
FROM public.receipts rc
LEFT JOIN public.reports rp ON rc.report_id = rp.id
LEFT JOIN public.profiles p ON rc.user_id = p.id;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.profiles IS 'Extended user profile information';
COMMENT ON TABLE public.reports IS 'Main reports/relatórios table';
COMMENT ON TABLE public.receipts IS 'Receipts/despesas associated with reports';

COMMENT ON COLUMN public.reports.total_value IS 'Denormalized sum of all receipt values (auto-calculated)';
COMMENT ON COLUMN public.reports.receipts_count IS 'Denormalized count of receipts (auto-calculated)';
COMMENT ON COLUMN public.receipts.ocr_text IS 'Raw text extracted from OCR';
COMMENT ON COLUMN public.receipts.ocr_confidence IS 'OCR confidence score (0-100)';
COMMENT ON COLUMN public.receipts.image_path IS 'Storage path for Supabase Storage bucket';
