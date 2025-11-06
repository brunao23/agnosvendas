# Configuração WhatsApp - Sistema de Ativação

## Status

✅ **Integração WhatsApp configurada e funcionando!**

## Como Funciona

1. **Recebimento de Mensagens**: O sistema recebe mensagens via webhook da Evolution API
2. **Ativação**: Só responde quando receber a palavra-chave `##ativar##`
3. **Qualificação**: Após ativar, usa o Lead Qualifier para conversar e qualificar leads
4. **Notificações**: Leads qualificados são enviados automaticamente para WhatsApp

## Configuração do Webhook na Evolution API

### 1. Configurar Webhook na Evolution API

Acesse o painel da Evolution API e configure o webhook:

- **URL do Webhook**: `http://seu-servidor:7777/whatsapp/webhook/evolution`
- **Método**: POST
- **Eventos**: `messages` (mensagens recebidas)

### 2. Se estiver usando servidor local

Para testar localmente, você precisa expor o servidor:

1. **Usar ngrok** (recomendado para testes):
   ```bash
   ngrok http 7777
   ```
   Use a URL gerada pelo ngrok como webhook.

2. **Ou usar serviço de tunnel** como:
   - Cloudflare Tunnel
   - LocalTunnel
   - Serveo

### 3. Estrutura do Webhook

O webhook espera receber mensagens no formato da Evolution API:

```json
{
  "key": {
    "remoteJid": "5522992523549@s.whatsapp.net"
  },
  "message": {
    "conversation": "texto da mensagem"
  }
}
```

Ou:

```json
{
  "from": "5522992523549",
  "text": "texto da mensagem"
}
```

## Fluxo de Funcionamento

### 1. Mensagem Normal (sem ativação)
- Usuário envia: "Olá"
- Sistema: Ignora (sessão não ativada)

### 2. Ativação
- Usuário envia: "##ativar##"
- Sistema: 
  - Ativa sessão para o número
  - Envia mensagem de boas-vindas
  - Responde: "Olá! 👋 Bem-vindo ao assistente da Synapse IA!"

### 3. Conversa Após Ativação
- Usuário envia: "Quero saber sobre automação"
- Sistema:
  - Processa com Lead Qualifier
  - Qualifica o lead
  - Responde com informações da Synapse IA
  - Envia notificação de lead qualificado para WhatsApp

## Endpoints

### POST `/whatsapp/webhook/evolution`
Recebe mensagens da Evolution API

**Respostas:**
- `200`: Mensagem processada
- `200 {"status": "ignored"}`: Sessão não ativada
- `200 {"status": "activated"}`: Sessão ativada
- `200 {"status": "processed"}`: Mensagem processada pelo agente
- `500`: Erro no processamento

### GET `/whatsapp/webhook/evolution`
Verifica se o webhook está ativo

**Resposta:**
```json
{
  "status": "ok",
  "message": "WhatsApp webhook is active"
}
```

## Teste Manual

### 1. Testar Webhook Localmente

```bash
curl -X POST http://localhost:7777/whatsapp/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "key": {
      "remoteJid": "5522992523549@s.whatsapp.net"
    },
    "message": {
      "conversation": "##ativar##"
    }
  }'
```

### 2. Testar Conversa

```bash
curl -X POST http://localhost:7777/whatsapp/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "key": {
      "remoteJid": "5522992523549@s.whatsapp.net"
    },
    "message": {
      "conversation": "Quero saber sobre automação para advogados"
    }
  }'
```

## Configuração no Evolution API

No painel da Evolution API (https://api.iagoflow.com/manager):

1. Acesse sua instância: **NOBRU**
2. Vá em **Webhooks** ou **Configurações**
3. Configure:
   - **URL**: `http://seu-servidor:7777/whatsapp/webhook/evolution`
   - **Método**: POST
   - **Eventos**: `messages`
4. Salve

## Próximos Passos

1. Configure o webhook na Evolution API
2. Teste enviando `##ativar##` para o número conectado
3. Verifique se a mensagem de boas-vindas é enviada
4. Envie outras mensagens e veja o Lead Qualifier em ação
5. Verifique se as notificações de leads qualificados chegam no WhatsApp

## Solução de Problemas

### Webhook não recebe mensagens
- Verifique se a URL está correta
- Confirme que o servidor está acessível (use ngrok se necessário)
- Verifique os logs do servidor

### Mensagens não são processadas
- Confirme que enviou `##ativar##` primeiro
- Verifique se a sessão está ativa (olhe o código de estado)
- Confira os logs do agente

### Erro ao enviar mensagens
- Verifique credenciais da Evolution API
- Confirme que a instância NOBRU está conectada
- Teste o envio manual usando `test_whatsapp.py`


