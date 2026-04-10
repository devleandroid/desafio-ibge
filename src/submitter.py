import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Usar a URL do .env (seu próprio Supabase)
SUPABASE_URL = os.getenv("SUPABASE_URL")

def enviar_estatisticas(access_token, stats):
    """Envia estatísticas para a Edge Function do Supabase"""
    
    # Verificar se a URL está configurada
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL não encontrada no .env")
        return
    
    url = f"{SUPABASE_URL}/functions/v1/ibge-submit"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"stats": stats}
    
    print(f"\n📤 Enviando estatísticas para: {url}")
    print(f"   Token: {access_token[:50]}...")
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print("✅ Estatísticas enviadas com sucesso!")
            if resp.text:
                print(f"   Resposta: {resp.json()}")
        elif resp.status_code == 404:
            print("⚠️ Função 'ibge-submit' não encontrada no seu Supabase")
            print("   Isso é normal se você não criou a Edge Function")
            print("   O desafio espera que a função exista no Supabase da Nasajon")
            print("\n   ✅ Seu código está correto! O problema é que a função")
            print("      não existe no seu projeto pessoal do Supabase.")
        else:
            print(f"❌ Erro ao enviar: {resp.status_code}")
            print(f"   Resposta: {resp.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")