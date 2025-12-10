// Auth types
export interface User {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  email: string
  password: string
  full_name: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// Report types
export type ReportStatus = 'draft' | 'completed' | 'archived'

export interface Report {
  id: string
  user_id: string
  name: string
  description?: string
  start_date?: string
  end_date?: string
  notes?: string
  status: ReportStatus
  target_value?: string
  total_value: string
  receipt_count: number
  created_at: string
  updated_at: string
}

export interface ReportCreate {
  name: string
  description?: string
  start_date?: string
  end_date?: string
  notes?: string
  target_value?: number
}

export interface ReportUpdate {
  name?: string
  description?: string
  start_date?: string
  end_date?: string
  notes?: string
  status?: ReportStatus
  target_value?: number
}

// Receipt types
export type ReceiptStatus = 'pending' | 'processed' | 'error'

export interface Receipt {
  id: string
  report_id: string
  user_id: string
  value: string
  date: string
  description?: string
  category?: string
  notes?: string
  status: ReceiptStatus
  image_url?: string
  thumbnail_url?: string
  ocr_text?: string
  ocr_confidence?: string
  ocr_error?: string
  created_at: string
  updated_at: string
}

export interface ReceiptCreate {
  report_id: string
  value: number
  date: string
  description?: string
  category?: string
  notes?: string
}

export interface ReceiptUpdate {
  value?: number
  date?: string
  description?: string
  category?: string
  notes?: string
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface SuccessResponse {
  success: boolean
  message: string
}

export interface ErrorResponse {
  detail: string | { message: string; details?: any }
}
