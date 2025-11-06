# Configuração Evolution API (WhatsApp)

## Status

✅ **Evolution API CONFIGURADA e PRONTA PARA USO**

- **URL**: https://api.iagoflow.com
- **Instância**: NOBRU
- **Token**: Configurado
- **Destino WhatsApp**: 5522992523549

## Configuração Atual

As credenciais estão configuradas diretamente no código. Se precisar alterar, edite as variáveis em `playground.py` ou use variáveis de ambiente.

## Variáveis Necessárias

### 1. EVOLUTION_API_URL
- URL base da sua Evolution API
- Exemplo: `https://api.evolutionapi.com` ou `https://seu-servidor.com.br`

### 2. EVOLUTION_API_TOKEN
- Token de autenticação da Evolution API
- Obtenha este token na sua conta Evolution API

### 3. EVOLUTION_INSTANCE_NAME
- Nome da instância do WhatsApp criada na Evolution API
- Exemplo: `synapse_ia_whatsapp` ou `instancia_principal`

### 4. WHATSAPP_DESTINATION
- Número do WhatsApp que receberá as notificações de leads
- Formato: `5511999999999` (sem caracteres especiais)
- Exemplo: `5511987654321`

## Como Configurar

### PowerShell (Windows)
```powershell
$env:EVOLUTION_API_URL="https://api.evolutionapi.com"
$env:EVOLUTION_API_TOKEN="seu-token-aqui"
$env:EVOLUTION_INSTANCE_NAME="nome-da-instancia"
$env:WHATSAPP_DESTINATION="5511999999999"
```

### Linux/Mac
```bash
export EVOLUTION_API_URL="https://api.evolutionapi.com"
export EVOLUTION_API_TOKEN="seu-token-aqui"
export EVOLUTION_INSTANCE_NAME="nome-da-instancia"
export WHATSAPP_DESTINATION="5511999999999"
```

## Como Funciona

1. **Lead Qualifier** qualifica um lead
2. Automaticamente envia notificação para WhatsApp usando `send_whatsapp_lead`
3. A mensagem inclui:
   - Nome do lead
   - Escritório/empresa
   - Dores identificadas
   - Produtos Synapse IA recomendados
   - Score interno de qualificação
   - Próximo passo

## Formato da Mensagem

```
🎯 *NOVO LEAD QUALIFICADO - SYNAPSE IA*

[Nome do Lead]
[Escritório/Empresa]
[Dores identificadas]
[Produtos recomendados]
[Score interno]
[Próximo passo]

✅ Lead qualificado e pronto para follow-up!
```

## Teste

Após configurar, qualifique um lead usando o Lead Qualifier e verifique se a mensagem chega no WhatsApp configurado.

