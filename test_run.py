"""Teste rápido para verificar se o AgentOS inicia"""
import os
import sys

# Configure a chave via variável de ambiente (não commitar chaves no repositório)
# Exemplo (PowerShell):
#   $env:OPENAI_API_KEY = "your_key_here"

print("🚀 Iniciando AgentOS...")
print("=" * 70)

try:
    from agentos_local import app
    print("✅ Imports OK!")
    print("✅ App criado!")
    print("\n📌 Servidor será iniciado...")
    print("   Acesse: http://localhost:7777")
    print("\n" + "=" * 70)
    
    # Importar e executar
    import uvicorn
    uvicorn.run(app, host="localhost", port=7777, log_level="info")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


