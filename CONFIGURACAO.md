# Configuração do Sistema de Vendas Synapse IA

## Agentes Disponíveis

### 1. Lead Qualifier - Synapse IA
- **Função**: Qualifica leads de advogados
- **Memória**: ✅ Habilitada (enable_agentic_memory)
- **Ferramentas**: DuckDuckGo, Newspaper4k, Reasoning
- **Características**: Humanizado, não menciona scores ao lead

### 2. Information Collector - Synapse IA
- **Função**: Coleta informações sobre escritórios
- **Memória**: ✅ Habilitada
- **Ferramentas**: DuckDuckGo, Newspaper4k, Reasoning
- **Características**: Web scraping do site Synapse IA

### 3. Objection Handler - Synapse IA
- **Função**: Quebra objeções de forma empática
- **Memória**: ✅ Habilitada
- **Ferramentas**: DuckDuckGo, Newspaper4k, Reasoning
- **Características**: Trata objeções de preço, complexidade, tempo, segurança

### 4. Communication Manager - Synapse IA
- **Função**: Envia emails e agenda reuniões
- **Memória**: ✅ Habilitada
- **Ferramentas**: EmailTools, GoogleCalendarTools (se configurados), Reasoning
- **Características**: Gerencia comunicação e agendamentos

### 5. Closer - Synapse IA
- **Função**: Fecha negócios
- **Memória**: ✅ Habilitada
- **Ferramentas**: DuckDuckGo, Newspaper4k, Reasoning
- **Características**: Humanizado, não menciona probabilidade ao lead

## Configuração de Email e Google Calendar

### EmailTools ✅ CONFIGURADO

O EmailTools está configurado com as credenciais do Gmail:

- **Email**: brunocostaads23@gmail.com
- **Nome do Remetente**: Synapse IA
- **Senha de App**: pyhmuqrzjzdfoomn
- **Servidor SMTP**: smtp.gmail.com
- **Porta**: 465

**Status**: ✅ EmailTools configurado e pronto para uso

**Nota**: Você pode sobrescrever essas configurações usando variáveis de ambiente:
```powershell
$env:EMAIL_SENDER="outro-email@gmail.com"
$env:EMAIL_SENDER_NAME="Outro Nome"
$env:EMAIL_PASSKEY="outra-senha"
```

### GoogleCalendarTools ✅ CONFIGURADO

O GoogleCalendarTools está configurado com as credenciais OAuth 2.0:

- **Arquivo de Credenciais**: `google_credentials.json`
- **Project ID**: gmail-make-417202
- **Client ID**: 115862926779-obilc068n64m7fp1hu0h74gd5cimbfoo.apps.googleusercontent.com

**Status**: ✅ GoogleCalendarTools configurado e pronto para uso

**Nota**: Na primeira execução, o GoogleCalendarTools irá solicitar autorização OAuth. 
Siga o fluxo de autenticação quando solicitado. Um arquivo `token.json` será criado para armazenar os tokens de acesso.

**Personalização**: Você pode usar um arquivo diferente definindo:
```powershell
$env:GOOGLE_CALENDAR_CREDENTIALS_PATH="caminho/para/outro-credentials.json"
```

## Memória

Todos os agentes têm **memória persistente** habilitada (`enable_agentic_memory=True`):
- Lembram informações sobre leads (nome, escritório, dores, interesses)
- Criam memórias sobre interações importantes
- Personalizam conversas futuras baseado em memórias

## Humanização

- ✅ **Nenhum score mencionado ao lead**: Agentes não mencionam scores, avaliações ou probabilidades
- ✅ **Comunicação natural**: Tom caloroso, empático e conversacional
- ✅ **Personalização**: Usa memórias para personalizar cada interação

## Router Inteligente

O workflow roteia automaticamente para:
- **Lead Qualifier**: Quando precisa qualificar leads
- **Information Collector**: Quando precisa coletar informações
- **Objection Handler**: Quando há objeções ou preocupações
- **Communication Manager**: Quando precisa enviar email ou agendar
- **Closer**: Quando está pronto para fechar

