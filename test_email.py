"""
Script de teste para EmailTools
Testa o envio de emails através do Communication Manager
"""

import os
from playground import communication_manager

# Configurar API key via variável de ambiente (não commitar chaves no repositório)
# Exemplo no PowerShell:
#   $env:OPENAI_API_KEY = "your_key_here"
# Ou criar um .env local sem commitar: NEXT_PUBLIC_OS_SECURITY_KEY=...

print("=" * 70)
print("TESTE DE ENVIO DE EMAIL - Communication Manager")
print("=" * 70)
print()

# Verificar se EmailTools está disponível
email_tools_available = any("EmailTools" in str(type(tool)) for tool in communication_manager.tools)
print(f"EmailTools disponivel: {'SIM' if email_tools_available else 'NAO'}")
print()

if email_tools_available:
    print("Testando envio de email...")
    print()
    
    # Teste 1: Email simples
    print("Teste 1: Enviar email de teste")
    print("-" * 70)
    
    test_message = """
    Envie um email de teste para brunocostaads23@gmail.com com:
    - Assunto: Teste de EmailTools - Synapse IA
    - Corpo: Este é um email de teste do sistema de vendas Synapse IA. 
    O EmailTools está funcionando corretamente!
    """
    
    try:
        response = communication_manager.run(test_message)
        print("Resposta do agente:")
        print(response.content)
        print()
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        print()
    
    # Teste 2: Email de apresentação
    print("Teste 2: Enviar email de apresentação")
    print("-" * 70)
    
    presentation_message = """
    Envie um email de apresentação da Synapse IA para brunocostaads23@gmail.com.
    O email deve incluir:
    - Apresentação da empresa Synapse IA
    - Principais produtos (Automação de WhatsApp, Atualizações Automatizadas, etc.)
    - Benefício de 70% de redução em perguntas repetitivas
    - Oferta de consultoria gratuita
    """
    
    try:
        response = communication_manager.run(presentation_message)
        print("Resposta do agente:")
        print(response.content)
        print()
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        print()
else:
    print("⚠️ EmailTools não está configurado ou disponível.")
    print("Verifique se as credenciais estão corretas no playground.py")
    print()

print("=" * 70)
print("Teste concluído!")
print("=" * 70)

