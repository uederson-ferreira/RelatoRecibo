export interface Receipt {
  id: string;
  reportId: string;
  imageUri: string;
  croppedImageUri?: string;
  value: number;
  description?: string;
  date: Date;
  createdAt: Date;
  updatedAt: Date;
  syncedAt?: Date;
}

export interface Report {
  id: string;
  name: string;
  description?: string;
  targetValue?: number;
  totalValue: number;
  receiptsCount: number;
  status: 'draft' | 'completed' | 'sent';
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  syncedAt?: Date;
}

export interface OCRResult {
  text: string;
  confidence: number;
  extractedValue?: number;
  rawData: any;
}

export interface PDFGenerationOptions {
  reportId: string;
  includeImages: boolean;
  imageQuality: 'low' | 'medium' | 'high';
}
