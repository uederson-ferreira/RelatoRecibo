import api from './api'
import { Receipt, ReceiptCreate, ReceiptUpdate, PaginatedResponse } from '../types'

export const receiptService = {
  async getReceipts(params?: {
    report_id?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Receipt>> {
    const { data } = await api.get<PaginatedResponse<Receipt>>('/receipts', { params })
    return data
  },

  async getReceipt(id: string): Promise<Receipt> {
    const { data } = await api.get<Receipt>(`/receipts/${id}`)
    return data
  },

  async createReceipt(receipt: ReceiptCreate): Promise<Receipt> {
    const { data } = await api.post<Receipt>('/receipts', receipt)
    return data
  },

  async updateReceipt(id: string, updates: ReceiptUpdate): Promise<Receipt> {
    const { data } = await api.put<Receipt>(`/receipts/${id}`, updates)
    return data
  },

  async deleteReceipt(id: string): Promise<void> {
    await api.delete(`/receipts/${id}`)
  },

  async uploadReceiptImage(receiptId: string, file: File): Promise<Receipt> {
    const formData = new FormData()
    formData.append('file', file)
    
    const { data } = await api.post<Receipt>(
      `/receipts/${receiptId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return data
  },
}
