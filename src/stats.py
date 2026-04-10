from collections import defaultdict

def calcular_estatisticas(resultados):
    total_municipios = len(resultados)
    total_ok = sum(1 for r in resultados if r["status"] == "OK")
    total_nao_encontrado = sum(1 for r in resultados if r["status"] == "NAO_ENCONTRADO")
    total_erro_api = sum(1 for r in resultados if r["status"] == "ERRO_API")
    
    pop_total_ok = 0
    medias_por_regiao = defaultdict(list)
    
    for r in resultados:
        if r["status"] == "OK":
            pop = int(r["populacao_input"])
            pop_total_ok += pop
            regiao = r["regiao"]
            medias_por_regiao[regiao].append(pop)
    
    # Calcula média por região
    medias = {}
    for regiao, pops in medias_por_regiao.items():
        medias[regiao] = sum(pops) / len(pops)
    
    return {
        "total_municipios": total_municipios,
        "total_ok": total_ok,
        "total_nao_encontrado": total_nao_encontrado,
        "total_erro_api": total_erro_api,
        "pop_total_ok": pop_total_ok,
        "medias_por_regiao": medias
    }