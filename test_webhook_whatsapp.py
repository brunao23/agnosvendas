"""
Script de teste para webhook WhatsApp
Testa a ativação e conversa via webhook
"""

import requests
import json

WEBHOOK_URL = "http://localhost:7777/whatsapp/webhook/evolution"

def test_webhook_activation():
    """Testa a ativação com ##ativar##"""
    print("=" * 70)
    print("TESTE 1: ATIVACAO COM ##ativar##")
    print("=" * 70)
    
    payload = {
        "key": {
            "remoteJid": "5522992523549@s.whatsapp.net"
        },
        "message": {
            "conversation": "##ativar##"
        }
    }
    
    print(f"\nEnviando para: {WEBHOOK_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "activated":
                print("\n[OK] Ativacao bem-sucedida!")
                return True
            else:
                print(f"\n[AVISO] Status inesperado: {data.get('status')}")
        else:
            print(f"\n[ERRO] Status code: {response.status_code}")
            
    except Exception as e:
        print(f"[ERRO] Excecao: {e}")
    
    return False

def test_webhook_conversation():
    """Testa conversa após ativação"""
    print("\n" + "=" * 70)
    print("TESTE 2: CONVERSA APOS ATIVACAO")
    print("=" * 70)
    
    payload = {
        "key": {
            "remoteJid": "5522992523549@s.whatsapp.net"
        },
        "message": {
            "conversation": "Quero saber sobre automacao para advogados"
        }
    }
    
    print(f"\nEnviando para: {WEBHOOK_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "processed":
                print("\n[OK] Mensagem processada pelo agente!")
                return True
            elif data.get("status") == "ignored":
                print("\n[AVISO] Mensagem ignorada - sessao nao ativada")
                print("Execute o teste 1 primeiro para ativar a sessao")
            else:
                print(f"\n[AVISO] Status: {data.get('status')}")
        else:
            print(f"\n[ERRO] Status code: {response.status_code}")
            
    except Exception as e:
        print(f"[ERRO] Excecao: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def test_webhook_verify():
    """Testa endpoint de verificação"""
    print("\n" + "=" * 70)
    print("TESTE 3: VERIFICACAO DO WEBHOOK (GET)")
    print("=" * 70)
    
    try:
        response = requests.get(WEBHOOK_URL, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook esta ativo!")
            return True
        else:
            print(f"\n[ERRO] Status code: {response.status_code}")
            
    except Exception as e:
        print(f"[ERRO] Excecao: {e}")
    
    return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTE DE WEBHOOK WHATSAPP - EVOLUTION API")
    print("=" * 70)
    print()
    
    # Teste 1: Verificação
    test_webhook_verify()
    
    # Teste 2: Ativação
    activation_success = test_webhook_activation()
    
    # Teste 3: Conversa (só se ativação funcionou)
    if activation_success:
        test_webhook_conversation()
    else:
        print("\n[AVISO] Pulando teste de conversa - ativacao falhou")
    
    print("\n" + "=" * 70)
    print("TESTES CONCLUIDOS")
    print("=" * 70)


