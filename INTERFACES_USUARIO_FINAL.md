# Interfaces para Usuário Final - Synapse IA Sales System

Este documento descreve as diferentes interfaces disponíveis para usuários finais interagirem com o sistema de vendas Synapse IA.

## Visão Geral

O AgentOS oferece múltiplas formas de interação:

1. **Control Plane (os.agno.com)** - Gerenciamento e monitoramento
2. **Agent UI** - Frontend open-source para usuários finais
3. **AG-UI Protocol** - Para frontends customizados (Dojo, etc.)
4. **API Direta** - Integração programática

## 1. Control Plane (os.agno.com)

### O que é?

Interface web centralizada da Agno para gerenciar, monitorar e testar seu AgentOS. É gratuita e os dados ficam apenas no seu AgentOS (privacidade total).

### Como Conectar?

1. Acesse: https://os.agno.com
2. Faça login ou crie uma conta
3. Clique em "Add new OS" na barra de navegação
4. Selecione "Local" para conectar ao AgentOS local
5. Digite o endpoint: `http://localhost:7777`
6. Dê um nome descritivo: "Synapse IA Sales System"
7. Clique em "Connect"

### Funcionalidades

- ✅ Chat com agentes, teams e workflows
- ✅ Gerenciamento de knowledge bases
- ✅ Visualização de sessões e histórico
- ✅ Monitoramento de memórias
- ✅ Métricas e analytics
- ✅ Testes e avaliações

### Nota Importante

- O Control Plane **NÃO** armazena seus dados
- Todos os dados ficam no seu AgentOS (banco de dados local)
- O Control Plane apenas **conecta** ao seu AgentOS

## 2. Agent UI (Frontend Open-Source)

### O que é?

Frontend open-source (Next.js + TypeScript) criado pela comunidade Agno para usuários finais interagirem com agentes. É bonito, moderno e totalmente customizável.

### Como Usar?

#### 2.1 Clonar o Repositório

```bash
git clone https://github.com/agno-agi/agent-ui.git
cd agent-ui
```

#### 2.2 Instalar Dependências

```bash
pnpm install
# ou
npm install
```

#### 2.3 Configurar para Conectar ao AgentOS

O Agent UI precisa se conectar ao seu AgentOS. Configure a URL do AgentOS:

```env
# .env.local
AGENTOS_URL=http://localhost:7777
```

#### 2.4 Executar

```bash
pnpm dev
# ou
npm run dev
```

#### 2.5 Acessar

Abra http://localhost:3000 no navegador.

### Funcionalidades

- ✅ Interface moderna e responsiva
- ✅ Chat com múltiplos agentes
- ✅ Visualização de memórias
- ✅ Histórico de conversas
- ✅ Totalmente open-source e customizável

### Customização

Você pode customizar completamente o Agent UI:
- Cores e temas
- Layout
- Funcionalidades adicionais
- Integrações customizadas

## 3. AG-UI Protocol (Frontends Customizados)

### O que é?

AG-UI (Agent-User Interaction Protocol) é um protocolo padrão para conectar agentes a frontends. O AgentOS já expõe endpoints AG-UI compatíveis.

### Endpoints Disponíveis

- **POST /agui** - Endpoint principal para interagir com agentes via AG-UI
- **GET /agui/status** - Status da interface AG-UI

### Frontends Compatíveis

#### Dojo (Frontend AG-UI Oficial)

```bash
git clone https://github.com/ag-ui-protocol/ag-ui.git
cd ag-ui

# Instalar dependências
cd typescript-sdk && pnpm install
cd ../integrations/agno && pnpm install && pnpm run build

# Executar Dojo
cd ../.. && pnpm dev
```

Acesse: http://localhost:3000

#### Frontend Customizado

Você pode criar seu próprio frontend usando o protocolo AG-UI:

```typescript
// Exemplo de uso do protocolo AG-UI
const response = await fetch('http://localhost:7777/agui', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Olá, preciso de ajuda com automação',
    agent_id: 'lead-qualifier',
    user_id: 'usuario123',
    session_id: 'sessao123'
  })
});
```

### Vantagens do AG-UI

- ✅ Protocolo padrão e aberto
- ✅ Compatível com múltiplos frontends
- ✅ Facilita desenvolvimento de interfaces customizadas
- ✅ Suporte a streaming de respostas

## 4. API Direta (Integração Programática)

### Endpoints Disponíveis

- **API Docs**: http://localhost:7777/docs
- **Config**: http://localhost:7777/config

### Exemplos de Uso

#### Executar um Agente

```bash
curl -X POST "http://localhost:7777/agents/lead-qualifier/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Olá, preciso de automação para meu escritório" \
  -d "user_id=usuario123" \
  -d "session_id=sessao123"
```

#### Executar um Workflow

```bash
curl -X POST "http://localhost:7777/workflows/synapse-sales-workflow/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Qualifique este lead: João Silva, advogado autônomo" \
  -d "user_id=usuario123" \
  -d "session_id=sessao123"
```

#### Executar um Team

```bash
curl -X POST "http://localhost:7777/teams/synapse-sales-team/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Preciso de ajuda com vendas" \
  -d "user_id=usuario123" \
  -d "session_id=sessao123"
```

## Comparação de Interfaces

| Interface | Uso | Customização | Complexidade |
|-----------|-----|--------------|--------------|
| **Control Plane** | Gerenciamento e monitoramento | Limitada | Baixa |
| **Agent UI** | Usuários finais | Alta | Média |
| **AG-UI (Dojo)** | Usuários finais | Alta | Média |
| **API Direta** | Integração programática | Total | Alta |

## Recomendações

### Para Desenvolvimento e Testes
Use o **Control Plane (os.agno.com)** - é a forma mais fácil de testar e monitorar.

### Para Usuários Finais
Use o **Agent UI** ou **Dojo** - interfaces bonitas e prontas para uso.

### Para Integrações Customizadas
Use a **API Direta** ou **AG-UI Protocol** - flexibilidade total.

## Próximos Passos

1. **Conectar ao Control Plane**: https://os.agno.com
2. **Testar os agentes** via Control Plane
3. **Clonar Agent UI** para interface de usuário final
4. **Customizar** conforme necessário

## Referências

- [Documentação Control Plane](https://docs.agno.com/agent-os/control-plane)
- [Documentação AG-UI](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction)
- [Agent UI GitHub](https://github.com/agno-agi/agent-ui)
- [Dojo GitHub](https://github.com/ag-ui-protocol/ag-ui)
- [AgentOS API](https://docs.agno.com/agent-os/api)


