import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Platform
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { Receipt } from '../types';
import { OCRService } from '../services/ocr';
import { ImageProcessingService } from '../services/imageProcessing';
import { DatabaseService } from '../services/database';

interface CameraCaptureScreenProps {
  navigation: any;
  route: {
    params: {
      reportId: string;
    };
  };
}

export const CameraCaptureScreen: React.FC<CameraCaptureScreenProps> = ({
  navigation,
  route
}) => {
  const { reportId } = route.params;
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState<'back' | 'front'>('back');
  const [processing, setProcessing] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  const processImage = async (imageUri: string) => {
    try {
      setProcessing(true);
      console.log('Processing image:', imageUri);

      // Auto-crop and enhance image
      let processedUri = imageUri;
      try {
        processedUri = await ImageProcessingService.autoCropReceipt(imageUri);
        console.log('Image processed:', processedUri);
      } catch (err) {
        console.log('Error processing image, using original:', err);
        // Use original if processing fails
        processedUri = imageUri;
      }

      // Extract text using OCR
      const ocrResult = await OCRService.extractTextFromImage(processedUri);
      console.log('OCR result:', ocrResult);

      // Prompt user to confirm or edit the extracted value
      let finalValue = ocrResult.extractedValue || 0;

      if (ocrResult.extractedValue) {
        await new Promise<void>((resolve) => {
          Alert.alert(
            'Valor Detectado',
            `Foi detectado o valor de ${OCRService.formatCurrency(ocrResult.extractedValue!)}. Deseja usar este valor?`,
            [
              {
                text: 'Editar',
                onPress: () => {
                  Alert.prompt(
                    'Digite o Valor',
                    'Digite o valor do recibo:',
                    [
                      { text: 'Cancelar', style: 'cancel', onPress: () => resolve() },
                      {
                        text: 'OK',
                        onPress: (value) => {
                          const parsedValue = parseFloat(value?.replace(',', '.') || '0');
                          if (!isNaN(parsedValue) && parsedValue > 0) {
                            finalValue = parsedValue;
                          }
                          resolve();
                        }
                      }
                    ],
                    'plain-text',
                    ocrResult.extractedValue!.toString()
                  );
                }
              },
              {
                text: 'Usar',
                onPress: () => resolve()
              }
            ]
          );
        });
      } else {
        // No value detected, ask user to input manually
        await new Promise<void>((resolve) => {
          Alert.prompt(
            'Digite o Valor',
            'Não foi possível detectar o valor automaticamente. Por favor, digite o valor do recibo:',
            [
              {
                text: 'Cancelar',
                style: 'cancel',
                onPress: () => {
                  resolve();
                }
              },
              {
                text: 'OK',
                onPress: (value) => {
                  const parsedValue = parseFloat(value?.replace(',', '.') || '0');
                  if (!isNaN(parsedValue) && parsedValue > 0) {
                    finalValue = parsedValue;
                  }
                  resolve();
                }
              }
            ],
            'plain-text'
          );
        });
      }

      if (finalValue <= 0) {
        Alert.alert('Erro', 'Por favor, insira um valor válido');
        setProcessing(false);
        return;
      }

      // ImageManipulator already saves the file, so we can use processedUri directly
      console.log('Creating receipt with URI:', processedUri);

      // Create receipt record
      const receipt: Receipt = {
        id: Date.now().toString(),
        reportId,
        imageUri: processedUri,
        croppedImageUri: processedUri,
        value: finalValue,
        date: new Date(),
        createdAt: new Date(),
        updatedAt: new Date()
      };

      console.log('Saving receipt to database...');
      // Save to database
      try {
        await DatabaseService.saveReceipt(receipt);
        console.log('Receipt saved successfully');
      } catch (dbError) {
        console.error('Database save error:', dbError);
        throw new Error('Erro ao salvar no banco de dados');
      }

      Alert.alert('Sucesso', 'Recibo adicionado com sucesso!', [
        {
          text: 'OK',
          onPress: () => navigation.goBack()
        }
      ]);
    } catch (error: any) {
      console.error('Error processing image:', error);
      const errorMessage = error?.message || 'Não foi possível processar a imagem';
      Alert.alert(
        'Erro ao Processar Imagem',
        errorMessage + '\n\nTente tirar a foto novamente ou escolher da galeria.',
        [
          { text: 'OK' }
        ]
      );
    } finally {
      setProcessing(false);
    }
  };

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8
        });

        if (photo?.uri) {
          await processImage(photo.uri);
        }
      } catch (error) {
        console.error('Error taking picture:', error);
        Alert.alert('Erro', 'Não foi possível tirar a foto');
      }
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8
      });

      if (!result.canceled && result.assets[0]) {
        await processImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Erro', 'Não foi possível selecionar a imagem');
    }
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Precisamos de acesso à câmera</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={requestPermission}
        >
          <Text style={styles.buttonText}>Permitir Câmera</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.button, { marginTop: 10, backgroundColor: '#666' }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>Voltar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (processing) {
    return (
      <View style={styles.processingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.processingText}>Processando imagem...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
        <View style={styles.overlay}>
          <View style={styles.topBar}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <Text style={styles.backButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.guideline}>
            <View style={styles.corner} style={[styles.corner, styles.topLeft]} />
            <View style={styles.corner} style={[styles.corner, styles.topRight]} />
            <View style={styles.corner} style={[styles.corner, styles.bottomLeft]} />
            <View style={styles.corner} style={[styles.corner, styles.bottomRight]} />
            <Text style={styles.guideText}>
              Posicione o recibo dentro da área marcada
            </Text>
          </View>

          <View style={styles.controls}>
            <TouchableOpacity style={styles.galleryButton} onPress={pickImage}>
              <Text style={styles.galleryButtonText}>📷</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
              <View style={styles.captureButtonInner} />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.flipButton}
              onPress={() => {
                setFacing(facing === 'back' ? 'front' : 'back');
              }}
            >
              <Text style={styles.flipButtonText}>🔄</Text>
            </TouchableOpacity>
          </View>
        </View>
      </CameraView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center'
  },
  camera: {
    flex: 1,
    width: '100%'
  },
  overlay: {
    flex: 1,
    backgroundColor: 'transparent'
  },
  topBar: {
    padding: 20,
    paddingTop: Platform.OS === 'ios' ? 60 : 20
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  backButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold'
  },
  guideline: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 40
  },
  corner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: '#fff',
    borderWidth: 3
  },
  topLeft: {
    top: 0,
    left: 0,
    borderBottomWidth: 0,
    borderRightWidth: 0
  },
  topRight: {
    top: 0,
    right: 0,
    borderBottomWidth: 0,
    borderLeftWidth: 0
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderTopWidth: 0,
    borderRightWidth: 0
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderTopWidth: 0,
    borderLeftWidth: 0
  },
  guideText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 12,
    borderRadius: 8
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 30,
    paddingHorizontal: 40,
    paddingBottom: Platform.OS === 'ios' ? 50 : 30
  },
  galleryButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  galleryButtonText: {
    fontSize: 24
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'rgba(255,255,255,0.5)'
  },
  captureButtonInner: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#2196F3'
  },
  flipButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  flipButtonText: {
    fontSize: 24
  },
  processingContainer: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center'
  },
  processingText: {
    color: '#fff',
    fontSize: 18,
    marginTop: 20
  },
  text: {
    color: '#fff',
    fontSize: 18,
    marginBottom: 20
  },
  button: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  }
});
