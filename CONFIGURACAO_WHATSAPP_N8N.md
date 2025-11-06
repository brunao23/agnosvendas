# Configuração WhatsApp via n8n Webhook

## Status

✅ **Integração WhatsApp via n8n configurada!**

> **Nota**: Esta é uma implementação customizada usando Evolution API. Para usar a interface oficial do Agno (WhatsApp Business API), veja `DOCUMENTACAO_WHATSAPP_COMPARACAO.md`.

## Webhook n8n

O sistema agora usa o webhook do n8n para receber mensagens:
- **URL Externa**: `https://webhook.iagoflow.com/webhook/agno`
- **Endpoint Local**: `POST /webhook/agno`
- **Endpoint de Verificação**: `GET /webhook/agno`

## Como Funciona

1. **Recebimento de Mensagens**: O n8n recebe mensagens da Evolution API e encaminha para o nosso servidor
2. **Ativação**: Só responde quando receber a palavra-chave `##ativar##`
3. **Qualificação**: Após ativar, usa o Lead Qualifier para conversar e qualificar leads
4. **Notificações**: Leads qualificados são enviados automaticamente para WhatsApp

## Configuração no n8n

O webhook do n8n (`https://webhook.iagoflow.com/webhook/agno`) já está configurado e precisa apontar para o nosso servidor AgentOS.

**📖 Guia Completo**: Veja `CONFIGURACAO_N8N_AGENTOS.md` para instruções detalhadas de configuração do n8n.

### Resumo Rápido

No n8n, configure o webhook para enviar dados para:
- **URL do Servidor**: `http://seu-servidor:7777/webhook/agno`
- **Método**: POST
- **Content-Type**: `application/json`

### 2. Formato de Dados Esperado

O endpoint aceita diferentes formatos de dados do n8n:

#### Formato 1: Evolução API direto
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

#### Formato 2: Dados diretos
```json
{
  "from": "5522992523549",
  "text": "texto da mensagem"
}
```

#### Formato 3: n8n body wrapper
```json
{
  "body": {
    "from": "5522992523549",
    "text": "texto da mensagem"
  }
}
```

### 3. Mapeamento no n8n

No workflow do n8n, mapeie os campos da Evolution API para o formato esperado:

- **Campo `from`**: Número do remetente (pode vir como `key.remoteJid` ou `from`)
- **Campo `text`**: Texto da mensagem (pode vir como `message.conversation`, `message.text`, ou `text`)

## Fluxo de Funcionamento

### 1. Mensagem Normal (sem ativação)
- Usuário envia: "Olá" via WhatsApp
- Evolution API → n8n → AgentOS
- Sistema: Ignora (sessão não ativada)

### 2. Ativação
- Usuário envia: "##ativar##" via WhatsApp
- Evolution API → n8n → AgentOS
- Sistema: 
  - Ativa sessão para o número
  - Envia mensagem de boas-vindas via Evolution API
  - Responde: "Olá! 👋 Bem-vindo ao assistente da Synapse IA!"

### 3. Conversa Após Ativação
- Usuário envia: "Quero saber sobre automação"
- Evolution API → n8n → AgentOS
- Sistema:
  - Processa com Lead Qualifier
  - Qualifica o lead
  - Responde com informações da Synapse IA
  - Envia notificação de lead qualificado para WhatsApp

## Endpoints Disponíveis

### POST `/webhook/agno`
Recebe mensagens via n8n webhook

**Respostas:**
- `200 {"status": "ignored"}`: Sessão não ativada ou formato inválido
- `200 {"status": "activated"}`: Sessão ativada
- `200 {"status": "processed"}`: Mensagem processada pelo agente
- `500`: Erro no processamento

### GET `/webhook/agno`
Verifica se o webhook está ativo

**Resposta:**
```json
{
  "status": "ok",
  "message": "WhatsApp webhook via n8n is active"
}
```

## Configuração do Servidor

### Local (Desenvolvimento)

Para testar localmente, você precisa expor o servidor. O webhook do n8n já está configurado em `https://webhook.iagoflow.com/webhook/agno`, então você precisa fazer o n8n apontar para seu servidor local ou servidor público.

**Opção 1: Usar ngrok (para testes)**
```bash
ngrok http 7777
```
Configure o n8n para enviar para: `https://seu-ngrok-url.ngrok.io/webhook/agno`

**Opção 2: Servidor Público**
Configure o n8n para enviar para: `http://seu-servidor-publico:7777/webhook/agno`

### Produção

1. Configure o AgentOS em um servidor público
2. Configure o n8n para enviar para: `http://seu-servidor:7777/webhook/agno`
3. Teste enviando `##ativar##` para o número conectado

## Debug

O endpoint inclui logs de debug. Para ver os dados recebidos:

```bash
# Verificar logs do servidor
# Os logs mostrarão:
# [DEBUG] Webhook recebido - Data: {...}
# [DEBUG] From number: ..., Message: ...
```

## Teste Manual

### 1. Testar Webhook Localmente

```bash
curl -X POST http://localhost:7777/webhook/agno \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5522992523549",
    "text": "##ativar##"
  }'
```

### 2. Testar Conversa

```bash
curl -X POST http://localhost:7777/webhook/agno \
  -H "Content-Type: application/json" \
  -d '{
    "from": "5522992523549",
    "text": "Quero saber sobre automação para advogados"
  }'
```

## Próximos Passos

1. ✅ Código atualizado para usar `/webhook/agno`
2. ⏳ Configure o n8n para enviar para seu servidor AgentOS
3. ⏳ Teste enviando `##ativar##` para o número conectado
4. ⏳ Verifique se a mensagem de boas-vindas é enviada
5. ⏳ Envie outras mensagens e veja o Lead Qualifier em ação
6. ⏳ Verifique se as notificações de leads qualificados chegam no WhatsApp

## Compatibilidade

O sistema mantém compatibilidade com o endpoint antigo:
- `/whatsapp/webhook/evolution` (redireciona para `/webhook/agno`)

