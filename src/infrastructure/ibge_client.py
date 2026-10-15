"""Adaptador HTTP que carrega e converte o catálogo oficial de municípios."""

from typing import Any

import requests

from application.errors import MunicipalityCatalogError
from domain.models import Municipality

IBGE_MUNICIPALITIES_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
)


class IbgeMunicipalityClient:
    """Consulta a API do IBGE e converte respostas JSON em entidades de domínio."""

    def __init__(self, session=requests, timeout: int = 30) -> None:
        """Permite substituir a sessão HTTP em testes automatizados."""
        self._session = session
        self._timeout = timeout

    def load(self) -> list[Municipality]:
        """Baixa os municípios e trata estruturas incompletas com valores padrão."""
        try:
            response = self._session.get(IBGE_MUNICIPALITIES_URL, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            raise MunicipalityCatalogError(
                f"Não foi possível carregar municípios do IBGE: {error}"
            ) from error
        if not isinstance(payload, list):
            raise MunicipalityCatalogError("A API do IBGE retornou dados inválidos.")
        municipalities = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            municipality = self._parse_municipality(item)
            if municipality is not None:
                municipalities.append(municipality)
        if not municipalities:
            raise MunicipalityCatalogError("A API do IBGE não retornou municípios.")
        return municipalities

    @staticmethod
    def _parse_municipality(item: dict[str, Any]) -> Municipality | None:
        """Extrai município, UF, região e código sem depender da hierarquia completa."""
        name = item.get("nome")
        if not isinstance(name, str) or not name.strip():
            return None
        microregion = item.get("microrregiao")
        microregion = microregion if isinstance(microregion, dict) else {}
        mesoregion = microregion.get("mesorregiao")
        mesoregion = mesoregion if isinstance(mesoregion, dict) else {}
        state = mesoregion.get("UF")
        state = state if isinstance(state, dict) else {}
        region = state.get("regiao")
        region = region if isinstance(region, dict) else {}
        raw_id = item.get("id")
        ibge_id = raw_id if isinstance(raw_id, int) else None

        if ibge_id == 5300108:
            state_name = "DF"
            region_name = "Centro-Oeste"
        else:
            state_name = state.get("sigla", "Desconhecido")
            region_name = region.get("nome", "Desconhecido")
        return Municipality(
            name=name,
            state=state_name,
            region=region_name,
            ibge_id=ibge_id,
        )
