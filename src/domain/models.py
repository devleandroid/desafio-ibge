"""Modelos imutáveis usados pelas regras centrais do desafio IBGE."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class MunicipalityStatus(str, Enum):
    """Estados possíveis ao comparar um município informado com o catálogo IBGE."""

    OK = "OK"
    NOT_FOUND = "NAO_ENCONTRADO"
    AMBIGUOUS = "AMBIGUO"
    API_ERROR = "ERRO_API"


@dataclass(frozen=True)
class Municipality:
    """Representa um município retornado pelo catálogo oficial do IBGE."""

    name: str
    state: str
    region: str
    ibge_id: int | None

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "Municipality":
        """Converte o formato legado do catálogo em uma entidade de domínio."""
        return cls(
            name=values["nome"],
            state=values["uf"],
            region=values["regiao"],
            ibge_id=values.get("id_ibge"),
        )

    def to_mapping(self) -> dict[str, Any]:
        """Exporta os campos no formato mantido pelas funções Python anteriores."""
        return {
            "nome": self.name,
            "uf": self.state,
            "regiao": self.region,
            "id_ibge": self.ibge_id,
        }


@dataclass(frozen=True)
class MunicipalityInput:
    """Município e população informados em uma linha do CSV de entrada."""

    name: str
    population: str


@dataclass(frozen=True)
class MunicipalityResult:
    """Resultado de matching de uma linha, com os dados IBGE quando encontrados."""

    input_name: str
    input_population: str
    status: MunicipalityStatus
    municipality: Municipality | None = None

    def to_mapping(self) -> dict[str, Any]:
        """Converte o resultado para as colunas públicas do CSV e da API."""
        matched = self.municipality
        return {
            "municipio_input": self.input_name,
            "populacao_input": self.input_population,
            "municipio_ibge": matched.name if matched else "",
            "uf": matched.state if matched else "",
            "regiao": matched.region if matched else "",
            "id_ibge": matched.ibge_id if matched else "",
            "status": self.status.value,
        }


@dataclass(frozen=True)
class MunicipalityStatistics:
    """Métricas tipadas calculadas para um lote de municípios processados."""

    total_municipalities: int
    found: int
    not_found: int
    ambiguous: int
    api_errors: int
    total_population: int
    average_by_region: dict[str, float]

    def to_mapping(self) -> dict[str, Any]:
        """Converte métricas para os nomes de campos esperados pela Edge Function."""
        return {
            "total_municipios": self.total_municipalities,
            "total_ok": self.found,
            "total_nao_encontrado": self.not_found,
            "total_ambiguo": self.ambiguous,
            "total_erro_api": self.api_errors,
            "pop_total_ok": self.total_population,
            "medias_por_regiao": self.average_by_region,
        }


@dataclass(frozen=True)
class ProcessedMunicipalities:
    """Resultados do processamento e estatísticas calculadas para o lote."""

    results: tuple[MunicipalityResult, ...]
    statistics: MunicipalityStatistics
    publishing_error: str | None = None
