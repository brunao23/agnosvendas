@echo off
REM Script Batch para executar o AgentOS Local no Windows

echo.
echo ========================================
echo   Sistema de Pre-Venda - AgentOS
echo ========================================
echo.

REM Configure sua chave da OpenAI como variável de ambiente em vez de commitar no código.
REM Exemplo (temporário no PowerShell):
REM   $env:OPENAI_API_KEY = "sua_chave_aqui"
REM Em Windows (cmd.exe) para sessão atual:
REM   set OPENAI_API_KEY=your_key_here
REM Para persistir (PowerShell):
REM   setx OPENAI_API_KEY "your_key_here"

echo [INFO] Certifique-se de definir a variável de ambiente OPENAI_API_KEY antes de executar.
echo.
echo O AgentOS sera iniciado em:
echo   - Interface: http://localhost:7777
echo   - API Docs: http://localhost:7777/docs
echo   - Config: http://localhost:7777/config
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

REM Executar o AgentOS
python agentos_local.py

pause


