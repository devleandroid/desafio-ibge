"""Autenticação de usuários na API Auth do Supabase."""

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

def _obter_configuracao():
    """Retorna URL e chave pública do Supabase ou informa configuração ausente."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ SUPABASE_URL e SUPABASE_ANON_KEY devem estar configuradas no .env")
        return None
    return SUPABASE_URL.rstrip("/"), SUPABASE_ANON_KEY

def criar_conta(email, password, nome):
    """Cria uma conta Supabase com e-mail, senha e nome de usuário."""
    configuracao = _obter_configuracao()
    if configuracao is None:
        return None
    supabase_url, anon_key = configuracao
    url = f"{supabase_url}/auth/v1/signup"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password,
        "data": {"nome": nome}
    }
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar conta no Supabase: {e}")
        return None
    if resp.ok:
        print("✅ Conta criada. Verifique seu e-mail para confirmar.")
    else:
        print(f"❌ Erro ao criar conta: {resp.text}")
    return resp

def login(email, password):
    """Autentica o usuário e retorna o token de acesso, se houver sucesso."""
    configuracao = _obter_configuracao()
    if configuracao is None:
        return None
    supabase_url, anon_key = configuracao
    url = f"{supabase_url}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    data = {"email": email, "password": password}
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão durante o login: {e}")
        return None
    if resp.ok:
        token = resp.json().get("access_token")
        if not token:
            print("❌ A resposta do Supabase não contém um token de acesso.")
            return None
        print("✅ Login realizado com sucesso")
        return token
    else:
        print(f"❌ Falha no login: {resp.text}")
        return None