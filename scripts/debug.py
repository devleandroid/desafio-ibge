#!/usr/bin/env python3
"""Ferramenta de debug para o desafio IBGE."""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def testar_dns():
    """Testa resolução de DNS."""
    import socket
    
    print("\n🔍 TESTANDO DNS")
    print("=" * 40)
    
    urls = [
        os.getenv("SUPABASE_URL", ""),
        "https://servicodados.ibge.gov.br",
    ]
    
    for url in urls:
        if not url:
            continue
            
        host = url.replace("https://", "").replace("http://", "")
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ {host} -> {ip}")
        except socket.gaierror as e:
            print(f"❌ {host} -> Erro: {e}")


def testar_api_ibge():
    """Testa conexão com API do IBGE."""
    print("\n📊 TESTANDO API DO IBGE")
    print("=" * 40)
    
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        print(f"✅ Conexão OK! {len(dados)} municípios encontrados")
        
        # Mostrar alguns exemplos
        print("\n   Exemplos dos primeiros 3 municípios:")
        for i, mun in enumerate(dados[:3]):
            print(f"   {i+1}. {mun['nome']} (ID: {mun['id']})")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")


def testar_supabase():
    """Testa conexão com Supabase."""
    print("\n🔐 TESTANDO SUPABASE")
    print("=" * 40)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL não configurada no .env")
        return
    
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY não configurada no .env")
        return
    
    print(f"✅ URL configurada: {supabase_url}")
    print(f"✅ Key configurada: {supabase_key[:50]}...")
    
    # Testar health check
    try:
        resp = requests.get(f"{supabase_url}/rest/v1/", 
                           headers={"apikey": supabase_key},
                           timeout=10)
        print(f"✅ Supabase respondendo (status: {resp.status_code})")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")


def testar_arquivos():
    """Verifica existência de arquivos necessários."""
    print("\n📁 VERIFICANDO ARQUIVOS")
    print("=" * 40)
    
    base_dir = Path(__file__).parent.parent
    arquivos = [
        base_dir / "data" / "input.csv",
        base_dir / "src" / "auth.py",
        base_dir / "src" / "ibge_client.py",
        base_dir / "src" / "processor.py",
        base_dir / "src" / "stats.py",
        base_dir / "src" / "submitter.py",
        base_dir / ".env",
    ]
    
    for arquivo in arquivos:
        if arquivo.exists():
            tamanho = arquivo.stat().st_size
            print(f"✅ {arquivo.name} ({tamanho} bytes)")
        else:
            print(f"❌ {arquivo.name} - NÃO ENCONTRADO")


def testar_token():
    """Testa obtenção de token do Supabase."""
    print("\n🎫 TESTANDO AUTENTICAÇÃO")
    print("=" * 40)
    
    from auth import login
    
    email = os.getenv("MY_EMAIL")
    password = os.getenv("MY_PASSWORD")
    
    if not email or not password:
        print("❌ Credenciais não configuradas no .env")
        return
    
    token = login(email, password)
    
    if token:
        print(f"✅ Token obtido com sucesso!")
        print(f"   Token: {token[:50]}...")
        print(f"   Tamanho: {len(token)} caracteres")
    else:
        print("❌ Falha ao obter token")


def main():
    """Executa todos os testes de debug."""
    print("\n" + "=" * 50)
    print("🔧 FERRAMENTA DE DEBUG - DESAFIO IBGE")
    print("=" * 50)
    
    testar_arquivos()
    testar_dns()
    testar_api_ibge()
    testar_supabase()
    testar_token()
    
    print("\n" + "=" * 50)
    print("✅ DEBUG CONCLUÍDO")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
