# Configuração n8n - Integração AgentOS com WhatsApp

## Visão Geral

Este guia mostra como configurar o n8n para integrar o WhatsApp (via Evolution API) com o AgentOS, permitindo que o sistema de vendas Synapse IA responda automaticamente às mensagens do WhatsApp.

## Arquitetura

```
WhatsApp → Evolution API → n8n → AgentOS → n8n → Evolution API → WhatsApp
```

## Pré-requisitos

1. ✅ AgentOS rodando em `http://localhost:7777` (ou servidor público)
2. ✅ Evolution API configurada com instância `NOBRU`
3. ✅ n8n instalado e configurado
4. ✅ Webhook do n8n: `https://webhook.iagoflow.com/webhook/agno`

## Passo 1: Configurar Webhook no n8n (Receber Mensagens)

### 1.1 Criar Workflow no n8n

1. Abra o n8n
2. Crie um novo workflow
3. Adicione o nó **Webhook**

### 1.2 Configurar Webhook

**Configurações do Webhook:**
- **HTTP Method**: `POST`
- **Path**: `/webhook/agno` (ou o que você configurou)
- **Response Mode**: `When Last Node Finishes`
- **Response Data**: `All Entries`

**URL do Webhook gerada:**
```
https://webhook.iagoflow.com/webhook/agno
```

### 1.3 Configurar Evolution API no n8n

No workflow do n8n, configure o Evolution API para enviar webhooks para o n8n:

1. Vá para o painel da Evolution API
2. Configure o webhook da instância `NOBRU`:
   - **URL**: `https://webhook.iagoflow.com/webhook/agno`
   - **Método**: POST
   - **Eventos**: `messages` (mensagens recebidas)

## Passo 2: Processar Mensagens Recebidas

### 2.1 Adicionar Nó "Function" ou "Code"

Adicione um nó para processar os dados recebidos da Evolution API e formatar para o AgentOS:

**Exemplo de código (nó Code):**
```javascript
// Extrair dados da mensagem
const evolutionData = $input.item.json.body || $input.item.json;

// Extrair número do remetente
let fromNumber = null;
if (evolutionData.key?.remoteJid) {
  fromNumber = evolutionData.key.remoteJid.split('@')[0];
} else if (evolutionData.from) {
  fromNumber = evolutionData.from.replace(/[^0-9]/g, '');
}

// Extrair texto da mensagem
let messageText = null;
if (evolutionData.message?.conversation) {
  messageText = evolutionData.message.conversation;
} else if (evolutionData.message?.extendedTextMessage?.text) {
  messageText = evolutionData.message.extendedTextMessage.text;
} else if (evolutionData.text) {
  messageText = evolutionData.text;
} else if (evolutionData.body) {
  messageText = evolutionData.body;
}

// Retornar dados formatados
return {
  json: {
    from: fromNumber,
    text: messageText,
    original_data: evolutionData
  }
};
```

### 2.2 Adicionar Nó HTTP Request (Enviar para AgentOS)

Configure para enviar a mensagem para o AgentOS:

**Configurações:**
- **Method**: `POST`
- **URL**: `http://localhost:7777/webhook/agno`
- **Authentication**: `None` (ou Bearer Token se configurado)
- **Body Content Type**: `JSON`
- **Body Parameters**:
  ```json
  {
    "from": "={{ $json.from }}",
    "text": "={{ $json.text }}"
  }
  ```

**Nota**: Se o AgentOS estiver em produção, substitua `localhost:7777` pela URL pública do servidor.

## Passo 3: Enviar Resposta de Volta para WhatsApp

### 3.1 Processar Resposta do AgentOS

Adicione um nó para processar a resposta do AgentOS:

**Exemplo (nó Code):**
```javascript
const response = $input.item.json;

// Extrair dados da resposta
let fromNumber = null;
let messageText = null;

if (response.send_result && response.send_result.success) {
  // Resposta já foi enviada pelo AgentOS
  return {
    json: {
      status: 'success',
      message: 'Resposta enviada automaticamente pelo AgentOS'
    }
  };
}

// Se não foi enviado automaticamente, preparar para enviar
if (response.agent_response) {
  messageText = response.agent_response;
} else if (response.message) {
  messageText = response.message;
}

// Pegar número do contexto anterior
fromNumber = $('Function').item.json.from;

return {
  json: {
    from: fromNumber,
    text: messageText,
    send: true
  }
};
```

### 3.2 Enviar para Evolution API

Adicione nó HTTP Request para enviar resposta via Evolution API:

**Configurações:**
- **Method**: `POST`
- **URL**: `https://api.iagoflow.com/message/sendText/NOBRU`
- **Authentication**: `Header Auth`
  - **Name**: `apikey`
  - **Value**: `0D8C5787071D-4419-90CC-DFA6496E9B07`
- **Body Content Type**: `JSON`
- **Body Parameters**:
  ```json
  {
    "number": "={{ $json.from }}",
    "text": "={{ $json.text }}"
  }
  ```

## Passo 4: Alternativa - Usar API Direta do AgentOS

Se preferir usar a API direta do AgentOS em vez do webhook customizado:

### 4.1 Executar Agent via API

Adicione nó HTTP Request para executar o Lead Qualifier:

**Configurações:**
- **Method**: `POST`
- **URL**: `http://localhost:7777/agents/lead-qualifier/runs`
- **Body Content Type**: `Form-Data` ou `x-www-form-urlencoded`
- **Body Parameters**:
  - `message`: `={{ $json.text }}`
  - `user_id`: `={{ $json.from }}`
  - `stream`: `false`

### 4.2 Processar Resposta do Agent

Adicione nó para extrair a resposta:

```javascript
const response = $input.item.json;

// Extrair conteúdo da resposta
let messageText = null;
if (response.content) {
  messageText = response.content;
} else if (response.response?.content) {
  messageText = response.response.content;
}

// Pegar número do contexto
const fromNumber = $('Function').item.json.from;

return {
  json: {
    from: fromNumber,
    text: messageText,
    send: true
  }
};
```

### 4.3 Enviar Resposta para WhatsApp

Use o mesmo nó HTTP Request da Evolution API (Passo 3.2).

## Passo 5: Workflow Completo Exemplo

### Estrutura do Workflow:

```
1. Webhook (Receber mensagem)
   ↓
2. Function/Code (Processar dados)
   ↓
3. HTTP Request (Enviar para AgentOS)
   ↓
4. Function/Code (Processar resposta)
   ↓
5. HTTP Request (Enviar para Evolution API)
```

### Variáveis de Ambiente no n8n

Configure variáveis de ambiente para facilitar:

```
AGENTOS_URL=http://localhost:7777
EVOLUTION_API_URL=https://api.iagoflow.com
EVOLUTION_INSTANCE=NOBRU
EVOLUTION_API_KEY=0D8C5787071D-4419-90CC-DFA6496E9B07
```

## Passo 6: Testar Workflow

### 6.1 Teste Manual no n8n

1. Ative o workflow no n8n
2. Use o botão "Test" no nó Webhook
3. Envie um JSON de teste:
   ```json
   {
     "from": "5522992523549",
     "text": "##ativar##"
   }
   ```
4. Execute o workflow e verifique se:
   - A mensagem é enviada para o AgentOS
   - O AgentOS responde
   - A resposta é enviada para o WhatsApp

### 6.2 Teste Real via WhatsApp

1. Envie `##ativar##` para o número conectado à instância NOBRU
2. Verifique se recebe a mensagem de boas-vindas
3. Envie outra mensagem e verifique se o Lead Qualifier responde

## Exemplo Completo de Workflow n8n (JSON)

```json
{
  "name": "WhatsApp AgentOS Integration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "webhook/agno",
        "responseMode": "lastNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "jsCode": "// Processar dados da Evolution API\nconst data = $input.item.json.body || $input.item.json;\n\nlet fromNumber = null;\nif (data.key?.remoteJid) {\n  fromNumber = data.key.remoteJid.split('@')[0];\n} else if (data.from) {\n  fromNumber = data.from.replace(/[^0-9]/g, '');\n}\n\nlet messageText = null;\nif (data.message?.conversation) {\n  messageText = data.message.conversation;\n} else if (data.text) {\n  messageText = data.text;\n}\n\nreturn {\n  json: {\n    from: fromNumber,\n    text: messageText\n  }\n};"
      },
      "name": "Process Message",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.AGENTOS_URL }}/webhook/agno",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "from",
              "value": "={{ $json.from }}"
            },
            {
              "name": "text",
              "value": "={{ $json.text }}"
            }
          ]
        },
        "options": {}
      },
      "name": "Send to AgentOS",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.EVOLUTION_API_URL }}/message/sendText/{{ $env.EVOLUTION_INSTANCE }}",
        "authentication": "headerAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "number",
              "value": "={{ $('Process Message').item.json.from }}"
            },
            {
              "name": "text",
              "value": "={{ $json.message || $json.text }}"
            }
          ]
        },
        "options": {}
      },
      "name": "Send to WhatsApp",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Process Message", "type": "main", "index": 0}]]
    },
    "Process Message": {
      "main": [[{"node": "Send to AgentOS", "type": "main", "index": 0}]]
    },
    "Send to AgentOS": {
      "main": [[{"node": "Send to WhatsApp", "type": "main", "index": 0}]]
    }
  }
}
```

## Troubleshooting

### Problema: Webhook não recebe mensagens

**Solução:**
1. Verifique se o webhook está ativo no n8n
2. Verifique se o Evolution API está configurado para enviar para o URL correto
3. Verifique os logs do n8n

### Problema: AgentOS não responde

**Solução:**
1. Verifique se o AgentOS está rodando: `http://localhost:7777/config`
2. Verifique se o endpoint está correto: `/webhook/agno`
3. Verifique os logs do AgentOS para erros

### Problema: Mensagens não chegam no WhatsApp

**Solução:**
1. Verifique se a API key da Evolution está correta
2. Verifique se o número está no formato correto (sem caracteres especiais)
3. Verifique os logs da Evolution API

## Recursos Adicionais

- [Documentação AgentOS API](https://docs.agno.com/reference-api/overview)
- [Documentação Evolution API](https://doc.evolution-api.com)
- [Documentação n8n](https://docs.n8n.io)

## Próximos Passos

1. ✅ Configure o workflow no n8n
2. ✅ Teste recebendo mensagens
3. ✅ Teste enviando respostas
4. ⏳ Configure autenticação (Bearer Token) se necessário
5. ⏳ Configure rate limiting se necessário
6. ⏳ Adicione tratamento de erros
7. ⏳ Configure logs e monitoramento


