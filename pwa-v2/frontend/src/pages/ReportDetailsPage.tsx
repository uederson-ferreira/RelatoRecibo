import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reportService } from '../services/reportService'
import { receiptService } from '../services/receiptService'
import { ArrowLeft, Plus, Download } from 'lucide-react'
import ReceiptCard from '../components/ReceiptCard'
import UploadReceiptModal from '../components/UploadReceiptModal'
import { useState } from 'react'

export default function ReportDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showUploadModal, setShowUploadModal] = useState(false)

  const { data: report, isLoading: reportLoading } = useQuery({
    queryKey: ['report', id],
    queryFn: () => reportService.getReport(id!),
    enabled: !!id,
  })

  const { data: receipts, isLoading: receiptsLoading } = useQuery({
    queryKey: ['receipts', id],
    queryFn: () => receiptService.getReceipts({ report_id: id! }),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: (receiptId: string) => receiptService.deleteReceipt(receiptId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['receipts', id] })
      queryClient.invalidateQueries({ queryKey: ['report', id] })
    },
  })

  const handleDeleteReceipt = async (receiptId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este recibo?')) {
      await deleteMutation.mutateAsync(receiptId)
    }
  }

  const handleDownloadPDF = async () => {
    if (!report) return
    try {
      const blob = await reportService.generatePDF(report.id, true)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${report.name}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Erro ao gerar PDF')
    }
  }

  if (reportLoading) {
    return (
      <div className="text-center py-12 text-gray-500">Carregando relatório...</div>
    )
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Relatório não encontrado</p>
        <button onClick={() => navigate('/reports')} className="btn btn-primary mt-4">
          Voltar para Relatórios
        </button>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/reports')}
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Voltar
        </button>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{report.name}</h1>
            {report.description && (
              <p className="mt-2 text-gray-600">{report.description}</p>
            )}
            <div className="mt-4 flex gap-4 text-sm text-gray-500">
              {report.start_date && (
                <span>Início: {new Date(report.start_date).toLocaleDateString('pt-BR')}</span>
              )}
              {report.end_date && (
                <span>Fim: {new Date(report.end_date).toLocaleDateString('pt-BR')}</span>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleDownloadPDF} className="btn btn-secondary inline-flex items-center">
              <Download className="h-4 w-4 mr-2" />
              Baixar PDF
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="btn btn-primary inline-flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Recibo
            </button>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Status</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">
            {report.status === 'completed'
              ? 'Concluído'
              : report.status === 'archived'
              ? 'Arquivado'
              : 'Rascunho'}
          </p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Total de Recibos</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">
            {report.receipt_count}
          </p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Valor Total</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">
            R$ {parseFloat(report.total_value || '0').toFixed(2).replace('.', ',')}
          </p>
        </div>
      </div>

      {/* Receipts */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recibos</h2>
        {receiptsLoading ? (
          <div className="text-center py-8 text-gray-500">Carregando recibos...</div>
        ) : receipts?.items.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">Nenhum recibo adicionado ainda.</p>
            <button
              onClick={() => setShowUploadModal(true)}
              className="btn btn-primary inline-flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Primeiro Recibo
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {receipts?.items.map((receipt) => (
              <ReceiptCard
                key={receipt.id}
                receipt={receipt}
                onDelete={() => handleDeleteReceipt(receipt.id)}
              />
            ))}
          </div>
        )}
      </div>

      {showUploadModal && (
        <UploadReceiptModal
          reportId={report.id}
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false)
            queryClient.invalidateQueries({ queryKey: ['receipts', id] })
            queryClient.invalidateQueries({ queryKey: ['report', id] })
          }}
        />
      )}
    </div>
  )
}
