import requests

url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
resp = requests.get(url)

for i, item in enumerate(resp.json()):
    try:
        uf = item["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        regiao = item["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
    except (TypeError, KeyError) as e:
        print(f"Erro no município {i}: {item.get('nome', 'sem nome')}")
        print(f"  Erro: {e}")
        print(f"  Dados: {item}")
        break