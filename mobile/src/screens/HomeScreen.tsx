import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import { Report } from '../types';
import { DatabaseService } from '../services/database';
import { OCRService } from '../services/ocr';

interface HomeScreenProps {
  navigation: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const [reports, setReports] = useState<Report[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadReports = async () => {
    try {
      const data = await DatabaseService.getAllReports();
      setReports(data.sort((a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      ));
    } catch (error) {
      console.error('Error loading reports:', error);
      Alert.alert('Erro', 'Não foi possível carregar os relatórios');
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadReports();
    }, [])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await loadReports();
    setRefreshing(false);
  };

  const handleCreateReport = () => {
    Alert.prompt(
      'Novo Relatório',
      'Digite o nome do relatório',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Próximo',
          onPress: async (name) => {
            if (!name || name.trim() === '') {
              Alert.alert('Erro', 'Por favor, digite um nome para o relatório');
              return;
            }

            // Pedir meta (valor alvo)
            Alert.prompt(
              'Meta do Relatório',
              'Digite o valor meta/alvo (opcional)',
              [
                { text: 'Pular', onPress: () => createReport(name.trim(), undefined) },
                {
                  text: 'Definir',
                  onPress: async (targetValue) => {
                    const parsedTarget = targetValue ? parseFloat(targetValue.replace(',', '.')) : undefined;
                    createReport(name.trim(), parsedTarget);
                  }
                }
              ],
              'plain-text',
              '',
              'numeric'
            );
          }
        }
      ],
      'plain-text'
    );
  };

  const createReport = async (name: string, targetValue?: number) => {
    try {
      const newReport: Report = {
        id: Date.now().toString(),
        name: name,
        targetValue: targetValue,
        totalValue: 0,
        receiptsCount: 0,
        status: 'draft',
        createdAt: new Date(),
        updatedAt: new Date()
      };

      await DatabaseService.saveReport(newReport);
      await loadReports();
    } catch (error) {
      console.error('Error creating report:', error);
      Alert.alert('Erro', 'Não foi possível criar o relatório');
    }
  };

  const handleDeleteReport = (report: Report) => {
    Alert.alert(
      'Confirmar Exclusão',
      `Deseja realmente excluir o relatório "${report.name}"? Todos os recibos associados serão excluídos.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: async () => {
            try {
              await DatabaseService.deleteReport(report.id);
              await loadReports();
            } catch (error) {
              console.error('Error deleting report:', error);
              Alert.alert('Erro', 'Não foi possível excluir o relatório');
            }
          }
        }
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return '#FFA726';
      case 'completed':
        return '#66BB6A';
      case 'sent':
        return '#42A5F5';
      default:
        return '#9E9E9E';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Rascunho';
      case 'completed':
        return 'Concluído';
      case 'sent':
        return 'Enviado';
      default:
        return status;
    }
  };

  const renderReportItem = ({ item }: { item: Report }) => (
    <TouchableOpacity
      style={styles.reportCard}
      onPress={() => navigation.navigate('ReportDetails', { reportId: item.id })}
      onLongPress={() => handleDeleteReport(item)}
    >
      <View style={styles.reportHeader}>
        <Text style={styles.reportName}>{item.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{getStatusLabel(item.status)}</Text>
        </View>
      </View>

      {item.description && (
        <Text style={styles.reportDescription} numberOfLines={2}>
          {item.description}
        </Text>
      )}

      <View style={styles.reportFooter}>
        <View style={styles.reportInfo}>
          <Text style={styles.reportLabel}>Recibos:</Text>
          <Text style={styles.reportValue}>{item.receiptsCount}</Text>
        </View>

        <View style={styles.reportInfo}>
          <Text style={styles.reportLabel}>Total:</Text>
          <Text style={styles.reportTotal}>{OCRService.formatCurrency(item.totalValue)}</Text>
        </View>
      </View>

      {item.targetValue && (
        <View style={styles.progressContainer}>
          <View style={styles.progressInfo}>
            <Text style={styles.progressLabel}>Meta: {OCRService.formatCurrency(item.targetValue)}</Text>
            <Text style={styles.progressPercentage}>
              {Math.min(100, Math.round((item.totalValue / item.targetValue) * 100))}%
            </Text>
          </View>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${Math.min(100, (item.totalValue / item.targetValue) * 100)}%`,
                  backgroundColor: item.totalValue >= item.targetValue ? '#4CAF50' : '#2196F3'
                }
              ]}
            />
          </View>
        </View>
      )}

      <Text style={styles.reportDate}>
        Criado em {new Date(item.createdAt).toLocaleDateString('pt-BR')}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Relatórios</Text>
        <TouchableOpacity style={styles.addButton} onPress={handleCreateReport}>
          <Text style={styles.addButtonText}>+ Novo</Text>
        </TouchableOpacity>
      </View>

      {reports.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Nenhum relatório criado</Text>
          <Text style={styles.emptySubtext}>
            Toque em "+ Novo" para criar seu primeiro relatório
          </Text>
        </View>
      ) : (
        <FlatList
          data={reports}
          renderItem={renderReportItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333'
  },
  addButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  listContainer: {
    padding: 16
  },
  reportCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  reportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  reportName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 8
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  reportDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12
  },
  reportFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0'
  },
  reportInfo: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  reportLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 4
  },
  reportValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333'
  },
  reportTotal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50'
  },
  reportDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 4
  },
  progressContainer: {
    marginTop: 12,
    marginBottom: 8
  },
  progressInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6
  },
  progressLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500'
  },
  progressPercentage: {
    fontSize: 12,
    color: '#2196F3',
    fontWeight: 'bold'
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    borderRadius: 4
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
  }
});
