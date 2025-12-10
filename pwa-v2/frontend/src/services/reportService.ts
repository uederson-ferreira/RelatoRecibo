import api from './api'
import { Report, ReportCreate, ReportUpdate, PaginatedResponse } from '../types'

export const reportService = {
  async getReports(params?: {
    status?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Report>> {
    const { data } = await api.get<PaginatedResponse<Report>>('/reports', { params })
    return data
  },

  async getReport(id: string): Promise<Report> {
    const { data } = await api.get<Report>(`/reports/${id}`)
    return data
  },

  async createReport(report: ReportCreate): Promise<Report> {
    const { data } = await api.post<Report>('/reports', report)
    return data
  },

  async updateReport(id: string, updates: ReportUpdate): Promise<Report> {
    const { data } = await api.put<Report>(`/reports/${id}`, updates)
    return data
  },

  async deleteReport(id: string): Promise<void> {
    await api.delete(`/reports/${id}`)
  },

  async generatePDF(id: string, download: boolean = false): Promise<Blob> {
    const { data } = await api.get(`/reports/${id}/pdf`, {
      params: { download },
      responseType: 'blob',
    })
    return data
  },
}
