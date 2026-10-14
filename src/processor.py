"""Normalização, identificação e exportação dos municípios informados."""

import csv
import unicodedata
import os

def normalizar(texto):
    """Remove acentos, normaliza espaços e converte o texto para minúsculas."""
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return ' '.join(texto.split())

def encontrar_municipio(nome_input, lista_ibge):
    """Encontra um município por nome normalizado e informa se há ambiguidade."""
    nome_norm = normalizar(nome_input)
    matches = []
    for mun in lista_ibge:
        if normalizar(mun["nome"]) == nome_norm:
            matches.append(mun)
    
    if len(matches) == 1:
        return ("OK", matches[0])
    elif len(matches) > 1:
        return ("AMBIGUO", None)
    else:
        return ("NAO_ENCONTRADO", None)

def processar(input_csv_path, output_csv_path, lista_ibge):
    """Cruza o CSV de entrada com os dados do IBGE e grava os resultados."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Se o caminho não for absoluto, torna absoluto
    if not os.path.isabs(input_csv_path):
        input_csv_path = os.path.join(base_dir, input_csv_path)
    if not os.path.isabs(output_csv_path):
        output_csv_path = os.path.join(base_dir, output_csv_path)
    
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_csv_path}")
    
    # Criar diretório de saída se não existir
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    resultados = []
    with open(input_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            municipio = row["municipio"]
            populacao = row["populacao"]
            status, dados_ibge = encontrar_municipio(municipio, lista_ibge)
            
            if status == "OK":
                resultados.append({
                    "municipio_input": municipio,
                    "populacao_input": populacao,
                    "municipio_ibge": dados_ibge["nome"],
                    "uf": dados_ibge["uf"],
                    "regiao": dados_ibge["regiao"],
                    "id_ibge": dados_ibge["id_ibge"],
                    "status": status
                })
            else:
                resultados.append({
                    "municipio_input": municipio,
                    "populacao_input": populacao,
                    "municipio_ibge": "",
                    "uf": "",
                    "regiao": "",
                    "id_ibge": "",
                    "status": status
                })
    
    # Escreve resultado.csv
    with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["municipio_input", "populacao_input", "municipio_ibge", "uf", "regiao", "id_ibge", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
    
    return resultados