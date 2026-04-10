import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Limpar a chave: remover espaços, quebras de linha, tabs
if SUPABASE_ANON_KEY:
    SUPABASE_ANON_KEY = SUPABASE_ANON_KEY.strip().replace('\n', '').replace(' ', '')
    SUPABASE_ANON_KEY = ' '.join(SUPABASE_ANON_KEY.split())  # remove espaços múltiplos

def criar_conta(email, password, nome):
    """Passo 1: Criar usuário no Supabase"""
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password,
        "data": {"nome": nome}
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        print("✅ Conta criada. Verifique seu e-mail para confirmar.")
    else:
        print(f"❌ Erro ao criar conta: {resp.text}")
    return resp

def login(email, password):
    """Passo 2: Obter access_token"""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {"email": email, "password": password}
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print("✅ Login realizado com sucesso")
        return token
    else:
        print(f"❌ Falha no login: {resp.text}")
        return None