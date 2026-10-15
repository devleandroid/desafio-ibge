"""Regras puras de matching e cálculo de estatísticas dos municípios."""

import unicodedata
from collections import defaultdict
from collections.abc import Iterable

from domain.models import (
    Municipality,
    MunicipalityResult,
    MunicipalityStatistics,
    MunicipalityStatus,
)


def normalize_municipality_name(name: str) -> str:
    """Remove acentos e espaços excedentes e converte o nome para minúsculas."""
    without_accents = unicodedata.normalize("NFKD", name.strip())
    without_accents = without_accents.encode("ascii", "ignore").decode("ascii")
    return " ".join(without_accents.casefold().split())


def find_municipality(
    input_name: str,
    catalog: Iterable[Municipality],
) -> tuple[MunicipalityStatus, Municipality | None]:
    """Retorna o município único correspondente ou status de ausência/ambiguidade."""
    normalized_name = normalize_municipality_name(input_name)
    matches = [
        municipality
        for municipality in catalog
        if normalize_municipality_name(municipality.name) == normalized_name
    ]
    if len(matches) == 1:
        return MunicipalityStatus.OK, matches[0]
    if matches:
        return MunicipalityStatus.AMBIGUOUS, None
    return MunicipalityStatus.NOT_FOUND, None


def calculate_statistics(results: Iterable[MunicipalityResult]) -> MunicipalityStatistics:
    """Calcula contagens, população total encontrada e médias agrupadas por região."""
    rows = tuple(results)
    found = [row for row in rows if row.status is MunicipalityStatus.OK]
    population_by_region: dict[str, list[int]] = defaultdict(list)
    total_population = 0

    for row in found:
        population = int(row.input_population)
        total_population += population
        if row.municipality is not None:
            population_by_region[row.municipality.region].append(population)

    return MunicipalityStatistics(
        total_municipalities=len(rows),
        found=len(found),
        not_found=sum(
            row.status is MunicipalityStatus.NOT_FOUND for row in rows
        ),
        ambiguous=sum(
            row.status is MunicipalityStatus.AMBIGUOUS for row in rows
        ),
        api_errors=sum(
            row.status is MunicipalityStatus.API_ERROR for row in rows
        ),
        total_population=total_population,
        average_by_region={
            region: sum(populations) / len(populations)
            for region, populations in population_by_region.items()
        },
    )
