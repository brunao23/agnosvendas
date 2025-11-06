# Script PowerShell para executar o AgentOS Local
# Este script configura a variável de ambiente e executa o sistema

Write-Host "🚀 Iniciando Sistema de Pré-Venda - AgentOS" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan

# Configure sua chave da OpenAI como variável de ambiente em vez de commitar no código.
# Exemplo (PowerShell para sessão atual):
#   $env:OPENAI_API_KEY = "your_key_here"
# Para persistir entre sessões (Windows):
#   setx OPENAI_API_KEY "your_key_here"

Write-Host "✅ Certifique-se de definir a variável de ambiente OPENAI_API_KEY antes de executar." -ForegroundColor Green
Write-Host ""
Write-Host "📌 O AgentOS será iniciado em:" -ForegroundColor Yellow
Write-Host "   • Interface: http://localhost:7777" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:7777/docs" -ForegroundColor White
Write-Host "   • Config: http://localhost:7777/config" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

# Executar o AgentOS
python agentos_local.py


