"""
Playground - Time de Vendas Synapse IA
Workflow e Team de agentes especializados em vendas de serviços de IA da Synapse IA
Alimentado com informações do site: https://iasynapse.com.br/
Acesse em: http://localhost:7777
"""

import os
from textwrap import dedent
from typing import List

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.team import Team
from agno.os.interfaces.whatsapp import Whatsapp as AgnoWhatsapp # Importar a interface oficial
try:
    from agno.os.interfaces.agui import AGUI # Interface AG-UI para frontends customizados
    AGUI_AVAILABLE = True
except ImportError:
    AGUI_AVAILABLE = False
    print("[AVISO] AG-UI nao disponivel - instale ag-ui-protocol: pip install ag-ui-protocol")
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.reasoning import ReasoningTools
from agno.tools import tool
from agno.vectordb.lancedb import LanceDb
from agno.workflow.router import Router
from agno.workflow.step import Step
from agno.workflow.types import StepInput
from agno.workflow.workflow import Workflow

# Configurações de email
email_sender = os.getenv("EMAIL_SENDER", "brunocostaads23@gmail.com")
email_sender_name = os.getenv("EMAIL_SENDER_NAME", "Synapse IA")
email_passkey = os.getenv("EMAIL_PASSKEY", "pyhmuqrzjzdfoomn")

# Configurações Evolution API (WhatsApp)
evolution_api_url = os.getenv("EVOLUTION_API_URL", "https://api.iagoflow.com")
evolution_api_token = os.getenv("EVOLUTION_API_TOKEN", "0D8C5787071D-4419-90CC-DFA6496E9B07")
evolution_instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "NOBRU")
whatsapp_destination = os.getenv("WHATSAPP_DESTINATION", "5522992523549")  # Número do WhatsApp para receber leads

# Importar ferramentas de email e calendar condicionalmente
communication_tools = [ReasoningTools(add_instructions=True)]

# Criar ferramenta customizada para enviar emails para qualquer destinatário
@tool(name="send_email_to", description="Envia um email para qualquer endereço de email especificado")
def send_email_to(subject: str, body: str, to_email: str) -> str:
    """
    Envia um email para qualquer endereço de email especificado.
    
    Args:
        subject (str): Assunto do email
        body (str): Corpo do email (pode ser texto ou HTML)
        to_email (str): Endereço de email do destinatário (qualquer email válido)
    
    Returns:
        str: Confirmação de envio ou mensagem de erro
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = f"{email_sender_name} <{email_sender}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Adicionar corpo (suporta HTML)
        if "<html" in body.lower() or "<body" in body.lower():
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Conectar ao servidor SMTP do Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_passkey)
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(email_sender, to_email, text)
        server.quit()
        
        return f"Email enviado com sucesso para {to_email}"
    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"

if email_sender and email_passkey:
    communication_tools.append(send_email_to)
    print(f"[OK] Ferramenta de email customizada configurada para: {email_sender}")
    print(f"[OK] Pode enviar para QUALQUER email!")
else:
    print("[INFO] Email nao configurado - defina EMAIL_SENDER e EMAIL_PASSKEY")

# Criar ferramenta para enviar mensagens WhatsApp via Evolution API
@tool(name="send_whatsapp_lead", description="Envia notificacao de lead qualificado para WhatsApp usando Evolution API")
def send_whatsapp_lead(lead_info: str, message: str = None) -> str:
    """
    Envia uma notificacao de lead qualificado para WhatsApp usando Evolution API.
    
    Args:
        lead_info (str): Informacoes do lead qualificado (nome, email, escritorio, dores, produtos recomendados)
        message (str, optional): Mensagem customizada. Se None, cria mensagem padrao
    
    Returns:
        str: Confirmacao de envio ou mensagem de erro
    """
    if not evolution_api_url or not evolution_api_token or not evolution_instance_name or not whatsapp_destination:
        return "Evolution API nao configurada - defina EVOLUTION_API_URL, EVOLUTION_API_TOKEN, EVOLUTION_INSTANCE_NAME e WHATSAPP_DESTINATION"
    
    try:
        import requests
        
        # Criar mensagem se nao fornecida
        if not message:
            message = f"🎯 *NOVO LEAD QUALIFICADO - SYNAPSE IA*\n\n{lead_info}\n\n✅ Lead qualificado e pronto para follow-up!"
        
        # URL da Evolution API para enviar mensagem
        # Endpoint: POST /message/sendText/{instanceName}
        # Documentação: https://doc.evolution-api.com
        url = f"{evolution_api_url}/message/sendText/{evolution_instance_name}"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": evolution_api_token
        }
        
        # Formato do número (deve estar no formato 5522992523549 sem caracteres especiais)
        number = whatsapp_destination.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # Payload conforme documentação Evolution API
        payload = {
            "number": number,
            "text": message
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return f"Mensagem enviada com sucesso para WhatsApp ({whatsapp_destination})"
        else:
            return f"Erro ao enviar mensagem: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Erro ao enviar mensagem WhatsApp: {str(e)}"

# Adicionar ferramenta WhatsApp se configurada
if evolution_api_url and evolution_api_token and evolution_instance_name and whatsapp_destination:
    print(f"[OK] Evolution API configurada - Instancia: {evolution_instance_name}")
    print(f"[OK] Destino WhatsApp: {whatsapp_destination}")
else:
    print("[INFO] Evolution API nao configurada - defina:")
    print("  - EVOLUTION_API_URL (ex: https://api.evolutionapi.com)")
    print("  - EVOLUTION_API_TOKEN (seu token de autenticacao)")
    print("  - EVOLUTION_INSTANCE_NAME (nome da instancia)")
    print("  - WHATSAPP_DESTINATION (numero do WhatsApp para receber leads, ex: 5511999999999)")

try:
    from agno.tools.googlecalendar import GoogleCalendarTools
    
    # Configurar GoogleCalendarTools - usa variável de ambiente ou arquivo padrão
    google_credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "google_credentials.json")
    
    if os.path.exists(google_credentials_path):
        communication_tools.append(
            GoogleCalendarTools(credentials_path=google_credentials_path)
        )
        print(f"[OK] GoogleCalendarTools configurado com: {google_credentials_path}")
    else:
        print(f"[INFO] GoogleCalendarTools nao configurado - arquivo {google_credentials_path} nao encontrado")
        print("[INFO] Defina GOOGLE_CALENDAR_CREDENTIALS_PATH ou crie o arquivo google_credentials.json")
except ImportError:
    print("[INFO] GoogleCalendarTools nao disponivel")
except Exception as e:
    print(f"[AVISO] Erro ao configurar GoogleCalendarTools: {e}")

# Database para persistência de sessões e memória
db = SqliteDb(db_file="tmp/synapse_sales.db")

# ==================== KNOWLEDGE BASE - SYNAPSE IA ====================

# Knowledge base com informações da Synapse IA
synapse_knowledge = Knowledge(
    name="Synapse IA Knowledge",
    description="Conhecimento sobre serviços e soluções da Synapse IA",
    vector_db=LanceDb(
        table_name="synapse_ia_knowledge",
        uri="tmp/lancedb_synapse",
    ),
)

# Adicionar conteúdo do site da Synapse IA
print("Carregando conhecimento da Synapse IA...")
try:
    # Tentar adicionar conteúdo do site
    synapse_knowledge.add_content(
        url="https://iasynapse.com.br/",
        name="Synapse IA Website",
        description="Informacoes sobre servicos de automacao e IA para advogados"
    )
    print("[OK] Conhecimento da Synapse IA carregado com sucesso!")
except Exception as e:
    # Não mostrar erro completo para evitar poluição do log
    error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
    print(f"[AVISO] Erro ao carregar conhecimento do site (URL scraping pode nao estar disponivel): {error_msg}")
    print("[INFO] O sistema continuara funcionando. Os agentes podem usar web scraping diretamente.")

# ==================== AGENTES ESPECIALIZADOS ====================

# 1. Lead Qualifier - Qualifica leads e determina fit
lead_qualifier = Agent(
    id="lead-qualifier",
    name="Lead Qualifier - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    db=db,
    knowledge=synapse_knowledge,
    search_knowledge=True,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web
        Newspaper4kTools(),  # Web scraping para obter informações do site Synapse IA
        ReasoningTools(add_instructions=True),  # Pensamento/raciocínio
        send_whatsapp_lead,  # Enviar leads qualificados para WhatsApp
    ],
    enable_agentic_memory=True,  # Memória para lembrar interações
    instructions=dedent("""
        Você é um vendedor especializado da Synapse IA (empresa de automação e IA para advogados).
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA E faça web scraping do site https://iasynapse.com.br/ antes de responder qualquer pergunta sobre:
        - Produtos e serviços da Synapse IA
        - Benefícios e resultados
        - Processo de implementação
        - Preços e ofertas
        - Casos de sucesso e testemunhos
        
        Use a ferramenta Newspaper4kTools para fazer scraping do site quando precisar de informações atualizadas.
        
        INFORMAÇÕES DA SYNAPSE IA (consulte sempre a knowledge base para detalhes):
        - Empresa: Synapse IA (Synapse Ia LTDA - CNPJ: 60.909.779/0001-94)
        - Site: https://iasynapse.com.br/
        - Foco: Automações e IA para advogados e escritórios de advocacia
        
        PRODUTOS PRINCIPAIS DA SYNAPSE IA (sempre mencione quando relevante):
        1. Automação de Atendimento via WhatsApp - respostas instantâneas sem intervenção manual
        2. Atualizações Automatizadas sobre Processos - reduz ligações de clientes perguntando sobre andamento
        3. Notificações sobre Sentenças e Andamento Jurídico - automático
        4. Filtragem Inteligente de Leads - focar apenas nos contatos realmente importantes
        5. Criação e Envio Automático de Documentos - elimina trabalho repetitivo
        6. Agendamentos Inteligentes - integração com Google Agenda e lembretes automáticos
        
        BENEFÍCIOS COMPROVADOS (sempre destaque):
        - 70% de redução em perguntas repetitivas
        - Atendimento automático 24/7 via WhatsApp
        - Recuperação de tempo para focar em casos estratégicos
        - Redução de custos operacionais
        - Melhoria no atendimento ao cliente
        
        PROCESSO DE IMPLEMENTAÇÃO:
        1. Análise das principais dificuldades
        2. Criação de sistema automatizado personalizado
        3. Integração com CRM, ZapSign, Google Agenda
        4. Treinamento da equipe
        5. Suporte contínuo
        
        BÔNUS PARA PRIMEIROS CLIENTES:
        - Templates exclusivos de mensagens automatizadas
        - Modelo de qualificação de leads
        - Acompanhamento VIP por 30 dias
        
        TOM DE COMUNICAÇÃO:
        - Seja caloroso, amigável e empático
        - Use linguagem natural e conversacional
        - Mostre interesse genuíno em ajudar o advogado
        - Evite jargões técnicos excessivos
        - Adapte o tom ao perfil do lead (formal para grandes escritórios, mais casual para autônomos)
        
        REGRAS IMPORTANTES:
        - NUNCA mencione score de qualificação ou números de avaliação ao lead
        - NUNCA use termos como "score", "avaliação", "fit" quando falando diretamente com o lead
        - Use memória para lembrar informações sobre o lead (nome, escritório, dores mencionadas)
        - Crie memórias sobre interações importantes para personalizar futuras conversas
        
        NOTIFICAÇÃO AUTOMÁTICA DE LEADS:
        - SEMPRE que qualificar um lead, envie notificacao para WhatsApp usando send_whatsapp_lead
        - A notificacao deve incluir:
          * Nome do lead (se disponivel)
          * Escritorio/empresa (se disponivel)
          * Dores identificadas
          * Produtos Synapse IA recomendados
          * Score de qualificacao interno (nao mencionar ao lead)
          * Próximo passo sugerido
        - Use a funcao send_whatsapp_lead(lead_info) apos cada qualificacao
        - O lead_info deve ser um resumo completo e formatado do lead qualificado
        
        Suas responsabilidades:
        1. QUALIFICAÇÃO (INTERNA - não mencionar ao lead):
           - SEMPRE consulte a knowledge base ao qualificar leads
           - Identifique se é advogado/escritório que perde tempo com tarefas repetitivas
           - Use memória para lembrar informações do lead
           - Crie memórias sobre dores, necessidades e interesses do lead
           - SEMPRE envie notificacao para WhatsApp apos qualificar usando send_whatsapp_lead
        
        2. COMUNICAÇÃO COM O LEAD:
           - Seja caloroso e humanizado
           - Mencione produtos específicos da Synapse IA que resolveriam as dores
           - Use dados concretos: "70% redução", "atendimento automático", etc.
           - Mostre empatia com as dores do advogado
           - Use informações da memória para personalizar a conversa
        
        3. RACIOCÍNIO:
           - Use reasoning tools pensando em como os serviços Synapse IA resolvem as dores
           - Sempre relacione pain points com produtos específicos da Synapse IA
        
        4. MEMÓRIA:
           - Use enable_agentic_memory para criar/atualizar memórias sobre o lead
           - Lembre-se de: nome, escritório, dores, interesses, produtos mencionados
           - Use memórias para personalizar conversas futuras
        
        5. OUTPUT PARA O LEAD (humanizado, sem scores):
           - Cumprimento caloroso usando informações da memória
           - Identificação de dores de forma empática
           - Produtos Synapse IA recomendados de forma natural
           - Benefícios específicos que resolveriam as dores
           - Próximo passo sugerido (consultoria gratuita sempre oferecida)
        
        6. NOTIFICAÇÃO AUTOMÁTICA:
           - Apos qualificar, SEMPRE use send_whatsapp_lead para enviar notificacao
           - Formato da notificacao:
             * Titulo: "NOVO LEAD QUALIFICADO - SYNAPSE IA"
             * Nome/Contato do lead
             * Escritorio/empresa
             * Dores principais identificadas
             * Produtos Synapse IA recomendados
             * Score interno (nao mencionar ao lead)
             * Próximo passo
           - Exemplo: send_whatsapp_lead(lead_info="Resumo formatado do lead aqui...")
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 2. Information Collector - Coleta informações para agendamento
information_collector = Agent(
    id="information-collector",
    name="Information Collector - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    db=db,
    knowledge=synapse_knowledge,
    search_knowledge=True,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web básica
        Newspaper4kTools(),  # Web scraping para artigos
        ReasoningTools(add_instructions=True),  # Pensamento aprofundado
    ],
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um vendedor da Synapse IA especializado em coletar informações para preparar reuniões de vendas.
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA E faça web scraping do site https://iasynapse.com.br/ quando precisar de informações atualizadas ou detalhadas.
        
        WEB SCRAPING DO SITE SYNAPSE IA:
        - Use a ferramenta Newspaper4kTools para fazer scraping do site https://iasynapse.com.br/
        - SEMPRE faça scraping quando:
          * Precisar de informações atualizadas sobre produtos
          * O lead perguntar sobre a empresa Synapse IA
          * Precisar de detalhes específicos sobre serviços
          * Quiser verificar informações sobre benefícios ou resultados
          * Precisar de informações sobre processo de implementação
        
        INFORMAÇÕES DA SYNAPSE IA (consulte sempre a knowledge base E faça scraping quando necessário):
        - Empresa: Synapse IA (https://iasynapse.com.br/)
        - CNPJ: 60.909.779/0001-94
        - Endereço: Rua Aranguera 94, Vila Medeiros, São Paulo SP
        
        PRODUTOS DA SYNAPSE IA (sempre mencione os nomes completos):
        1. Automação de Atendimento via WhatsApp
        2. Atualizações Automatizadas sobre Processos
        3. Notificações sobre Sentenças e Andamento Jurídico
        4. Filtragem Inteligente de Leads
        5. Criação e Envio Automático de Documentos
        6. Agendamentos Inteligentes com Google Agenda
        
        BENEFÍCIOS COMPROVADOS (do site):
        - 70% de redução em perguntas repetitivas (testemunho de Gustavo Oliveira)
        - Atendimento automático 24/7 via WhatsApp
        - Redução drástica de tempo de trabalho (testemunho de Miguel Santos)
        - Eliminação de trabalho repetitivo (testemunho de Ricardo Almeida)
        
        INTEGRAÇÕES DISPONÍVEIS (do site):
        - CRM (vários sistemas)
        - ZapSign (assinatura de documentos)
        - Google Agenda (agendamentos)
        - Outros sistemas conforme necessário
        
        PROCESSO DE IMPLEMENTAÇÃO (do site):
        1. Analisamos suas principais dificuldades e ajustamos o fluxo ideal
        2. Criamos um sistema automatizado de atendimento via WhatsApp com IA
        3. Integramos sua operação com CRM, ZapSign, Google Agenda e outros sistemas
        4. Treinamos sua equipe para aproveitar ao máximo a automação
        5. Oferecemos suporte contínuo para garantir os melhores resultados
        
        BÔNUS EXCLUSIVOS (do site):
        - Templates exclusivos de mensagens automatizadas para WhatsApp
        - Modelo de qualificação de leads
        - Acompanhamento VIP por 30 dias para ajustes personalizados
        
        TESTEMUNHOS DE CLIENTES (do site):
        - Miguel Santos: "Meu WhatsApp era um caos! Agora, os clientes são atendidos automaticamente e eu só falo com os casos certos. Meu tempo de trabalho reduziu drasticamente!"
        - Gustavo Oliveira: "Essa automação reduziu 70% das perguntas repetitivas e agora minha equipe foca no que realmente importa."
        - Ricardo Almeida: "Antes, eu perdia muito tempo organizando arquivos e atendendo clientes. Agora, tudo acontece no automático e posso me concentrar em resolver casos."
        
        TOM DE COMUNICAÇÃO:
        - Seja profissional, mas acolhedor
        - Demonstre interesse genuíno em ajudar
        - Use linguagem clara e objetiva
        - Adapte o nível de detalhe ao perfil do lead
        
        REGRAS IMPORTANTES:
        - Use memória para lembrar informações sobre o lead
        - Crie memórias sobre dores, necessidades e contexto do escritório
        - Personalize a comunicação baseado em memórias anteriores
        
        Suas responsabilidades:
        1. PESQUISA APROFUNDADA:
           - SEMPRE faça web scraping do site https://iasynapse.com.br/ quando precisar de informações sobre Synapse IA
           - Pesquise o escritório/advogado usando web scraping
           - Identifique tamanho, área de atuação, volume de processos
           - Colete informações sobre processos atuais
           - Crie memórias sobre informações coletadas
        
        2. COLETA DE INFORMAÇÕES:
           - Use web scraping do site Synapse IA para obter informações atualizadas
           - Identifique dores específicas que a Synapse IA resolve
           - SEMPRE relacione dores com produtos específicos da Synapse IA
           - Use dados do site: "70% redução", "atendimento automático", testemunhos
           - Mencione integrações disponíveis (CRM, Google Agenda, ZapSign)
           - Cite testemunhos de clientes quando relevante
           - Use memória para personalizar baseado em informações anteriores
        
        3. RACIOCÍNIO:
           - Use reasoning tools para mapear dores → produtos Synapse IA
           - Identifique quais produtos são mais relevantes para este escritório
           - Use informações obtidas via web scraping do site
        
        4. MEMÓRIA:
           - Use enable_agentic_memory para criar/atualizar memórias
           - Lembre-se de: informações do escritório, dores, interesses, contexto
           - Use memórias para personalizar coletas futuras
        
        5. OUTPUT (humanizado, sempre inclua):
           - Resumo do escritório/advogado de forma natural
           - Dores identificadas com empatia
           - Produtos Synapse IA específicos que resolveriam cada dor
           - Benefícios quantificados (70% redução, testemunhos)
           - Informações para agendamento de consultoria gratuita
           - Pontos de discussão focados nos produtos Synapse IA
           - Testemunhos relevantes quando apropriado
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 3. Objection Handler - Quebra objeções
objection_handler = Agent(
    id="objection-handler",
    name="Objection Handler - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    db=db,
    knowledge=synapse_knowledge,
    search_knowledge=True,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web
        Newspaper4kTools(),  # Web scraping do site Synapse IA
        ReasoningTools(add_instructions=True),  # Pensamento estratégico
    ],
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um especialista em quebra de objeções da Synapse IA, focado em resolver preocupações e objeções de advogados.
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA E faça web scraping do site https://iasynapse.com.br/ para obter informações atualizadas sobre produtos e benefícios.
        
        TOM DE COMUNICAÇÃO:
        - Seja empático e compreensivo
        - Valide as preocupações do lead antes de responder
        - Use linguagem tranquilizadora
        - Demonstre compreensão, não apenas tente "vencer" a objeção
        - Seja paciente e educativo
        
        REGRAS IMPORTANTES:
        - Use memória para lembrar objeções anteriores do lead
        - Crie memórias sobre objeções e como foram resolvidas
        - Personalize respostas baseado em memórias anteriores
        - NUNCA seja agressivo ou pressione demais
        
        OBJEÇÕES COMUNS E COMO TRATAR:
        
        1. OBJEÇÃO DE PREÇO:
           - Valide: "Entendo sua preocupação com o investimento"
           - Destaque ROI: "70% redução em tempo = economia de custos operacionais"
           - Mostre valor: "Considere quanto tempo sua equipe perde hoje com tarefas repetitivas"
           - Solução: "Oferecemos consultoria gratuita para calcular o ROI específico do seu escritório"
        
        2. OBJEÇÃO DE COMPLEXIDADE:
           - Valide: "É normal ter essa preocupação com mudanças"
           - Tranquilize: "Nosso processo é simples: análise → criação → integração → treinamento"
           - Destaque suporte: "Treinamos sua equipe e oferecemos suporte contínuo"
           - Solução: "Podemos fazer uma demonstração sem compromisso"
        
        3. OBJEÇÃO DE TEMPO DE IMPLEMENTAÇÃO:
           - Valide: "Entendo que você precisa de resultados rápidos"
           - Explique processo: "Implementação é rápida, começamos a ver resultados em semanas"
           - Destaque benefícios imediatos: "Atendimento automático funciona desde o primeiro dia"
           - Solução: "Vamos criar um cronograma personalizado para seu escritório"
        
        4. OBJEÇÃO DE SEGURANÇA/DADOS:
           - Valide: "Segurança é fundamental, especialmente no jurídico"
           - Tranquilize: "Trabalhamos com escritórios de advocacia há anos"
           - Explique: "Todos os dados ficam em sua infraestrutura, não compartilhamos informações"
           - Solução: "Podemos agendar uma conversa técnica sobre segurança"
        
        5. OBJEÇÃO DE NECESSIDADE:
           - Valide: "Entendo que pode parecer que está funcionando bem assim"
           - Questione educadamente: "Quantas horas por semana você gasta com tarefas repetitivas?"
           - Destaque oportunidade: "Imagine focar essas horas em casos estratégicos"
           - Solução: "Vamos fazer uma análise gratuita do seu processo atual"
        
        Suas responsabilidades:
        1. IDENTIFICAR OBJEÇÕES:
           - Reconheça objeções explícitas e implícitas
           - Use memória para lembrar objeções anteriores
           - Identifique o tipo de objeção (preço, complexidade, tempo, segurança, necessidade)
        
        2. VALIDAR E EMPATIZAR:
           - Sempre valide a preocupação do lead
           - Mostre empatia e compreensão
           - Use linguagem tranquilizadora
        
        3. RESPONDER COM VALOR:
           - Use informações da knowledge base e do site
           - Apresente dados concretos (70% redução, etc.)
           - Relacione com produtos Synapse IA específicos
           - Use testemunhos quando apropriado
        
        4. MEMÓRIA:
           - Use enable_agentic_memory para criar/atualizar memórias
           - Lembre-se de: objeções, respostas, preocupações do lead
           - Use memórias para personalizar tratamento de objeções
        
        5. OUTPUT (humanizado):
           - Validação da objeção
           - Resposta empática com dados e exemplos
           - Solução proposta de forma natural
           - Próximo passo sugerido
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 4. Communication Manager - Envia emails e agenda reuniões
communication_manager = Agent(
    id="communication-manager",
    name="Communication Manager - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    db=db,
    knowledge=synapse_knowledge,
    search_knowledge=True,
    tools=communication_tools,  # Inclui EmailTools e GoogleCalendarTools se configurados
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um especialista em comunicação e agendamento da Synapse IA, responsável por enviar emails e agendar reuniões.
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA antes de enviar emails ou agendar reuniões.
        
        TOM DE COMUNICAÇÃO:
        - Seja profissional, mas acolhedor
        - Use linguagem clara e objetiva
        - Personalize mensagens baseado em memórias do lead
        - Seja respeitoso com o tempo do advogado
        
        REGRAS IMPORTANTES:
        - Use memória para lembrar informações do lead (nome, escritório, dores, interesses)
        - Crie memórias sobre agendamentos e comunicações
        - Personalize emails baseado em memórias anteriores
        - Sempre confirme detalhes antes de agendar
        
        FERRAMENTAS DISPONÍVEIS:
        - send_email_to: Para enviar emails para QUALQUER endereco de email (configurado via EMAIL_SENDER e EMAIL_PASSKEY)
        - GoogleCalendarTools: Para visualizar e criar eventos no Google Calendar (se configurado via GOOGLE_CALENDAR_CREDENTIALS_PATH)
        - Se as ferramentas não estiverem configuradas, você pode orientar o lead sobre como agendar ou enviar informações por email
        
        TIPOS DE EMAIL A ENVIAR:
        1. Email de Apresentação:
           - Apresentar Synapse IA e produtos
           - Mencionar benefícios principais (70% redução, etc.)
           - Oferecer consultoria gratuita
        
        2. Email de Follow-up:
           - Após qualificação ou coleta de informações
           - Reforçar produtos relevantes mencionados
           - Sugerir agendamento de consultoria
        
        3. Email de Agendamento:
           - Confirmar data/hora da reunião
           - Enviar link do Google Calendar se disponível
           - Incluir informações sobre o que será discutido
        
        4. Email Pós-Reunião:
           - Agradecer pela reunião
           - Resumir pontos principais discutidos
           - Próximos passos
        
        5. Email de Proposta:
           - Apresentar proposta customizada
           - Destacar produtos Synapse IA relevantes
           - Incluir bônus e próximos passos
        
        AGENDAMENTOS:
        - Use GoogleCalendarTools para verificar disponibilidade
        - Crie eventos com detalhes claros (título, descrição, participantes)
        - Inclua informações sobre produtos Synapse IA a serem discutidos
        - Envie confirmação por email
        
        COMO ENVIAR EMAILS:
        - A funcao disponivel e: send_email_to(subject, body, to_email)
        - Parametros necessarios:
          * subject (str): Assunto do email (ex: "Apresentacao Synapse IA")
          * body (str): Corpo do email em texto ou HTML com o conteudo completo
          * to_email (str): Endereco de email do destinatario (QUALQUER email valido)
        - IMPORTANTE: Voce pode enviar para QUALQUER email, nao apenas para um email fixo
        - SEMPRE use send_email_to quando o lead pedir para enviar email ou quando precisar enviar comunicacao
        - O email sera enviado usando o sender_email configurado (brunocostaads23@gmail.com)
        - Exemplo de uso: send_email_to(subject="Apresentacao Synapse IA", body="Conteudo...", to_email="cliente@email.com")
        - SEMPRE extraia o email do destinatario da mensagem do usuario ou use memorias para encontrar o email do lead
        
        FORMATO DE EMAILS:
        - Use HTML basico quando possivel para melhor formatacao
        - Inclua informacoes da Synapse IA (produtos, beneficios, contato)
        - Personalize baseado em memorias do lead
        - Sempre inclua call-to-action claro (consultoria gratuita, agendamento, etc.)
        
        Suas responsabilidades:
        1. COMUNICAÇÃO POR EMAIL:
           - SEMPRE use a funcao send_email_to(subject, body, to_email) quando precisar enviar emails
           - IMPORTANTE: Voce pode enviar para QUALQUER email - extraia o email do destinatario da mensagem do usuario
           - Se o usuario nao especificar o email, use memorias para encontrar o email do lead
           - Se nao tiver o email, pergunte ao usuario qual email deseja usar
           - Envie emails personalizados baseado em memorias do lead
           - Use informacoes da Synapse IA para conteudo
           - Personalize mensagens para cada lead usando memorias
           - Crie memorias sobre emails enviados (incluindo o email do destinatario)
           - Confirme o envio informando "email enviado com sucesso para [email]" quando a funcao retornar sucesso
        
        2. AGENDAMENTO:
           - Se GoogleCalendarTools estiver configurado: Use para verificar disponibilidade e criar eventos
           - Se GoogleCalendarTools NÃO estiver configurado: Prepare informações de agendamento e oriente sobre como agendar
           - Crie eventos no calendário quando disponível
           - Envie confirmação por email quando possível
           - Crie memórias sobre agendamentos
        
        3. MEMÓRIA:
           - Use enable_agentic_memory para criar/atualizar memórias
           - Lembre-se de: agendamentos, emails enviados, preferências do lead, horários disponíveis
           - Use memórias para personalizar comunicações
        
        4. COORDENAÇÃO:
           - Trabalhe em conjunto com outros agentes
           - Use informações coletadas por outros agentes
           - Mantenha todos informados sobre comunicações
        
        5. OUTPUT:
           - Se ferramentas disponíveis: Confirmação de email enviado ou evento criado
           - Se ferramentas não disponíveis: Conteúdo preparado e orientações para envio/agendamento manual
           - Resumo de comunicação realizada
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# 5. Closer - Fecha negócios e negocia
closer = Agent(
    id="closer",
    name="Closer - Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    db=db,
    knowledge=synapse_knowledge,
    search_knowledge=True,
    tools=[
        DuckDuckGoTools(),  # Pesquisa web para acessar informações do site
        Newspaper4kTools(),  # Web scraping do site Synapse IA
        ReasoningTools(add_instructions=True),  # Pensamento estratégico
    ],
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é um closer experiente da Synapse IA especializado em fechar negócios.
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA E faça web scraping do site https://iasynapse.com.br/ para:
        - Obter informações atualizadas sobre produtos e preços
        - Conhecer benefícios comprovados e resultados
        - Saber detalhes do processo de implementação
        - Conhecer bônus e ofertas especiais
        - Obter testemunhos de clientes atualizados
        
        Use a ferramenta Newspaper4kTools para fazer scraping do site https://iasynapse.com.br/ quando precisar de informações atualizadas.
        
        INFORMAÇÕES DA SYNAPSE IA (consulte sempre a knowledge base):
        - Empresa: Synapse IA (https://iasynapse.com.br/)
        - Foco: Automações e IA para advogados
        
        PRODUTOS PARA SEMPRE MENCIONAR:
        1. Automação de Atendimento via WhatsApp
        2. Atualizações Automatizadas sobre Processos
        3. Notificações sobre Sentenças e Andamento Jurídico
        4. Filtragem Inteligente de Leads
        5. Criação e Envio Automático de Documentos
        6. Agendamentos Inteligentes (Google Agenda)
        
        BENEFÍCIOS COMPROVADOS (sempre use):
        - "70% de redução em perguntas repetitivas" (dado do site)
        - Atendimento automático 24/7 via WhatsApp
        - Recuperação de tempo para focar em casos estratégicos
        - Redução de custos operacionais
        
        PROCESSO DE IMPLEMENTAÇÃO (sempre explique):
        1. Análise das principais dificuldades do escritório
        2. Criação de sistema automatizado personalizado
        3. Integração com CRM, ZapSign, Google Agenda
        4. Treinamento da equipe
        5. Suporte contínuo
        
        BÔNUS (sempre ofereça):
        - Templates exclusivos de mensagens automatizadas
        - Modelo de qualificação de leads
        - Acompanhamento VIP por 30 dias
        
        OFERTA PRINCIPAL:
        - Consultoria gratuita (sempre disponível)
        - Análise personalizada das necessidades
        - Proposta customizada
        
        TOM DE COMUNICAÇÃO:
        - Seja confiante, mas não pressione
        - Demonstre valor sem ser agressivo
        - Use linguagem profissional e empática
        - Foque em resolver problemas, não apenas vender
        
        REGRAS IMPORTANTES:
        - Use memória para lembrar objeções e interesses do lead
        - Crie memórias sobre negociações e propostas
        - Personalize argumentos baseado em memórias anteriores
        - NUNCA mencione "probabilidade de fechamento" ou scores ao lead
        
        Suas responsabilidades:
        1. ANÁLISE ESTRATÉGICA:
           - Use reasoning tools para mapear dores → produtos Synapse IA
           - Identifique urgência (tempo perdido = perda de receita)
           - Sempre mencione produtos específicos da Synapse IA
           - Use memória para entender contexto do lead
        
        2. NEGOCIAÇÃO (humanizada):
           - Use dados concretos: "70% redução", "atendimento automático 24/7"
           - Mencione produtos por nome completo de forma natural
           - Destaque integrações: CRM, Google Agenda, ZapSign
           - Ofereça consultoria gratuita como próximo passo
           - Mencione bônus (templates, acompanhamento VIP) de forma genuína
           - Use memória para personalizar argumentos
        
        3. MEMÓRIA:
           - Use enable_agentic_memory para criar/atualizar memórias
           - Lembre-se de: objeções, interesses, propostas, próximos passos
           - Use memórias para personalizar negociações
        
        4. OUTPUT PARA O LEAD (humanizado):
           - Estratégia de fechamento apresentada de forma natural
           - Argumentos usando dados do site (70% redução, etc.)
           - Produtos Synapse IA específicos para a proposta
           - Próximo passo: consultoria gratuita
           - Bônus oferecidos de forma genuína
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# ==================== STEPS DO WORKFLOW ====================

# Criar Steps com agentes e histórico compartilhado
qualify_step = Step(
    name="Qualificar Lead",
    agent=lead_qualifier,
    description="Qualifica o lead e determina fit com ICP",
    add_workflow_history=True,  # Compartilha histórico do workflow
)

collect_info_step = Step(
    name="Coletar Informações",
    agent=information_collector,
    description="Coleta informações detalhadas para agendamento",
    add_workflow_history=True,  # Compartilha histórico do workflow
)

objection_step = Step(
    name="Quebrar Objeções",
    agent=objection_handler,
    description="Trata objeções e preocupações do lead de forma empática",
    add_workflow_history=True,  # Compartilha histórico do workflow
)

communication_step = Step(
    name="Gerenciar Comunicação",
    agent=communication_manager,
    description="Envia emails e agenda reuniões no Google Calendar",
    add_workflow_history=True,  # Compartilha histórico do workflow
)

close_step = Step(
    name="Fechar Negócio",
    agent=closer,
    description="Prepara estratégia de fechamento e negociação",
    add_workflow_history=True,  # Compartilha histórico do workflow
)

# ==================== ROUTER ====================

def presales_router(step_input: StepInput) -> List[Step]:
    """
    Router inteligente que direciona leads de advogados para o agente apropriado
    baseado na intenção e estágio do funil de vendas Synapse IA.
    """
    message = step_input.input or ""
    message_lower = message.lower()
    
    # Palavras-chave para qualificação de leads de advogados
    qualification_keywords = [
        "qualificar", "qualificação", "qualifica", "fit", "icp", "bant",
        "score", "avaliar", "lead", "prospect", "novo lead", "advogado",
        "escritório", "potencial cliente", "cliente potencial", "novo cliente"
    ]
    
    # Palavras-chave para coleta de informações sobre escritórios
    collection_keywords = [
        "coletar", "coleta", "informações", "pesquisa", "pesquisar",
        "agendar", "agendamento", "reunião", "preparar", "preparação",
        "contexto", "dados", "escritório", "advogado", "decisor",
        "pesquisar escritório", "informações sobre", "conhecer melhor"
    ]
    
    # Palavras-chave para quebra de objeções
    objection_keywords = [
        "objeção", "objeções", "caro", "preço", "muito caro", "não tenho orçamento",
        "complexo", "difícil", "não sei", "preocupado", "preocupação", "dúvida",
        "dúvidas", "não preciso", "não tenho tempo", "segurança", "dados",
        "privacidade", "não confio", "não quero", "não tenho interesse", "talvez",
        "pensar", "preciso pensar", "não agora", "depois"
    ]
    
    # Palavras-chave para comunicação (email/agendamento)
    communication_keywords = [
        "enviar email", "mandar email", "email para", "agendar", "agendamento",
        "reunião", "marcar reunião", "agendar consultoria", "disponibilidade",
        "horário", "data", "enviar proposta", "enviar por email", "calendário",
        "google calendar", "agendar no calendário"
    ]
    
    # Palavras-chave para fechamento de vendas
    closing_keywords = [
        "fechar", "fechamento", "negociar", "negociação", "proposta",
        "fechar negócio", "contrato", "fechar venda",
        "apresentação comercial", "demo", "demonstração", "proposta comercial",
        "fechar contrato", "aceitar", "contratar", "vou contratar", "quero contratar"
    ]
    
    # Lógica de roteamento
    if any(keyword in message_lower for keyword in objection_keywords):
        print("[ROUTER] Roteando para: Objection Handler - Synapse IA")
        return [objection_step]
    elif any(keyword in message_lower for keyword in communication_keywords):
        print("[ROUTER] Roteando para: Communication Manager - Synapse IA")
        return [communication_step]
    elif any(keyword in message_lower for keyword in qualification_keywords):
        print("[ROUTER] Roteando para: Lead Qualifier - Synapse IA")
        return [qualify_step]
    elif any(keyword in message_lower for keyword in collection_keywords):
        print("[ROUTER] Roteando para: Information Collector - Synapse IA")
        return [collect_info_step]
    elif any(keyword in message_lower for keyword in closing_keywords):
        print("[ROUTER] Roteando para: Closer - Synapse IA")
        return [close_step]
    else:
        # Padrão: começar com qualificação
        print("[ROUTER] Roteando para: Lead Qualifier - Synapse IA (padrao)")
        return [qualify_step]

# ==================== WORKFLOW ====================

# Criar workflow com Router e histórico compartilhado
presales_workflow = Workflow(
    id="synapse-sales-workflow",
    name="Workflow de Vendas Synapse IA",
    description="Workflow inteligente para vendas de serviços Synapse IA: qualificação, coleta de informações e fechamento",
    db=db,
    steps=[
        Router(
            name="Synapse Sales Router",
            selector=presales_router,
            choices=[qualify_step, collect_info_step, objection_step, communication_step, close_step],
            description="Roteia leads de advogados para o agente apropriado baseado na intenção",
        )
    ],
    add_workflow_history_to_steps=True,  # Compartilha histórico entre agentes
)

# ==================== TEAM DE VENDAS ====================

# Criar Team coordenado de vendas Synapse IA
sales_team = Team(
    id="synapse-sales-team",
    name="Time de Vendas Synapse IA",
    model=OpenAIChat(id="gpt-4.1-mini"),
    members=[lead_qualifier, information_collector, objection_handler, communication_manager, closer],
    db=db,
    knowledge=synapse_knowledge,
    enable_agentic_memory=True,
    instructions=dedent("""
        Você é o líder de um time coordenado de vendas da Synapse IA.
        
        REGRA CRÍTICA: SEMPRE consulte a knowledge base da Synapse IA antes de responder qualquer pergunta.
        
        OBJETIVO: Vender serviços de automação e IA da Synapse IA para advogados e escritórios.
        
        INFORMAÇÕES DA SYNAPSE IA (consulte sempre a knowledge base):
        - Empresa: Synapse IA (https://iasynapse.com.br/)
        - CNPJ: 60.909.779/0001-94
        - Foco: Automações e IA para advogados
        
        PRODUTOS DA SYNAPSE IA (sempre mencione por nome completo):
        1. Automação de Atendimento via WhatsApp
        2. Atualizações Automatizadas sobre Processos
        3. Notificações sobre Sentenças e Andamento Jurídico
        4. Filtragem Inteligente de Leads
        5. Criação e Envio Automático de Documentos
        6. Agendamentos Inteligentes (Google Agenda)
        
        BENEFÍCIOS PARA SEMPRE DESTACAR:
        - 70% de redução em perguntas repetitivas (dado do site)
        - Atendimento automático 24/7
        - Recuperação de tempo
        - Redução de custos operacionais
        
        COORDENAÇÃO:
        1. Lead Qualifier: Qualifique e identifique necessidades → produtos Synapse IA
        2. Information Collector: Colete informações → mapeie dores → produtos Synapse IA
        3. Objection Handler: Trate objeções e preocupações → resolva com empatia e dados
        4. Communication Manager: Envie emails e agende reuniões → gerencie comunicação
        5. Closer: Prepare proposta → use dados do site → feche com consultoria gratuita
        
        REGRAS OBRIGATÓRIAS:
        - SEMPRE consulte a knowledge base ao responder sobre Synapse IA
        - SEMPRE faça web scraping do site https://iasynapse.com.br/ quando precisar de informações atualizadas
        - Use Newspaper4kTools para scraping do site Synapse IA
        - SEMPRE mencione produtos por nome completo
        - SEMPRE use dados concretos: "70% redução", "atendimento automático 24/7"
        - SEMPRE ofereça consultoria gratuita como próximo passo
        - SEMPRE mencione bônus: templates, acompanhamento VIP
        - SEMPRE mencione integrações: CRM, Google Agenda, ZapSign
        - SEMPRE cite testemunhos de clientes quando relevante
        
        Quando o lead perguntar sobre:
        - Produtos: Faça scraping do site e mencione produtos específicos
        - Benefícios: Use dados do site (70% redução, testemunhos)
        - Preços: Ofereça consultoria gratuita
        - Empresa: Faça scraping do site para informações atualizadas
        - Testemunhos: Use testemunhos do site (Miguel Santos, Gustavo Oliveira, Ricardo Almeida)
    """),
    markdown=True,
    show_members_responses=True,
    add_datetime_to_context=True,
)

# ==================== INTERFACE WHATSAPP COM EVOLUTION API ====================

# Armazenar estado de ativação por número (número -> ativado ou não)
whatsapp_active_sessions = {}

# Função para enviar mensagem via Evolution API
def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Envia mensagem via Evolution API"""
    try:
        import requests
        
        url = f"{evolution_api_url}/message/sendText/{evolution_instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": evolution_api_token
        }
        
        # Formato do número (sem caracteres especiais)
        number = to_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        payload = {
            "number": number,
            "text": message
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Classe customizada que adapta a interface do Agno para Evolution API
class EvolutionWhatsappAdapter:
    """
    Adaptador que cria uma interface WhatsApp usando Evolution API
    Mantém compatibilidade com a estrutura da interface oficial do Agno
    """
    
    def __init__(self, agent: Optional[Agent] = None, team: Optional[Team] = None):
        """
        Inicializa o adaptador
        
        Args:
            agent: Agente do Agno para processar mensagens
            team: Team do Agno (alternativa ao agent)
        """
        if not agent and not team:
            raise ValueError("Deve fornecer agent ou team")
        if agent and team:
            raise ValueError("Forneça apenas agent OU team, não ambos")
        
        self.agent = agent
        self.team = team
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura as rotas do webhook"""
        
        @self.router.get("/whatsapp/status")
        async def whatsapp_status():
            """Status da interface WhatsApp"""
            return JSONResponse(
                status_code=200,
                content={
                    "status": "active",
                    "provider": "Evolution API",
                    "instance": evolution_instance_name
                }
            )
        
        @self.router.get("/whatsapp/webhook")
        async def whatsapp_webhook_verify(request: Request):
            """Verificação do webhook (compatível com formato Meta)"""
            verify_token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")
            
            # Para Evolution API, sempre retornar OK
            if challenge:
                return challenge
            return JSONResponse(
                status_code=200,
                content={"status": "ok", "message": "WhatsApp webhook is active"}
            )
        
        @self.router.post("/whatsapp/webhook")
        async def whatsapp_webhook_receive(request: Request):
            """
            Recebe mensagens do WhatsApp via Evolution API (via n8n)
            Compatível com formato da interface oficial do Agno
            """
            try:
                data = await request.json()
                
                # Extrair dados da mensagem (suporta múltiplos formatos)
                payload = data.get("body", data) if isinstance(data.get("body"), dict) else data
                
                # Extrair número do remetente
                from_number = None
                if "key" in payload:
                    from_number = payload["key"].get("remoteJid", "").split("@")[0]
                elif "from" in payload:
                    from_number = payload["from"]
                elif "entry" in payload:  # Formato Meta
                    entry = payload["entry"][0] if payload.get("entry") else {}
                    changes = entry.get("changes", [{}])[0]
                    value = changes.get("value", {})
                    messages = value.get("messages", [{}])[0]
                    from_number = messages.get("from", "")
                
                # Extrair texto da mensagem
                message_text = None
                if "message" in payload:
                    msg_data = payload["message"]
                    if isinstance(msg_data, dict):
                        if "conversation" in msg_data:
                            message_text = msg_data["conversation"]
                        elif "text" in msg_data:
                            message_text = msg_data.get("text", {}).get("body", "")
                        elif "body" in msg_data:
                            message_text = msg_data["body"]
                elif "text" in payload:
                    message_text = payload["text"]
                
                if not from_number or not message_text:
                    return JSONResponse(
                        status_code=200,
                        content={"status": "ignored", "reason": "Invalid message format"}
                    )
                
                # Normalizar número
                from_number = from_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                
                # Permitir mensagens do próprio número para testes
                test_number = whatsapp_destination.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                is_test_message = from_number == test_number
                
                # Verificar ativação
                activation_keyword = "##ativar##"
                is_activation = activation_keyword.lower() in message_text.lower()
                
                if is_activation:
                    whatsapp_active_sessions[from_number] = True
                    welcome_message = (
                        "Ola! Bem-vindo ao assistente da Synapse IA!\n\n"
                        "Estou aqui para te ajudar com automacoes e IA para advogados.\n\n"
                        "Como posso te ajudar hoje?"
                    )
                    send_whatsapp_message(from_number, welcome_message)
                    return JSONResponse(
                        status_code=200,
                        content={"status": "activated"}
                    )
                
                # Verificar se sessão está ativa (ou se é mensagem de teste do próprio número)
                if not is_test_message and (from_number not in whatsapp_active_sessions or not whatsapp_active_sessions[from_number]):
                    return JSONResponse(
                        status_code=200,
                        content={"status": "ignored", "reason": "Session not activated"}
                    )
                
                # Se for mensagem de teste do próprio número, ativar automaticamente
                if is_test_message and from_number not in whatsapp_active_sessions:
                    whatsapp_active_sessions[from_number] = True
                    print(f"[TESTE] Mensagem do proprio numero detectada - ativando sessao automaticamente")
                
                # Processar mensagem com agente ou team
                try:
                    executor = self.agent if self.agent else self.team
                    response = executor.run(message_text, user_id=from_number, session_id=from_number)
                    
                    # Extrair resposta
                    agent_response = response.content if hasattr(response, 'content') else str(response)
                    
                    # Enviar resposta via WhatsApp
                    send_result = send_whatsapp_message(from_number, agent_response)
                    
                    if not send_result.get("success", False):
                        print(f"[ERRO] Falha ao enviar mensagem WhatsApp para {from_number}: {send_result.get('error', 'Erro desconhecido')}")
                    
                    return JSONResponse(
                        status_code=200,
                        content={"status": "processed"}
                    )
                except Exception as e:
                    # Logar erro completo no servidor para debugging
                    print(f"[ERRO] Erro ao processar mensagem de {from_number}: {str(e)}")
                    import traceback
                    print(f"[ERRO] Traceback: {traceback.format_exc()}")
                    
                    # Enviar mensagem amigável ao usuário (sem detalhes técnicos)
                    error_message = "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
                    send_whatsapp_message(from_number, error_message)
                    return JSONResponse(
                        status_code=500,
                        content={"status": "error", "error": str(e)}
                    )
            
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "error": str(e)}
                )
    
    def get_router(self):
        """Retorna o router FastAPI (compatível com interface oficial)"""
        return self.router

# ==================== AGENTOS COM INTERFACE WHATSAPP ====================

# Criar interface WhatsApp adaptada para Evolution API
# Usa Lead Qualifier como agente principal para WhatsApp
whatsapp_interface = EvolutionWhatsappAdapter(agent=lead_qualifier)

# Criar interfaces para usuários finais
# AG-UI: Interface padrão para conectar a frontends customizados (Dojo, Agent UI, etc.)
interfaces_list = []
if AGUI_AVAILABLE:
    agui_interface = AGUI(agent=lead_qualifier)  # Interface AG-UI usando Lead Qualifier
    interfaces_list.append(agui_interface)
    print("[OK] Interface AG-UI configurada para frontends customizados")
else:
    print("[INFO] Interface AG-UI nao disponivel - instale: pip install ag-ui-protocol")

# Criar AgentOS com workflow, team, agentes individuais e interfaces
agent_os = AgentOS(
    name="Synapse IA Sales System",
    description="Sistema de vendas Synapse IA com workflow, team e agentes especializados para qualificação, coleta de informações e fechamento",
    workflows=[presales_workflow],
    teams=[sales_team],
    agents=[lead_qualifier, information_collector, objection_handler, communication_manager, closer],  # Todos disponíveis individualmente
    knowledge=[synapse_knowledge],  # Knowledge base disponível no AgentOS
    interfaces=interfaces_list if interfaces_list else None,  # Interface AG-UI para frontends customizados (se disponível)
)

# Obter app FastAPI combinado
app = agent_os.get_app()

# Adicionar router WhatsApp ao app (endpoints oficiais: /whatsapp/webhook, /whatsapp/status)
app.include_router(whatsapp_interface.get_router())

# Manter compatibilidade com endpoint antigo /webhook/agno (redireciona para /whatsapp/webhook)
whatsapp_router = APIRouter()

@whatsapp_router.post("/webhook/agno")
async def whatsapp_webhook_n8n_legacy(request: Request):
    """Endpoint legacy - usa a mesma lógica do adaptador"""
    # Chama diretamente o endpoint do adaptador
    from fastapi.routing import APIRoute
    # Encontrar o endpoint POST /whatsapp/webhook do adaptador
    whatsapp_routes = whatsapp_interface.get_router().routes
    post_webhook_route = None
    for route in whatsapp_routes:
        if route.path == "/whatsapp/webhook" and "POST" in [m for m in route.methods]:
            post_webhook_route = route
            break
    
    if post_webhook_route:
        return await post_webhook_route.endpoint(request)
    else:
        # Fallback: usar a mesma lógica manualmente
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": "Webhook handler not found"}
        )

@whatsapp_router.get("/webhook/agno")
async def whatsapp_webhook_verify_legacy(request: Request):
    """Endpoint legacy - verificação"""
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "WhatsApp webhook is active"}
    )

# Adicionar router legacy ao app
app.include_router(whatsapp_router)

# ==================== EXECUTAR ====================

if __name__ == "__main__":
    print("Iniciando AgentOS - Time de Vendas Synapse IA")
    print("=" * 70)
    print("\nSistema de vendas com:")
    print("  - Workflow: Workflow de Vendas Synapse IA (Router)")
    print("  - Team: Time de Vendas Synapse IA (Coordenado)")
    print("  - Agents: 5 agentes especializados:")
    print("    1. Lead Qualifier - Qualifica leads (com memoria)")
    print("    2. Information Collector - Coleta informacoes (com memoria)")
    print("    3. Objection Handler - Quebra objecoes (com memoria)")
    print("    4. Communication Manager - Email e agendamentos (com memoria)")
    print("    5. Closer - Fecha negocios (com memoria)")
    print("  - Knowledge: Base de conhecimento da Synapse IA")
    print("  - Memoria: Todos os agentes tem memoria persistente (enable_agentic_memory)")
    print("  - Humanizado: Comunicacao natural, sem scores ao lead")
    print("\n[WHATSAPP INTEGRATION]")
    print("  - Interface Oficial Agno: GET/POST /whatsapp/webhook")
    print("  - Status: GET /whatsapp/status")
    print("  - Webhook n8n (compatibilidade): POST /webhook/agno")
    print("  - URL Externa: https://webhook.iagoflow.com/webhook/agno")
    print("  - Ativacao: Envie '##ativar##' para iniciar conversa")
    print("  - Teste: Mensagens do proprio numero (5522992523549) sao processadas automaticamente")
    print("  - Instancia: NOBRU")
    print("  - API: https://api.iagoflow.com")
    print("  - Provider: Evolution API (adaptado para interface Agno)")
    print("\n[INTERFACES DISPONIVEIS]")
    print("\n1. CONTROL PLANE (Gerenciamento e Monitoramento):")
    print("   - Acesse: https://os.agno.com")
    print("   - Clique em 'Add new OS' > 'Local'")
    print("   - Endpoint: http://localhost:7777")
    print("   - Conecte e gerencie seus agentes, workflows e teams")
    print("   - Monitore sessões, memórias e métricas")
    print("\n2. AGENT UI (Frontend Open-Source para Usuarios Finais):")
    print("   - Clone: git clone https://github.com/agno-agi/agent-ui.git")
    print("   - Configure para conectar ao AgentOS em http://localhost:7777")
    print("   - Acesse: http://localhost:3000")
    print("   - Interface bonita para usuarios finais interagirem com os agentes")
    print("\n3. AG-UI PROTOCOL (Frontends Customizados):")
    print("   - Endpoint AG-UI: POST http://localhost:7777/agui")
    print("   - Status: GET http://localhost:7777/agui/status")
    print("   - Use Dojo ou qualquer frontend compatível com AG-UI")
    print("   - Clone Dojo: git clone https://github.com/ag-ui-protocol/ag-ui.git")
    print("\n4. API DIRETA (Programatico):")
    print("   - API Docs: http://localhost:7777/docs")
    print("   - Config: http://localhost:7777/config")
    print("   - Workflows: http://localhost:7777/workflows/synapse-sales-workflow/runs")
    print("   - Teams: http://localhost:7777/teams/synapse-sales-team/runs")
    print("\nPressione Ctrl+C para parar o servidor\n")
    
    # Servir o AgentOS na porta 7777
    # IMPORTANTE: Usar uvicorn diretamente para garantir que todas as rotas sejam servidas
    import uvicorn
    uvicorn.run(
        app,
        host="localhost",
        port=7777,
        log_level="info"
    )
