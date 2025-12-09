import { OCRResult } from '../types';

export class OCRService {
  /**
   * Extracts text from an image using OCR
   * Note: This is a placeholder implementation. For production, you'll need to:
   * 1. Use react-native-tesseract-ocr or similar library
   * 2. Or use a cloud service like Google Cloud Vision API
   */
  static async extractTextFromImage(imageUri: string): Promise<OCRResult> {
    try {
      // TODO: Implement actual OCR using Tesseract or similar
      // For now, this is a placeholder that returns mock data

      console.log('OCR: Processing image:', imageUri);

      // Simulate OCR processing
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock OCR result
      const mockText = 'RECIBO\nValor: R$ 150,00\nData: 08/12/2025';
      const extractedValue = this.extractValueFromText(mockText);

      return {
        text: mockText,
        confidence: 0.85,
        extractedValue,
        rawData: { mock: true }
      };
    } catch (error) {
      console.error('OCR Error:', error);
      throw new Error('Failed to extract text from image');
    }
  }

  /**
   * Extracts monetary value from OCR text
   */
  static extractValueFromText(text: string): number | undefined {
    try {
      // Common patterns for Brazilian currency
      const patterns = [
        /R\$\s*(\d+[.,]\d{2})/i,           // R$ 150,00 or R$ 150.00
        /valor[:\s]+R?\$?\s*(\d+[.,]\d{2})/i, // Valor: 150,00
        /total[:\s]+R?\$?\s*(\d+[.,]\d{2})/i, // Total: 150,00
        /(\d+[.,]\d{2})\s*reais/i,         // 150,00 reais
      ];

      for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
          // Convert Brazilian format (150,00) to number (150.00)
          const valueStr = match[1].replace('.', '').replace(',', '.');
          const value = parseFloat(valueStr);

          if (!isNaN(value) && value > 0) {
            return value;
          }
        }
      }

      return undefined;
    } catch (error) {
      console.error('Error extracting value from text:', error);
      return undefined;
    }
  }

  /**
   * Validates if extracted value seems reasonable
   */
  static isValidValue(value: number): boolean {
    return value > 0 && value < 1000000; // Between 0 and 1 million
  }

  /**
   * Formats currency for display
   */
  static formatCurrency(value: number): string {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }
}

/**
 * TODO: To implement full Tesseract OCR:
 *
 * 1. Install: npm install react-native-tesseract-ocr
 *
 * 2. Update extractTextFromImage:
 *
 * import TesseractOcr from 'react-native-tesseract-ocr';
 *
 * static async extractTextFromImage(imageUri: string): Promise<OCRResult> {
 *   try {
 *     const tessOptions = {
 *       whitelist: null,
 *       blacklist: null
 *     };
 *
 *     const text = await TesseractOcr.recognize(
 *       imageUri,
 *       'por', // Portuguese language
 *       tessOptions
 *     );
 *
 *     const extractedValue = this.extractValueFromText(text);
 *
 *     return {
 *       text,
 *       confidence: 0.85, // Tesseract provides confidence per word
 *       extractedValue,
 *       rawData: { text }
 *     };
 *   } catch (error) {
 *     console.error('OCR Error:', error);
 *     throw new Error('Failed to extract text from image');
 *   }
 * }
 */
