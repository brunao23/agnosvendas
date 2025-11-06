# Guia de Configuração e Uso do EmailTools

## Status Atual

✅ **EmailTools CONFIGURADO e FUNCIONAL**

- **Email Remetente**: brunocostaads23@gmail.com
- **Nome Remetente**: Synapse IA  
- **Senha de App**: Configurada
- **Servidor SMTP**: smtp.gmail.com
- **Porta**: 465

## Como o EmailTools Funciona

O EmailTools do Agno usa a função `email_user(subject, body)` para enviar emails.

### Parâmetros

- `subject` (str): Assunto do email
- `body` (str): Corpo do email (texto ou HTML)

### Limitações

⚠️ **IMPORTANTE**: O EmailTools do Agno pode ter limitações quanto ao destinatário:
- O `receiver_email` pode precisar ser configurado na inicialização do EmailTools
- Ou pode ser necessário especificar o destinatário de outra forma

## Como Usar no Communication Manager

O agente **Communication Manager** pode enviar emails usando comandos como:

```
"Envie um email para [email] com assunto [assunto] e corpo [corpo]"
"Envie email de apresentação da Synapse IA para [email]"
"Envie email de follow-up para o lead"
```

## Exemplo de Uso

```python
# O Communication Manager irá usar:
email_user(
    subject="Apresentação Synapse IA",
    body="Conteúdo do email personalizado..."
)
```

## Próximos Passos

Se precisar enviar para emails diferentes dinamicamente, pode ser necessário:

1. **Configurar múltiplos EmailTools** com diferentes receiver_email
2. **Usar GmailTools** em vez de EmailTools (mais flexível)
3. **Verificar documentação atualizada** do Agno sobre EmailTools

## Teste

Para testar o envio de emails, use o Communication Manager no AgentOS:

1. Acesse: http://localhost:7777
2. Use o agente: `communication-manager`
3. Envie mensagem: "Envie um email de teste para brunocostaads23@gmail.com"


