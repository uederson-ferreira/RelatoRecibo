# Ícones do App

## Como gerar o ícone

1. Abra o arquivo `generate-icon.html` no navegador
2. Clique em "Baixar 1024x1024" para baixar o ícone principal
3. Renomeie o arquivo baixado para `icon.png`
4. Coloque o arquivo `icon.png` nesta pasta (`assets/`)

## Ou use um gerador online

Se preferir criar um ícone personalizado:

1. Acesse: https://www.appicon.co/ ou https://icon.kitchen/
2. Faça upload de uma imagem 1024x1024
3. Baixe o pacote de ícones
4. Coloque o arquivo icon.png nesta pasta

## Configuração no app.json

O ícone já está configurado em `app.json`:

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png"
    }
  }
}
```

## Tamanhos recomendados

- **icon.png**: 1024x1024 (necessário)
- **splash.png**: 1284x2778 (opcional)
- **adaptive-icon.png**: 1024x1024 (para Android, opcional)

## Design do ícone padrão

O ícone gerado automaticamente tem:
- Fundo azul gradiente (#2196F3 → #1976D2)
- Recibo branco no centro com linhas
- Símbolo R$ em verde
- Ícone de câmera no canto inferior direito
