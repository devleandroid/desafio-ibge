"""Envio das estatísticas calculadas para uma Edge Function do Supabase."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def enviar_estatisticas(access_token, stats):
    """Envia estatísticas usando o token de acesso do usuário autenticado."""
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL não encontrada no .env")
        return
    if not access_token:
        print("❌ Token de acesso ausente; as estatísticas não foram enviadas.")
        return

    url = f"{SUPABASE_URL.rstrip('/')}/functions/v1/ibge-submit"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    if SUPABASE_ANON_KEY:
        headers["apikey"] = SUPABASE_ANON_KEY

    print(f"\n📤 Enviando estatísticas para: {url}")
    try:
        resp = requests.post(url, json={"stats": stats}, headers=headers, timeout=10)

        if 200 <= resp.status_code < 300:
            print("✅ Estatísticas enviadas com sucesso!")
            if resp.text:
                try:
                    print(f"   Resposta: {resp.json()}")
                except ValueError:
                    print(f"   Resposta: {resp.text}")
        elif resp.status_code == 404:
            print("⚠️ Função 'ibge-submit' não encontrada no Supabase.")
            print("   Verifique se a Edge Function está implantada neste projeto.")
        else:
            print(f"❌ Erro ao enviar: {resp.status_code}")
            print(f"   Resposta: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar estatísticas: {e}")
