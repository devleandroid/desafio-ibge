"""Compatibilidade para cálculo de estatísticas usando dicionários legados."""

from domain.models import Municipality, MunicipalityResult, MunicipalityStatus
from domain.services import calculate_statistics


def calcular_estatisticas(resultados):
    """Converte resultados antigos para entidades e devolve as estatísticas."""
    rows = []
    for result in resultados:
        status = MunicipalityStatus(result["status"])
        matched = None
        if status is MunicipalityStatus.OK:
            matched = Municipality(
                name=result.get("municipio_ibge", ""),
                state=result.get("uf", ""),
                region=result.get("regiao", ""),
                ibge_id=result.get("id_ibge"),
            )
        rows.append(
            MunicipalityResult(
                input_name=result.get("municipio_input", ""),
                input_population=str(result.get("populacao_input", "0")),
                status=status,
                municipality=matched,
            )
        )
    return calculate_statistics(rows).to_mapping()
