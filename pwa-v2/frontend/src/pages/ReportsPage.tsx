import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { reportService } from '../services/reportService'
import { Plus, FileText, Trash2, Download } from 'lucide-react'
import { format } from 'date-fns'
import ptBR from 'date-fns/locale/pt-BR'
import CreateReportModal from '../components/CreateReportModal'

export default function ReportsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportService.getReports({ limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => reportService.deleteReport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este relatório?')) {
      await deleteMutation.mutateAsync(id)
    }
  }

  const handleDownloadPDF = async (id: string, name: string) => {
    try {
      const blob = await reportService.generatePDF(id, true)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${name}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Erro ao gerar PDF')
    }
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
          <p className="mt-2 text-gray-600">Gerencie seus relatórios de despesas</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary inline-flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Relatório
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Carregando...</div>
      ) : reports?.items.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum relatório</h3>
          <p className="mt-1 text-sm text-gray-500">
            Comece criando seu primeiro relatório.
          </p>
          <div className="mt-6">
            <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
              Criar Relatório
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {reports?.items.map((report) => (
            <div key={report.id} className="card hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <Link
                    to={`/reports/${report.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                  >
                    {report.name}
                  </Link>
                  {report.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {report.description}
                    </p>
                  )}
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Status:</span>
                  <span
                    className={`font-medium ${
                      report.status === 'completed'
                        ? 'text-green-600'
                        : report.status === 'archived'
                        ? 'text-gray-600'
                        : 'text-yellow-600'
                    }`}
                  >
                    {report.status === 'completed'
                      ? 'Concluído'
                      : report.status === 'archived'
                      ? 'Arquivado'
                      : 'Rascunho'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Recibos:</span>
                  <span className="font-medium text-gray-900">{report.receipt_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Valor Total:</span>
                  <span className="font-semibold text-gray-900">
                    R$ {parseFloat(report.total_value || '0').toFixed(2).replace('.', ',')}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Criado em:</span>
                  <span className="text-gray-700">
                    {format(new Date(report.created_at), "dd/MM/yyyy", { locale: ptBR })}
                  </span>
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <Link
                  to={`/reports/${report.id}`}
                  className="flex-1 btn btn-secondary text-center"
                >
                  Ver Detalhes
                </Link>
                <button
                  onClick={() => handleDownloadPDF(report.id, report.name)}
                  className="btn btn-secondary"
                  title="Baixar PDF"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(report.id)}
                  className="btn btn-danger"
                  title="Excluir"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateReportModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['reports'] })
          }}
        />
      )}
    </div>
  )
}
