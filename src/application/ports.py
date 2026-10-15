"""Contratos dos adaptadores externos necessários ao caso de uso principal."""

from pathlib import Path
from typing import Protocol

from domain.models import (
    Municipality,
    MunicipalityInput,
    MunicipalityResult,
    MunicipalityStatistics,
)


class AuthenticationPort(Protocol):
    """Autentica o usuário e retorna um token para a integração Supabase."""

    def authenticate(self, email: str, password: str) -> str:
        """Retorna um token ou informa a falha de autenticação."""
        ...


class MunicipalityCatalogPort(Protocol):
    """Fornece os municípios oficiais usados pela regra de matching."""

    def load(self) -> list[Municipality]:
        """Carrega o catálogo oficial utilizado pelo caso de uso."""
        ...


class CsvPort(Protocol):
    """Lê entradas e grava resultados no formato CSV."""

    def read(self, path: Path) -> list[MunicipalityInput]:
        """Lê e valida as linhas de entrada do arquivo indicado."""
        ...

    def write(self, path: Path, results: list[MunicipalityResult]) -> None:
        """Persiste os resultados no arquivo indicado."""
        ...


class StatisticsPublisherPort(Protocol):
    """Publica estatísticas calculadas usando um token autenticado."""

    def publish(
        self, access_token: str, statistics: MunicipalityStatistics
    ) -> None:
        """Publica estatísticas ou levanta erro de integração."""
        ...
