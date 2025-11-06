# Sistema de Agentes de Vendas (Agno)

Este projeto contém dois sistemas de agentes de vendas usando o framework Agno:

1. **Sistema de Pré-Venda** (`presales_workflow.py`) - Workflow com Router e agentes especializados
2. **Time de Vendas** (`sales_team.py`) - Time coordenado de agentes

## Requisitos
- Python 3.10+
- Chave de API da OpenAI (`OPENAI_API_KEY`)

## Instalação
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuração
Configure a variável de ambiente:
```powershell
$env:OPENAI_API_KEY="sua_chave_aqui"
```

Ou crie um arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_aqui
```

## Executar

### 🚀 AgentOS Local (Playground da Agno) - RECOMENDADO

#### Opção 1: Script Automático (Mais Fácil)

**Windows (PowerShell):**
```powershell
.\run_agentos.ps1
```

**Windows (CMD):**
```cmd
run_agentos.bat
```

#### Opção 2: Manual

1. Configure a variável de ambiente:
```powershell
$env:OPENAI_API_KEY="sua_chave_aqui"
```

2. Execute o AgentOS:
```powershell
python .\agentos_local.py
```

#### Acessar o Sistema

Após iniciar, o AgentOS estará disponível em:
- **Interface Web (Playground)**: http://localhost:7777
- **API Docs (Swagger)**: http://localhost:7777/docs
- **Configuração**: http://localhost:7777/config

Você pode usar o playground da Agno para testar workflows, agentes e ver histórico de sessões.

### Sistema de Pré-Venda (CLI)
```powershell
python .\presales_workflow.py
```

### Time de Vendas
```powershell
python .\sales_team.py
```

## Sistema de Pré-Venda

Sistema inteligente com **Router** que direciona leads para agentes especializados baseado na intenção.

### Agentes Especializados

1. **Lead Qualifier** - Qualifica leads e determina fit
   - Ferramentas: Pesquisa web (DuckDuckGo), Reasoning, Memória
   - Avalia fit com ICP, BANT, score de qualificação

2. **Information Collector** - Coleta informações para agendamento
   - Ferramentas: Pesquisa web, Web scraping (Newspaper4k), Reasoning, Memória
   - Pesquisa empresa, decisores, contexto para reunião

3. **Closer** - Fecha negócios e negocia
   - Ferramentas: Reasoning, Memória
   - Estratégia de fechamento, tratamento de objeções

### Funcionalidades

- ✅ **Router Inteligente**: Roteia automaticamente para o agente correto
- ✅ **Pesquisa Web**: Busca informações atualizadas
- ✅ **Web Scraping**: Extrai conteúdo detalhado de artigos
- ✅ **Reasoning**: Pensamento estratégico e análise aprofundada
- ✅ **Memória Persistente**: Lembra interações anteriores com leads
- ✅ **Histórico Compartilhado**: Agentes compartilham contexto do workflow

### Exemplos de Queries

**Qualificação:**
- "Qualifique este lead: João Silva, CEO da TechCorp, empresa SaaS B2B"
- "Qual é o fit deste prospect com nosso ICP?"

**Coleta de Informações:**
- "Colete informações sobre a empresa TechCorp para agendarmos uma reunião"
- "Preciso pesquisar sobre o decisor e a empresa antes da reunião"

**Fechamento:**
- "Ajude-me a fechar este negócio com TechCorp"
- "Como tratar objeções de preço e preparar proposta?"

## Time de Vendas

Time coordenado de 4 agentes especializados:

- **SDR**: Prospecção e qualificação inicial de leads
- **Pesquisador de Conta**: Pesquisa profunda de conta e decisores
- **Outreach**: Escrita de email frio e sequência de follow-ups
- **CRM Updater**: Registro estruturado de contatos, notas e próximos passos

Os agentes trabalham em coordenação através da classe `Team` do Agno.

## Estrutura

```
agentos_local.py     # AgentOS local com playground (EXECUTAR ESTE)
presales_workflow.py  # Sistema de pré-venda com Router (CLI)
sales_team.py        # Time de agentes coordenado
requirements.txt      # Dependências
README.md            # Este arquivo
```

## Uso no Playground da Agno

1. Copie o código de `presales_workflow.py` ou `sales_team.py` para o playground
2. O sistema está pronto para usar com as queries de exemplo acima

## Personalização

Você pode modificar as instruções de cada agente nos arquivos correspondentes para ajustar o comportamento conforme suas necessidades.
