import AsyncStorage from '@react-native-async-storage/async-storage';
import { Report, Receipt } from '../types';

const REPORTS_KEY = '@relato_recibo_reports';
const RECEIPTS_KEY = '@relato_recibo_receipts';

export class DatabaseService {
  // Reports
  static async getAllReports(): Promise<Report[]> {
    try {
      const data = await AsyncStorage.getItem(REPORTS_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error getting reports:', error);
      return [];
    }
  }

  static async getReport(id: string): Promise<Report | null> {
    try {
      const reports = await this.getAllReports();
      return reports.find(r => r.id === id) || null;
    } catch (error) {
      console.error('Error getting report:', error);
      return null;
    }
  }

  static async saveReport(report: Report): Promise<void> {
    try {
      const reports = await this.getAllReports();
      const index = reports.findIndex(r => r.id === report.id);

      if (index >= 0) {
        reports[index] = { ...report, updatedAt: new Date() };
      } else {
        reports.push(report);
      }

      await AsyncStorage.setItem(REPORTS_KEY, JSON.stringify(reports));
    } catch (error) {
      console.error('Error saving report:', error);
      throw error;
    }
  }

  static async deleteReport(id: string): Promise<void> {
    try {
      const reports = await this.getAllReports();
      const filtered = reports.filter(r => r.id !== id);
      await AsyncStorage.setItem(REPORTS_KEY, JSON.stringify(filtered));

      // Delete associated receipts
      const receipts = await this.getAllReceipts();
      const filteredReceipts = receipts.filter(r => r.reportId !== id);
      await AsyncStorage.setItem(RECEIPTS_KEY, JSON.stringify(filteredReceipts));
    } catch (error) {
      console.error('Error deleting report:', error);
      throw error;
    }
  }

  // Receipts
  static async getAllReceipts(): Promise<Receipt[]> {
    try {
      const data = await AsyncStorage.getItem(RECEIPTS_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error getting receipts:', error);
      return [];
    }
  }

  static async getReceiptsByReport(reportId: string): Promise<Receipt[]> {
    try {
      const receipts = await this.getAllReceipts();
      return receipts.filter(r => r.reportId === reportId);
    } catch (error) {
      console.error('Error getting receipts by report:', error);
      return [];
    }
  }

  static async getReceipt(id: string): Promise<Receipt | null> {
    try {
      const receipts = await this.getAllReceipts();
      return receipts.find(r => r.id === id) || null;
    } catch (error) {
      console.error('Error getting receipt:', error);
      return null;
    }
  }

  static async saveReceipt(receipt: Receipt): Promise<void> {
    try {
      const receipts = await this.getAllReceipts();
      const index = receipts.findIndex(r => r.id === receipt.id);

      if (index >= 0) {
        receipts[index] = { ...receipt, updatedAt: new Date() };
      } else {
        receipts.push(receipt);
      }

      await AsyncStorage.setItem(RECEIPTS_KEY, JSON.stringify(receipts));

      // Update report total
      await this.updateReportTotal(receipt.reportId);
    } catch (error) {
      console.error('Error saving receipt:', error);
      throw error;
    }
  }

  static async deleteReceipt(id: string): Promise<void> {
    try {
      const receipt = await this.getReceipt(id);
      if (!receipt) return;

      const receipts = await this.getAllReceipts();
      const filtered = receipts.filter(r => r.id !== id);
      await AsyncStorage.setItem(RECEIPTS_KEY, JSON.stringify(filtered));

      // Update report total
      await this.updateReportTotal(receipt.reportId);
    } catch (error) {
      console.error('Error deleting receipt:', error);
      throw error;
    }
  }

  private static async updateReportTotal(reportId: string): Promise<void> {
    try {
      const receipts = await this.getReceiptsByReport(reportId);
      const total = receipts.reduce((sum, r) => sum + r.value, 0);

      const report = await this.getReport(reportId);
      if (report) {
        report.totalValue = total;
        report.receiptsCount = receipts.length;
        await this.saveReport(report);
      }
    } catch (error) {
      console.error('Error updating report total:', error);
    }
  }

  static async clearAll(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([REPORTS_KEY, RECEIPTS_KEY]);
    } catch (error) {
      console.error('Error clearing data:', error);
      throw error;
    }
  }
}
