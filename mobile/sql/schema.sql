-- =====================================================
-- RelatoRecibo - Database Schema
-- =====================================================
-- NOTA: Este app atualmente NÃO USA BACKEND
-- Os dados são salvos localmente no dispositivo usando AsyncStorage
--
-- Este script SQL é fornecido caso você queira implementar
-- um backend com PostgreSQL/Supabase no futuro
-- =====================================================

-- Tabela de Relatórios
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    target_value DECIMAL(10, 2),
    total_value DECIMAL(10, 2) NOT NULL DEFAULT 0,
    receipts_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('draft', 'completed', 'sent')) DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    synced_at TIMESTAMP
);

-- Tabela de Recibos
CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    image_uri TEXT NOT NULL,
    cropped_image_uri TEXT,
    value DECIMAL(10, 2) NOT NULL,
    description TEXT,
    date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    synced_at TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_receipts_report_id ON receipts(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_receipts_date ON receipts(date DESC);

-- Trigger para atualizar updated_at automaticamente em reports
CREATE OR REPLACE FUNCTION update_report_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reports_updated_at
    BEFORE UPDATE ON reports
    FOR EACH ROW
    EXECUTE FUNCTION update_report_updated_at();

-- Trigger para atualizar updated_at automaticamente em receipts
CREATE OR REPLACE FUNCTION update_receipt_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER receipts_updated_at
    BEFORE UPDATE ON receipts
    FOR EACH ROW
    EXECUTE FUNCTION update_receipt_updated_at();

-- Trigger para atualizar total_value e receipts_count no report
CREATE OR REPLACE FUNCTION update_report_totals()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualizar total_value e receipts_count do relatório
    UPDATE reports
    SET
        total_value = (
            SELECT COALESCE(SUM(value), 0)
            FROM receipts
            WHERE report_id = COALESCE(NEW.report_id, OLD.report_id)
        ),
        receipts_count = (
            SELECT COUNT(*)
            FROM receipts
            WHERE report_id = COALESCE(NEW.report_id, OLD.report_id)
        )
    WHERE id = COALESCE(NEW.report_id, OLD.report_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER receipts_update_report_totals
    AFTER INSERT OR UPDATE OR DELETE ON receipts
    FOR EACH ROW
    EXECUTE FUNCTION update_report_totals();

-- Comentários nas tabelas
COMMENT ON TABLE reports IS 'Relatórios de prestação de contas';
COMMENT ON TABLE receipts IS 'Recibos individuais associados aos relatórios';

COMMENT ON COLUMN reports.target_value IS 'Meta/valor alvo a ser atingido pelo relatório (opcional)';
COMMENT ON COLUMN reports.total_value IS 'Soma total dos valores de todos os recibos';
COMMENT ON COLUMN reports.receipts_count IS 'Quantidade de recibos no relatório';
COMMENT ON COLUMN reports.status IS 'Status do relatório: draft (rascunho), completed (concluído), sent (enviado)';

COMMENT ON COLUMN receipts.image_uri IS 'URI da imagem original do recibo';
COMMENT ON COLUMN receipts.cropped_image_uri IS 'URI da imagem processada/cortada do recibo';
COMMENT ON COLUMN receipts.value IS 'Valor monetário extraído do recibo';
