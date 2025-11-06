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
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# ... existing content ...
