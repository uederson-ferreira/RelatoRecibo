# Início Rápido - RelatoRecibo

## Instalação Rápida

Se você está tendo problemas com a instalação automática, siga estes passos:

### 1. Limpar e Reinstalar

```bash
# Limpar cache do npm
npm cache clean --force

# Remover node_modules e package-lock.json
rm -rf node_modules package-lock.json

# Reinstalar tudo
npm install
```

### 2. Instalar Dependências de Navegação

```bash
npm install @react-navigation/native@^7.0.0 @react-navigation/stack@^7.0.0
```

### 3. Verificar Instalação

```bash
npm list
```

## Testar o App

```bash
# Iniciar o servidor de desenvolvimento
npx expo start

# Ou para iniciar direto no modo de desenvolvimento
npx expo start --clear
```

## Troubleshooting

### Erro "Invalid Version"

Se você receber erros de versão inválida:

```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Erro de Permissões da Câmera

No iOS: Verifique se as permissões estão configuradas no `app.json`
No Android: As permissões devem ser solicitadas automaticamente

### Erro ao Gerar PDF

Verifique se o `expo-print` está instalado corretamente:

```bash
npx expo install expo-print expo-sharing
```

## Estrutura de Dados

### Report (Relatório)

```typescript
{
  id: string;
  name: string;
  description?: string;
  totalValue: number;
  receiptsCount: number;
  status: 'draft' | 'completed' | 'sent';
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  syncedAt?: Date;
}
```

### Receipt (Recibo)

```typescript
{
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
```

## Fluxo de Uso

1. **Criar Relatório** → HomeScreen
2. **Adicionar Recibos** → CameraCaptureScreen
3. **Ver Detalhes** → ReportDetailsScreen
4. **Gerar PDF** → PDFService

## Serviços Disponíveis

- **DatabaseService**: Armazenamento local com AsyncStorage
- **OCRService**: Extração de texto/valores (placeholder, implementar Tesseract)
- **ImageProcessingService**: Manipulação e recorte de imagens
- **PDFService**: Geração de PDFs com fotos
- **SupabaseService**: Sincronização em nuvem (opcional, requer configuração)

## Próximos Passos

1. Implementar OCR real com Tesseract ou Google Vision
2. Configurar Supabase para sync em nuvem
3. Adicionar testes automatizados
4. Implementar autenticação de usuários
5. Adicionar mais features (categorias, filtros, etc.)

## Suporte

Para mais informações, consulte o README.md principal.
