"""
AgentOS Local - Sistema de Pré-Venda
Executa o sistema de pré-venda localmente usando AgentOS (playground da Agno)
Acesse em: http://localhost:7777
"""

from textwrap import dedent
from typing import List

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.reasoning import ReasoningTools
from agno.workflow.router import Router
from agno.workflow.step import Step
from agno.workflow.types import StepInput
from agno.workflow.workflow import Workflow

# Database para persistência de sessões e memória
db = SqliteDb(db_file="tmp/presales_workflow.db")

# ==================== AGENTES ESPECIALIZADOS ====================

# 1. Lead Qualifier - Qualifica leads e determina fit
lead_qualifier = Agent(
    name="Lead Qualifier",
    model=OpenAIChat(id="gpt-5-mini"),
    db=db,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web
        ReasoningTools(add_instructions=True),  # Pensamento/raciocínio
    ],
    enable_agentic_memory=True,  # Memória para lembrar interações
    instructions=dedent("""
        Você é um especialista em qualificação de leads B2B.
        
        Suas responsabilidades:
        1. QUALIFICAÇÃO:
           - Avalie fit do lead com ICP (Ideal Customer Profile)
           - Identifique budget, authority, need, timeline (BANT)
           - Determine score de qualificação (1-10)
           - Use pesquisa web para validar informações da empresa
        
        2. RACIOCÍNIO:
           - Use ferramentas de reasoning para pensar cuidadosamente sobre cada lead
           - Analise sinais de intenção e urgência
           - Identifique pain points e necessidades
        
        3. MEMÓRIA:
           - Lembre-se de interações anteriores com o lead
           - Mantenha histórico de qualificações e scores
        
        4. OUTPUT:
           - Score de qualificação (1-10)
           - Fit com ICP (Sim/Não/Parcial)
           - BANT completo
           - Recomendação: Qualificar / Desqualificar / Mais informações necessárias
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 2. Information Collector - Coleta informações para agendamento
information_collector = Agent(
    name="Information Collector",
    model=OpenAIChat(id="gpt-5-mini"),
    db=db,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web básica
        Newspaper4kTools(),  # Web scraping para artigos
        ReasoningTools(add_instructions=True),  # Pensamento aprofundado
    ],
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um coletor de informações especializado em preparar dados para reuniões de vendas.
        
        Suas responsabilidades:
        1. PESQUISA APROFUNDADA:
           - Pesquise a empresa do lead (histórico, produtos, notícias recentes)
           - Identifique decisores e estrutura organizacional
           - Colete informações sobre concorrentes e mercado
           - Use web scraping para extrair conteúdo detalhado de artigos
        
        2. COLETA DE INFORMAÇÕES:
           - Levante informações sobre budget, timeline, processo de compra
           - Identifique dores e necessidades específicas
           - Colete informações sobre tecnologia e stack atual
           - Pesquise notícias e eventos recentes da empresa
        
        3. RACIOCÍNIO:
           - Use reasoning tools para analisar informações coletadas
           - Identifique oportunidades e pontos de conexão
           - Estruture informações de forma lógica para a reunião
        
        4. OUTPUT:
           - Resumo executivo da empresa
           - Perfil do decisor (se identificado)
           - Informações de contexto para agendamento
           - Pontos de discussão sugeridos
           - Notícias e eventos relevantes
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 3. Closer - Fecha negócios e negocia
closer = Agent(
    name="Closer",
    model=OpenAIChat(id="gpt-5-mini"),
    db=db,
    tools=[
        ReasoningTools(add_instructions=True),  # Pensamento estratégico
    ],
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um closer experiente especializado em fechar negócios B2B.
        
        Suas responsabilidades:
        1. ANÁLISE ESTRATÉGICA:
           - Use reasoning tools para pensar estrategicamente sobre cada negociação
           - Analise objeções e contra-argumentos
           - Identifique pontos de alavancagem e urgência
        
        2. NEGOCIAÇÃO:
           - Prepare argumentos de valor personalizados
           - Identifique e trate objeções comuns
           - Sugira estratégias de fechamento apropriadas
           - Proponha próximos passos e compromissos
        
        3. MEMÓRIA:
           - Lembre-se de interações anteriores com o lead
           - Mantenha histórico de negociações e propostas
           - Acompanhe estágio do funil e próximos passos
        
        4. OUTPUT:
           - Estratégia de fechamento recomendada
           - Argumentos de valor personalizados
           - Tratamento de objeções
           - Próximos passos e compromissos sugeridos
           - Probabilidade de fechamento (%)
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# ==================== STEPS DO WORKFLOW ====================

qualify_step = Step(
    name="Qualificar Lead",
    agent=lead_qualifier,
    description="Qualifica o lead e determina fit com ICP",
    add_workflow_history=True,
)

collect_info_step = Step(
    name="Coletar Informações",
    agent=information_collector,
    description="Coleta informações detalhadas para agendamento",
    add_workflow_history=True,
)

close_step = Step(
    name="Fechar Negócio",
    agent=closer,
    description="Prepara estratégia de fechamento e negociação",
    add_workflow_history=True,
)

# ==================== ROUTER ====================

def presales_router(step_input: StepInput) -> List[Step]:
    """
    Router inteligente que direciona leads para o agente apropriado
    baseado na intenção e estágio do funil.
    """
    message = step_input.input or ""
    message_lower = message.lower()
    
    # Palavras-chave para qualificação
    qualification_keywords = [
        "qualificar", "qualificação", "qualifica", "fit", "icp", "bant",
        "score", "avaliar", "lead", "prospect", "novo lead", "potencial cliente"
    ]
    
    # Palavras-chave para coleta de informações
    collection_keywords = [
        "coletar", "coleta", "informações", "pesquisa", "pesquisar",
        "agendar", "agendamento", "reunião", "preparar", "preparação",
        "contexto", "dados", "empresa", "decisor", "pesquisar empresa"
    ]
    
    # Palavras-chave para fechamento
    closing_keywords = [
        "fechar", "fechamento", "negociar", "negociação", "proposta",
        "objeção", "objeções", "fechar negócio", "contrato", "fechar venda",
        "apresentação comercial", "demo", "demonstração"
    ]
    
    # Lógica de roteamento
    if any(keyword in message_lower for keyword in qualification_keywords):
        return [qualify_step]
    elif any(keyword in message_lower for keyword in collection_keywords):
        return [collect_info_step]
    elif any(keyword in message_lower for keyword in closing_keywords):
        return [close_step]
    else:
        # Padrão: começar com qualificação
        return [qualify_step]

# ==================== WORKFLOW ====================

presales_workflow = Workflow(
    name="Sistema de Pré-Venda",
    description="Workflow inteligente para qualificação, coleta de informações e fechamento",
    db=db,
    steps=[
        Router(
            name="Presales Router",
            selector=presales_router,
            choices=[qualify_step, collect_info_step, close_step],
            description="Roteia leads para o agente apropriado baseado na intenção",
        )
    ],
    add_workflow_history_to_steps=True,  # Compartilha histórico entre agentes
)

# ==================== AGENTOS ====================

# Criar AgentOS com o workflow de pré-venda
agent_os = AgentOS(
    name="Sistema de Pré-Venda",
    description="Sistema inteligente de pré-venda com agentes especializados para qualificação, coleta de informações e fechamento",
    workflows=[presales_workflow],
    agents=[lead_qualifier, information_collector, closer],  # Também disponíveis individualmente
)

# Obter app FastAPI
app = agent_os.get_app()

# ==================== EXECUTAR ====================

if __name__ == "__main__":
    print("Iniciando AgentOS - Sistema de Pre-Venda")
    print("=" * 70)
    print("\nAcesse o playground da Agno em:")
    print("   - Interface: http://localhost:7777")
    print("   - API Docs: http://localhost:7777/docs")
    print("   - Config: http://localhost:7777/config")
    print("\nPressione Ctrl+C para parar o servidor\n")
    
    # Servir o AgentOS na porta 7777
    agent_os.serve(
        app="agentos_local:app",
        host="localhost",
        port=7777,
        reload=False,  # Desabilitar reload para evitar problemas
    )

