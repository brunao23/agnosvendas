# Documentação WhatsApp - Agno vs Evolution API

## Visão Geral

Existem duas formas de integrar WhatsApp com AgentOS:

1. **Interface Oficial do Agno** (`Whatsapp` interface) - Para WhatsApp Business API (Meta/Facebook)
2. **Implementação Customizada** - Para Evolution API (nossa implementação atual)

## Comparação

| Aspecto | Interface Agno (WhatsApp Business) | Nossa Implementação (Evolution API) |
|---------|-----------------------------------|-----------------------------------|
| **API** | WhatsApp Business API (Meta) | Evolution API |
| **Configuração** | Requer tokens da Meta | Usa Evolution API |
| **Complexidade** | Mais simples (interface oficial) | Customizada (mais controle) |
| **Custo** | Pode ter custos da Meta | Depende do provedor Evolution |
| **Endpoints** | `/whatsapp/webhook` e `/whatsapp/status` | `/webhook/agno` (customizado) |
| **Integração n8n** | Direta via webhook | Via n8n (atual) |

## Opção 1: Interface Oficial do Agno (WhatsApp Business API)

### Quando Usar

- Você tem acesso ao WhatsApp Business API da Meta
- Quer usar a interface oficial e suportada pelo Agno
- Prefere integração mais simples

### Requisitos

1. **WhatsApp Business Account** (Meta)
2. **Variáveis de Ambiente**:
   ```bash
   WHATSAPP_ACCESS_TOKEN=seu_token_da_meta
   WHATSAPP_PHONE_NUMBER_ID=seu_phone_number_id
   WHATSAPP_VERIFY_TOKEN=seu_verify_token
   # Opcional para produção:
   WHATSAPP_APP_SECRET=seu_app_secret
   APP_ENV=production
   ```

### Como Implementar

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.os.interfaces.whatsapp import Whatsapp

# Criar agente
lead_qualifier = Agent(
    id="lead-qualifier",
    name="Lead Qualifier - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    # ... outras configurações
)

# Criar AgentOS com interface WhatsApp
agent_os = AgentOS(
    name="Synapse IA Sales System",
    agents=[lead_qualifier],
    interfaces=[Whatsapp(agent=lead_qualifier)],  # Interface oficial
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="playground:app", port=7777, reload=False)
```

### Endpoints Criados

- `GET /whatsapp/status` - Status da interface
- `GET /whatsapp/webhook` - Verificação do webhook (hub.challenge)
- `POST /whatsapp/webhook` - Recebe mensagens do WhatsApp

### Configuração no Meta/Facebook

1. Acesse o [Facebook Developers](https://developers.facebook.com/)
2. Configure o webhook:
   - **URL**: `https://seu-servidor:7777/whatsapp/webhook`
   - **Verify Token**: O mesmo definido em `WHATSAPP_VERIFY_TOKEN`
3. Configure eventos: `messages`

### Vantagens

- ✅ Interface oficial e suportada pelo Agno
- ✅ Integração mais simples
- ✅ Suporte nativo a imagens, vídeos, áudios
- ✅ Gerenciamento automático de sessões (usa número do telefone como `user_id` e `session_id`)
- ✅ Validação de assinatura automática em produção

### Desvantagens

- ❌ Requer WhatsApp Business API (pode ter custos)
- ❌ Processo de configuração mais complexo com Meta
- ❌ Depende dos serviços da Meta

## Opção 2: Nossa Implementação (Evolution API) - Atual

### Quando Usar

- Você já usa Evolution API ou similar
- Quer mais controle sobre a implementação
- Prefere integração via n8n

### Requisitos

1. **Evolution API** configurada
2. **Variáveis de Ambiente**:
   ```bash
   EVOLUTION_API_URL=https://api.iagoflow.com
   EVOLUTION_API_TOKEN=seu_token
   EVOLUTION_INSTANCE_NAME=NOBRU
   WHATSAPP_DESTINATION=5522992523549
   ```

### Como Implementar

```python
from agno.agent import Agent
from agno.os import AgentOS
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# Criar agente
lead_qualifier = Agent(...)

# Criar AgentOS
agent_os = AgentOS(
    agents=[lead_qualifier],
)

app = agent_os.get_app()

# Criar router customizado
whatsapp_router = APIRouter()

@whatsapp_router.post("/webhook/agno")
async def whatsapp_webhook(request: Request):
    # Processar mensagens da Evolution API
    # Enviar para Lead Qualifier
    # Enviar resposta via Evolution API
    pass

app.include_router(whatsapp_router)
```

### Endpoints Criados

- `POST /webhook/agno` - Recebe mensagens via n8n/Evolution API
- `GET /webhook/agno` - Verificação do webhook

### Configuração

1. Configure Evolution API para enviar webhooks para n8n
2. Configure n8n para encaminhar para `/webhook/agno`
3. Sistema processa e responde automaticamente

### Vantagens

- ✅ Mais controle sobre a implementação
- ✅ Flexível (funciona com qualquer API de WhatsApp)
- ✅ Integração com n8n já configurada
- ✅ Sem dependência direta da Meta

### Desvantagens

- ❌ Implementação customizada (manutenção própria)
- ❌ Precisa gerenciar envio de mensagens manualmente
- ❌ Não tem suporte nativo a mídia (precisa implementar)

## Qual Usar?

### Use Interface Agno se:
- ✅ Você tem WhatsApp Business API da Meta
- ✅ Quer integração oficial e suportada
- ✅ Precisa de suporte completo a mídia

### Use Evolution API (atual) se:
- ✅ Você já usa Evolution API ou similar
- ✅ Quer mais controle e flexibilidade
- ✅ Já tem n8n configurado
- ✅ Prefere evitar dependência da Meta

## Migração de Evolution API para Interface Agno

Se quiser migrar para a interface oficial:

### Passo 1: Obter Credenciais da Meta

1. Crie uma conta no [Facebook Developers](https://developers.facebook.com/)
2. Configure um app do WhatsApp Business
3. Obtenha:
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_VERIFY_TOKEN`

### Passo 2: Atualizar Código

```python
# Remover implementação customizada
# Remover whatsapp_router e endpoints customizados

# Adicionar interface oficial
from agno.os.interfaces.whatsapp import Whatsapp

agent_os = AgentOS(
    agents=[lead_qualifier],
    interfaces=[Whatsapp(agent=lead_qualifier)],  # Substituir router customizado
)
```

### Passo 3: Configurar Variáveis de Ambiente

```bash
export WHATSAPP_ACCESS_TOKEN="seu_token"
export WHATSAPP_PHONE_NUMBER_ID="seu_id"
export WHATSAPP_VERIFY_TOKEN="seu_verify_token"
```

### Passo 4: Configurar Webhook no Meta

- URL: `https://seu-servidor:7777/whatsapp/webhook`
- Verify Token: O mesmo de `WHATSAPP_VERIFY_TOKEN`

## Nossa Implementação Atual (Recomendada para seu caso)

Como você já tem Evolution API configurada e n8n funcionando, **recomendamos manter a implementação atual** por enquanto:

- ✅ Já está funcionando
- ✅ Integração com n8n configurada
- ✅ Controle total sobre o fluxo
- ✅ Sem necessidade de migrar para Meta

## Melhorias Futuras

Se quiser melhorar a implementação atual:

1. **Adicionar suporte a mídia**: Processar imagens, vídeos, áudios
2. **Melhorar tratamento de erros**: Retry logic, fallbacks
3. **Adicionar logs**: Melhor observabilidade
4. **Otimizar performance**: Cache, rate limiting

## Referências

- [Documentação Agno WhatsApp Interface](https://docs.agno.com/agent-os/interfaces/whatsapp)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Evolution API Documentation](https://doc.evolution-api.com)
- [Cookbook Agno WhatsApp](https://github.com/agno-agi/agno/tree/main/cookbook/agent_os/interfaces/whatsapp)


