import { Receipt } from '../types'
import { Trash2, Image as ImageIcon } from 'lucide-react'
import { format } from 'date-fns'
import ptBR from 'date-fns/locale/pt-BR'
import { useState } from 'react'

interface Props {
  receipt: Receipt
  onDelete: () => void
}

export default function ReceiptCard({ receipt, onDelete }: Props) {
  const [showImage, setShowImage] = useState(false)

  return (
    <>
      <div className="card hover:shadow-md transition-shadow">
        {receipt.thumbnail_url && (
          <div
            className="mb-4 cursor-pointer rounded-lg overflow-hidden"
            onClick={() => setShowImage(true)}
          >
            <img
              src={receipt.thumbnail_url}
              alt={receipt.description || 'Recibo'}
              className="w-full h-48 object-cover"
            />
          </div>
        )}
        {!receipt.thumbnail_url && (
          <div className="mb-4 bg-gray-100 rounded-lg h-48 flex items-center justify-center">
            <ImageIcon className="h-12 w-12 text-gray-400" />
          </div>
        )}

        <div className="space-y-2">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-lg font-semibold text-gray-900">
                R$ {parseFloat(receipt.value || '0').toFixed(2).replace('.', ',')}
              </p>
              {receipt.description && (
                <p className="text-sm text-gray-600 mt-1">{receipt.description}</p>
              )}
            </div>
            <button
              onClick={onDelete}
              className="text-red-600 hover:text-red-800"
              title="Excluir recibo"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>

          <div className="text-sm text-gray-500 space-y-1">
            <p>Data: {format(new Date(receipt.date), "dd/MM/yyyy", { locale: ptBR })}</p>
            {receipt.category && <p>Categoria: {receipt.category}</p>}
            {receipt.status === 'processed' && receipt.ocr_confidence && (
              <p className="text-green-600">
                OCR: {(parseFloat(receipt.ocr_confidence) * 100).toFixed(0)}% confiança
              </p>
            )}
            {receipt.status === 'error' && receipt.ocr_error && (
              <p className="text-red-600">Erro no OCR: {receipt.ocr_error}</p>
            )}
          </div>
        </div>
      </div>

      {showImage && receipt.image_url && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowImage(false)}
        >
          <div className="max-w-4xl max-h-full">
            <img
              src={receipt.image_url}
              alt={receipt.description || 'Recibo'}
              className="max-w-full max-h-full object-contain"
            />
          </div>
        </div>
      )}
    </>
  )
}
