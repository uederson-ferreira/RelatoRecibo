import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { Report, Receipt } from '../types';
import { OCRService } from './ocr';

export class PDFService {
  /**
   * Generates a PDF report with receipts
   */
  static async generateReport(
    report: Report,
    receipts: Receipt[]
  ): Promise<string> {
    try {
      const html = await this.generateHTML(report, receipts);

      const { uri } = await Print.printToFileAsync({
        html,
        base64: false
      });

      return uri;
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF report');
    }
  }

  /**
   * Generates and shares a PDF report
   */
  static async generateAndShare(
    report: Report,
    receipts: Receipt[]
  ): Promise<void> {
    try {
      const pdfUri = await this.generateReport(report, receipts);

      // Check if sharing is available
      const isAvailable = await Sharing.isAvailableAsync();

      if (isAvailable) {
        await Sharing.shareAsync(pdfUri, {
          mimeType: 'application/pdf',
          dialogTitle: `Relatório - ${report.name}`,
          UTI: 'com.adobe.pdf'
        });
      } else {
        throw new Error('Sharing is not available on this device');
      }
    } catch (error) {
      console.error('Error sharing PDF:', error);
      throw error;
    }
  }

  /**
   * Generates HTML content for the PDF
   */
  private static async generateHTML(
    report: Report,
    receipts: Receipt[]
  ): Promise<string> {
    const receiptItems = await this.generateReceiptItems(receipts);

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }

            body {
              font-family: 'Helvetica', 'Arial', sans-serif;
              padding: 40px;
              font-size: 12px;
              line-height: 1.6;
              color: #333;
            }

            .header {
              text-align: center;
              margin-bottom: 40px;
              border-bottom: 2px solid #2196F3;
              padding-bottom: 20px;
            }

            .header h1 {
              color: #2196F3;
              font-size: 28px;
              margin-bottom: 10px;
            }

            .header .subtitle {
              color: #666;
              font-size: 14px;
            }

            .report-info {
              background-color: #f5f5f5;
              padding: 20px;
              border-radius: 8px;
              margin-bottom: 30px;
            }

            .report-info h2 {
              color: #2196F3;
              font-size: 18px;
              margin-bottom: 15px;
            }

            .info-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 8px;
            }

            .info-label {
              font-weight: bold;
              color: #666;
            }

            .receipts-section {
              margin-top: 30px;
            }

            .receipts-section h2 {
              color: #2196F3;
              font-size: 18px;
              margin-bottom: 20px;
              border-bottom: 1px solid #ddd;
              padding-bottom: 10px;
            }

            .receipt-item {
              margin-bottom: 40px;
              page-break-inside: avoid;
              border: 1px solid #ddd;
              border-radius: 8px;
              padding: 15px;
              background-color: #fff;
            }

            .receipt-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 15px;
              padding-bottom: 10px;
              border-bottom: 1px solid #eee;
            }

            .receipt-number {
              font-weight: bold;
              color: #2196F3;
              font-size: 14px;
            }

            .receipt-value {
              font-weight: bold;
              color: #4CAF50;
              font-size: 16px;
            }

            .receipt-details {
              margin-bottom: 15px;
            }

            .receipt-details p {
              margin-bottom: 5px;
              color: #666;
            }

            .receipt-image {
              width: 100%;
              max-width: 500px;
              margin: 15px auto;
              display: block;
              border: 1px solid #ddd;
              border-radius: 4px;
            }

            .summary {
              margin-top: 40px;
              padding: 20px;
              background-color: #e3f2fd;
              border-radius: 8px;
              border-left: 4px solid #2196F3;
            }

            .summary h3 {
              color: #2196F3;
              margin-bottom: 15px;
              font-size: 16px;
            }

            .summary-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 8px;
              font-size: 14px;
            }

            .summary-total {
              font-size: 18px;
              font-weight: bold;
              color: #2196F3;
              margin-top: 10px;
              padding-top: 10px;
              border-top: 2px solid #2196F3;
            }

            .footer {
              margin-top: 50px;
              text-align: center;
              color: #999;
              font-size: 10px;
              border-top: 1px solid #ddd;
              padding-top: 20px;
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Relatório de Prestação de Contas</h1>
            <p class="subtitle">RelatoRecibo - Sistema de Gestão de Recibos</p>
          </div>

          <div class="report-info">
            <h2>${report.name}</h2>
            ${report.description ? `<p style="margin-bottom: 15px; color: #666;">${report.description}</p>` : ''}
            <div class="info-row">
              <span class="info-label">Data de Criação:</span>
              <span>${new Date(report.createdAt).toLocaleDateString('pt-BR')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Status:</span>
              <span>${this.getStatusLabel(report.status)}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Número de Recibos:</span>
              <span>${receipts.length}</span>
            </div>
          </div>

          <div class="receipts-section">
            <h2>Recibos</h2>
            ${receiptItems}
          </div>

          <div class="summary">
            <h3>Resumo Financeiro</h3>
            <div class="summary-row">
              <span>Quantidade de Recibos:</span>
              <span>${receipts.length}</span>
            </div>
            ${report.targetValue ? `
            <div class="summary-row">
              <span>Meta:</span>
              <span>${OCRService.formatCurrency(report.targetValue)}</span>
            </div>
            <div class="summary-row">
              <span>Progresso:</span>
              <span>${Math.min(100, Math.round((report.totalValue / report.targetValue) * 100))}%</span>
            </div>
            ` : ''}
            <div class="summary-row summary-total">
              <span>Valor Total:</span>
              <span>${OCRService.formatCurrency(report.totalValue)}</span>
            </div>
          </div>

          <div class="footer">
            <p>Gerado em ${new Date().toLocaleString('pt-BR')}</p>
            <p>RelatoRecibo - Todos os direitos reservados</p>
          </div>
        </body>
      </html>
    `;

    return html;
  }

  /**
   * Generates HTML for receipt items
   */
  private static async generateReceiptItems(receipts: Receipt[]): Promise<string> {
    const items = await Promise.all(
      receipts.map(async (receipt, index) => {
        const imageUri = receipt.croppedImageUri || receipt.imageUri;
        let imageBase64 = '';

        try {
          // Convert image to base64 for embedding in PDF
          const base64 = await FileSystem.readAsStringAsync(imageUri, {
            encoding: FileSystem.EncodingType.Base64
          });
          imageBase64 = `data:image/jpeg;base64,${base64}`;
        } catch (error) {
          console.error('Error reading image:', error);
        }

        return `
          <div class="receipt-item">
            <div class="receipt-header">
              <span class="receipt-number">Recibo #${index + 1}</span>
              <span class="receipt-value">${OCRService.formatCurrency(receipt.value)}</span>
            </div>
            <div class="receipt-details">
              ${receipt.description ? `<p><strong>Descrição:</strong> ${receipt.description}</p>` : ''}
              <p><strong>Data:</strong> ${new Date(receipt.date).toLocaleDateString('pt-BR')}</p>
            </div>
            ${imageBase64 ? `<img src="${imageBase64}" class="receipt-image" alt="Recibo ${index + 1}" />` : ''}
          </div>
        `;
      })
    );

    return items.join('\n');
  }

  /**
   * Gets localized status label
   */
  private static getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      draft: 'Rascunho',
      completed: 'Concluído',
      sent: 'Enviado'
    };

    return labels[status] || status;
  }
}
