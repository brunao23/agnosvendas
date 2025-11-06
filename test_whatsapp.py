"""
Script de teste para enviar mensagem WhatsApp via Evolution API
Testa a ferramenta send_whatsapp_lead
"""

import os
import sys

# Configure a chave via variável de ambiente (não commitar chaves no repositório)
# Exemplo (PowerShell):
#   $env:OPENAI_API_KEY = "your_key_here"

# Importar configurações e criar função de teste direta
import requests
from playground import evolution_api_url, evolution_api_token, evolution_instance_name, whatsapp_destination

print("=" * 70)
print("TESTE DE ENVIO WHATSAPP - EVOLUTION API")
print("=" * 70)
print()

# Dados do teste
lead_info = """
NOME: Joao Silva
ESCRITORIO: Silva & Associados
DORES IDENTIFICADAS:
- Perde tempo com atendimento repetitivo no WhatsApp
- Clientes ligam constantemente perguntando sobre processos
- Trabalho manual em documentos

PRODUTOS SYNAPSE IA RECOMENDADOS:
- Automacao de Atendimento via WhatsApp
- Atualizacoes Automatizadas sobre Processos
- Notificacoes sobre Sentencas

SCORE INTERNO: 85/100
PROXIMO PASSO: Agendar consultoria gratuita
"""

mensagem = f"*NOVO LEAD QUALIFICADO - SYNAPSE IA*\n\n{lead_info}\n\nLead qualificado e pronto para follow-up!"

numero_teste = "5522992523549"

print(f"Configuracao:")
print(f"  URL: {evolution_api_url}")
print(f"  Instancia: {evolution_instance_name}")
print(f"  Token: {evolution_api_token[:20]}...")
print(f"")
print(f"Enviando mensagem de teste para WhatsApp...")
print(f"Destino: {numero_teste}")
print()

try:
    # URL da Evolution API para enviar mensagem
    url = f"{evolution_api_url}/message/sendText/{evolution_instance_name}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": evolution_api_token
    }
    
    # Formato do número
    number = numero_teste.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    
    payload = {
        "number": number,
        "text": mensagem
    }
    
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    print()
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    print("RESULTADO:")
    print("-" * 70)
    print(f"Status Code: {response.status_code}")
    print(f"Resposta: {response.text}")
    print("-" * 70)
    print()
    
    if response.status_code in [200, 201]:
        print("[OK] Mensagem enviada com sucesso!")
        print(f"Verifique o WhatsApp: {numero_teste}")
        print(f"Status da mensagem: {response.json().get('status', 'PENDING')}")
    else:
        print("[ERRO] Falha ao enviar mensagem")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"[ERRO] Excecao ao testar: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)

