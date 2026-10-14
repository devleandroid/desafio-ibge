"""Cliente da API de Localidades do IBGE."""

import requests

def carregar_municipios_ibge():
    """Baixa os municípios do IBGE e extrai nome, UF, região e identificador."""
    print("   Conectando à API do IBGE...")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao acessar IBGE: {e}")
    
    print(f"   Processando {len(resp.json())} municípios...")
    municipios = []
    erros = 0
    
    for item in resp.json():
        try:
            # Navegação segura com fallback para valores padrão
            # Usamos .get() para evitar KeyError e verificamos se não é None
            
            microrregiao = item.get("microrregiao")
            if microrregiao is None:
                # Caso especial: município sem microrregião (ex: Distrito Federal)
                uf = "DF"
                regiao = "Centro-Oeste"
                id_ibge = item.get("id")
                nome = item.get("nome", "Desconhecido")
            else:
                mesorregiao = microrregiao.get("mesorregiao")
                if mesorregiao is None:
                    uf = "Desconhecido"
                    regiao = "Desconhecido"
                else:
                    uf_info = mesorregiao.get("UF")
                    if uf_info is None:
                        uf = "Desconhecido"
                        regiao = "Desconhecido"
                    else:
                        uf = uf_info.get("sigla", "Desconhecido")
                        regiao_info = uf_info.get("regiao")
                        regiao = regiao_info.get("nome", "Desconhecido") if regiao_info else "Desconhecido"
                
                id_ibge = item.get("id")
                nome = item.get("nome", "Desconhecido")
            
            municipios.append({
                "nome": nome,
                "uf": uf,
                "regiao": regiao,
                "id_ibge": id_ibge
            })
            
        except Exception as e:
            erros += 1
            # Para debugging, mostre o primeiro erro apenas
            if erros == 1:
                print(f"   ⚠️ Aviso: Um município teve dados incompletos: {item.get('nome', 'desconhecido')}")
            # Ainda assim adiciona um registro básico
            municipios.append({
                "nome": item.get("nome", "Desconhecido"),
                "uf": "Desconhecido",
                "regiao": "Desconhecido",
                "id_ibge": item.get("id")
            })
    
    if erros > 0:
        print(f"   ⚠️ {erros} municípios tinham dados incompletos (usado valores padrão)")
    
    print(f"   ✅ {len(municipios)} municípios carregados com sucesso")
    return municipios