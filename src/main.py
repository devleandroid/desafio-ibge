import os
from dotenv import load_dotenv
from auth import login
from ibge_client import carregar_municipios_ibge
from processor import processar
from stats import calcular_estatisticas
from submitter import enviar_estatisticas

load_dotenv()

def main():
    # Criar pasta data se não existir
    os.makedirs("data", exist_ok=True)
    
    # Verificar se input.csv existe
    if not os.path.exists("data/input.csv"):
        print("❌ Arquivo data/input.csv não encontrado!")
        print("   Por favor, crie o arquivo com os dados do desafio")
        print("\n   Conteúdo esperado:")
        print("   municipio,populacao")
        print("   Niteroi,515317")
        print("   Sao Goncalo,1091737")
        print("   ...")
        return
    
    # 1. Login
    token = login(os.getenv("MY_EMAIL"), os.getenv("MY_PASSWORD"))
    if not token:
        return
    
    # 2. Carregar dados IBGE
    print("Carregando municípios do IBGE...")
    municipios_ibge = carregar_municipios_ibge()
    
    # 3. Processar input.csv
    print("Processando input.csv...")
    resultados = processar("data/input.csv", "data/resultado.csv", municipios_ibge)
    
    # 4. Calcular estatísticas
    stats = calcular_estatisticas(resultados)
    print("Estatísticas calculadas:", stats)
    
    # 5. Enviar
    enviar_estatisticas(token, stats)

if __name__ == "__main__":
    main()