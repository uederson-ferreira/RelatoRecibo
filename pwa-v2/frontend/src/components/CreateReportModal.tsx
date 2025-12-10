import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { reportService } from '../services/reportService'
import { X } from 'lucide-react'
import { ReportCreate } from '../types'

const reportSchema = z.object({
  name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  description: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  notes: z.string().optional(),
  target_value: z.string().optional().transform((val) => {
    if (!val || val === '') return undefined
    const num = parseFloat(val.replace(',', '.'))
    return isNaN(num) ? undefined : num
  }),
})

type ReportForm = z.infer<typeof reportSchema>

interface Props {
  onClose: () => void
  onSuccess: () => void
}

export default function CreateReportModal({ onClose, onSuccess }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ReportForm>({
    resolver: zodResolver(reportSchema),
  })

  const mutation = useMutation({
    mutationFn: (data: ReportCreate) => reportService.createReport(data),
    onSuccess: () => {
      onSuccess()
    },
  })

  const onSubmit = (data: ReportForm) => {
    mutation.mutate(data as ReportCreate)
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Novo Relatório</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome do Relatório *
            </label>
            <input
              {...register('name')}
              type="text"
              className="input"
              placeholder="Ex: Viagem São Paulo - Janeiro 2025"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descrição
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Descrição opcional do relatório"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Início
              </label>
              <input
                {...register('start_date')}
                type="date"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Fim
              </label>
              <input
                {...register('end_date')}
                type="date"
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Valor de Meta (R$)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">R$</span>
              <input
                {...register('target_value')}
                type="text"
                className="input pl-10"
                placeholder="0,00"
                inputMode="decimal"
                onInput={(e) => {
                  // Format input: allow only numbers and comma/dot
                  const value = e.currentTarget.value.replace(/[^\d,.]/g, '')
                  e.currentTarget.value = value
                }}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Valor total esperado para este relatório (opcional)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observações
            </label>
            <textarea
              {...register('notes')}
              rows={2}
              className="input"
              placeholder="Observações adicionais"
            />
          </div>

          {mutation.isError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              Erro ao criar relatório
            </div>
          )}

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn btn-secondary"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 btn btn-primary"
            >
              {mutation.isPending ? 'Criando...' : 'Criar Relatório'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
