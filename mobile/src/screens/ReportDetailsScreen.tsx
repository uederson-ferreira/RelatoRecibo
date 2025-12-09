import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  Image,
  ActivityIndicator,
  Modal,
  Dimensions
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import { Report, Receipt } from '../types';
import { DatabaseService } from '../services/database';
import { PDFService } from '../services/pdf';
import { OCRService } from '../services/ocr';

const { width, height } = Dimensions.get('window');

interface ReportDetailsScreenProps {
  navigation: any;
  route: {
    params: {
      reportId: string;
    };
  };
}

export const ReportDetailsScreen: React.FC<ReportDetailsScreenProps> = ({
  navigation,
  route
}) => {
  const { reportId } = route.params;
  const [report, setReport] = useState<Report | null>(null);
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  const [imageModalVisible, setImageModalVisible] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const reportData = await DatabaseService.getReport(reportId);
      const receiptsData = await DatabaseService.getReceiptsByReport(reportId);

      setReport(reportData);
      setReceipts(receiptsData.sort((a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      ));
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('Erro', 'Não foi possível carregar os dados');
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [reportId])
  );

  const handleAddReceipt = () => {
    navigation.navigate('CameraCapture', { reportId });
  };

  const handleDeleteReceipt = (receipt: Receipt) => {
    Alert.alert(
      'Confirmar Exclusão',
      'Deseja realmente excluir este recibo?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: async () => {
            try {
              await DatabaseService.deleteReceipt(receipt.id);
              await loadData();
            } catch (error) {
              console.error('Error deleting receipt:', error);
              Alert.alert('Erro', 'Não foi possível excluir o recibo');
            }
          }
        }
      ]
    );
  };

  const handleGeneratePDF = async () => {
    if (!report) return;

    if (receipts.length === 0) {
      Alert.alert('Atenção', 'Adicione pelo menos um recibo antes de gerar o PDF');
      return;
    }

    try {
      setGeneratingPDF(true);
      await PDFService.generateAndShare(report, receipts);

      // Update report status
      if (report.status === 'draft') {
        report.status = 'completed';
        report.completedAt = new Date();
        await DatabaseService.saveReport(report);
        await loadData();
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      Alert.alert('Erro', 'Não foi possível gerar o PDF');
    } finally {
      setGeneratingPDF(false);
    }
  };

  const handleCompleteReport = async () => {
    if (!report) return;

    if (receipts.length === 0) {
      Alert.alert('Atenção', 'Adicione pelo menos um recibo antes de concluir');
      return;
    }

    Alert.alert(
      'Concluir Relatório',
      'Deseja marcar este relatório como concluído?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Concluir',
          onPress: async () => {
            try {
              report.status = 'completed';
              report.completedAt = new Date();
              await DatabaseService.saveReport(report);
              await loadData();
            } catch (error) {
              console.error('Error completing report:', error);
              Alert.alert('Erro', 'Não foi possível concluir o relatório');
            }
          }
        }
      ]
    );
  };

  const handleViewReceipt = (receipt: Receipt) => {
    setSelectedReceipt(receipt);
    setImageModalVisible(true);
  };

  const renderReceiptItem = ({ item }: { item: Receipt }) => (
    <TouchableOpacity
      style={styles.receiptCard}
      onPress={() => handleViewReceipt(item)}
      onLongPress={() => handleDeleteReceipt(item)}
    >
      <Image
        source={{ uri: item.croppedImageUri || item.imageUri }}
        style={styles.receiptImage}
        resizeMode="cover"
      />

      <View style={styles.receiptInfo}>
        <Text style={styles.receiptValue}>
          {OCRService.formatCurrency(item.value)}
        </Text>

        {item.description && (
          <Text style={styles.receiptDescription} numberOfLines={2}>
            {item.description}
          </Text>
        )}

        <Text style={styles.receiptDate}>
          {new Date(item.date).toLocaleDateString('pt-BR')}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!report) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Relatório não encontrado</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <View style={styles.header}>
        <View style={styles.headerInfo}>
          <Text style={styles.reportName}>{report.name}</Text>
          <Text style={styles.reportTotal}>
            {OCRService.formatCurrency(report.totalValue)}
          </Text>
        </View>

        <View style={styles.actionButtons}>
          {report.status === 'draft' && receipts.length > 0 && (
            <TouchableOpacity
              style={styles.completeButton}
              onPress={handleCompleteReport}
            >
              <Text style={styles.buttonText}>Concluir</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={[styles.pdfButton, generatingPDF && styles.buttonDisabled]}
            onPress={handleGeneratePDF}
            disabled={generatingPDF}
          >
            {generatingPDF ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Gerar PDF</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{receipts.length}</Text>
          <Text style={styles.statLabel}>Recibos</Text>
        </View>

        <View style={styles.statDivider} />

        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {OCRService.formatCurrency(report.totalValue / Math.max(receipts.length, 1))}
          </Text>
          <Text style={styles.statLabel}>Média</Text>
        </View>

        {report.targetValue && (
          <>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {Math.min(100, Math.round((report.totalValue / report.targetValue) * 100))}%
              </Text>
              <Text style={styles.statLabel}>da Meta</Text>
            </View>
          </>
        )}
      </View>

      {report.targetValue && (
        <View style={styles.targetContainer}>
          <View style={styles.targetInfo}>
            <Text style={styles.targetLabel}>
              Meta: {OCRService.formatCurrency(report.targetValue)}
            </Text>
            <Text style={styles.targetRemaining}>
              {report.totalValue >= report.targetValue
                ? '✓ Meta atingida!'
                : `Faltam ${OCRService.formatCurrency(report.targetValue - report.totalValue)}`}
            </Text>
          </View>
          <View style={styles.targetProgressBar}>
            <View
              style={[
                styles.targetProgressFill,
                {
                  width: `${Math.min(100, (report.totalValue / report.targetValue) * 100)}%`,
                  backgroundColor: report.totalValue >= report.targetValue ? '#4CAF50' : '#2196F3'
                }
              ]}
            />
          </View>
        </View>
      )}

      {receipts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Nenhum recibo adicionado</Text>
          <Text style={styles.emptySubtext}>
            Toque no botão "+" para capturar um recibo
          </Text>
        </View>
      ) : (
        <FlatList
          data={receipts}
          renderItem={renderReceiptItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContainer}
          numColumns={2}
        />
      )}

      <TouchableOpacity style={styles.fab} onPress={handleAddReceipt}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {/* Modal para visualizar foto completa */}
      <Modal
        visible={imageModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setImageModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <TouchableOpacity
            style={styles.modalBackground}
            activeOpacity={1}
            onPress={() => setImageModalVisible(false)}
          >
            <View style={styles.modalContent}>
              {selectedReceipt && (
                <>
                  <Image
                    source={{ uri: selectedReceipt.croppedImageUri || selectedReceipt.imageUri }}
                    style={styles.modalImage}
                    resizeMode="contain"
                  />
                  <View style={styles.modalInfo}>
                    <Text style={styles.modalValue}>
                      {OCRService.formatCurrency(selectedReceipt.value)}
                    </Text>
                    <Text style={styles.modalDate}>
                      {new Date(selectedReceipt.date).toLocaleDateString('pt-BR')}
                    </Text>
                  </View>
                  <TouchableOpacity
                    style={styles.modalCloseButton}
                    onPress={() => setImageModalVisible(false)}
                  >
                    <Text style={styles.modalCloseText}>✕</Text>
                  </TouchableOpacity>
                </>
              )}
            </View>
          </TouchableOpacity>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  errorText: {
    fontSize: 16,
    color: '#666'
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  headerInfo: {
    marginBottom: 16
  },
  reportName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8
  },
  reportTotal: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4CAF50'
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12
  },
  completeButton: {
    flex: 1,
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  pdfButton: {
    flex: 1,
    backgroundColor: '#2196F3',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  buttonDisabled: {
    opacity: 0.6
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 20,
    marginBottom: 16
  },
  statItem: {
    flex: 1,
    alignItems: 'center'
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 4
  },
  statLabel: {
    fontSize: 14,
    color: '#666'
  },
  statDivider: {
    width: 1,
    backgroundColor: '#e0e0e0',
    marginHorizontal: 20
  },
  targetContainer: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    marginHorizontal: 16
  },
  targetInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10
  },
  targetLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666'
  },
  targetRemaining: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3'
  },
  targetProgressBar: {
    height: 12,
    backgroundColor: '#E0E0E0',
    borderRadius: 6,
    overflow: 'hidden'
  },
  targetProgressFill: {
    height: '100%',
    borderRadius: 6
  },
  listContainer: {
    padding: 8
  },
  receiptCard: {
    flex: 1,
    margin: 8,
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  receiptImage: {
    width: '100%',
    height: 120,
    backgroundColor: '#f0f0f0'
  },
  receiptInfo: {
    padding: 12
  },
  receiptValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 4
  },
  receiptDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4
  },
  receiptDate: {
    fontSize: 11,
    color: '#999'
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center'
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#2196F3',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6
  },
  fabText: {
    fontSize: 32,
    color: '#fff',
    fontWeight: '300'
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.9)'
  },
  modalBackground: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    width: width * 0.95,
    maxHeight: height * 0.9,
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalImage: {
    width: width * 0.95,
    height: height * 0.75,
    borderRadius: 8
  },
  modalInfo: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: 16,
    borderRadius: 8,
    marginTop: 16,
    alignItems: 'center',
    minWidth: 200
  },
  modalValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 8
  },
  modalDate: {
    fontSize: 16,
    color: '#666'
  },
  modalCloseButton: {
    position: 'absolute',
    top: 40,
    right: 20,
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4
  },
  modalCloseText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333'
  }
});
