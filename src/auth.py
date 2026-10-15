"""Compatibilidade para os consumidores da autenticação Supabase anterior."""

import os

import requests
from dotenv import load_dotenv

from application.errors import AuthenticationError
from infrastructure.config import AppSettings
from infrastructure.supabase_auth import SupabaseAuthenticator


def _settings():
    """Carrega as configurações Supabase do ambiente, incluindo arquivo `.env`."""
    load_dotenv()
    try:
        return AppSettings.from_environment().supabase
    except ValueError as error:
        print(f"❌ {error}")
        return None


def criar_conta(email, password, nome):
    """Cria uma conta no Supabase sem expor credenciais ou tokens no log."""
    settings = _settings()
    if settings is None:
        print("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY no arquivo .env.")
        return None
    try:
        response = requests.post(
            f"{settings.url}/auth/v1/signup",
            json={"email": email, "password": password, "data": {"nome": nome}},
            headers={"apikey": settings.anon_key, "Content-Type": "application/json"},
            timeout=10,
        )
    except requests.exceptions.RequestException as error:
        print(f"❌ Erro ao criar conta no Supabase: {error}")
        return None
    if response.ok:
        print("✅ Conta criada. Verifique seu e-mail para confirmar.")
    else:
        print(f"❌ Erro ao criar conta: {response.text}")
    return response


def login(email, password):
    """Autentica no Supabase e preserva o retorno de token ou `None` legado."""
    settings = _settings()
    if settings is None:
        print("❌ Configure as credenciais do Supabase no arquivo .env.")
        return None
    try:
        return SupabaseAuthenticator(settings).authenticate(email, password)
    except AuthenticationError as error:
        print(f"❌ {error}")
        return None
