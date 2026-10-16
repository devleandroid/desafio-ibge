"""Adaptador HTTP que carrega e converte o catálogo oficial de municípios."""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from collections.abc import Iterator

import requests

from application.errors import MunicipalityCatalogError
from domain.models import Municipality

IBGE_MUNICIPALITIES_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
)
SECTIGO_INTERMEDIATE_CERTIFICATE = (
    Path(__file__).resolve().parent
    / "certs"
    / "sectigo-public-server-authentication-ca-dv-r36.pem"
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
            with self._trusted_ca_bundle() as ca_bundle:
                response = self._session.get(
                    IBGE_MUNICIPALITIES_URL,
                    timeout=self._timeout,
                    verify=ca_bundle,
                )
                response.raise_for_status()
                payload = response.json()
        except requests.exceptions.SSLError as error:
            raise MunicipalityCatalogError(
                "Falha na validação TLS da API do IBGE. Verifique a cadeia de "
                "certificados do servidor ou configure REQUESTS_CA_BUNDLE com "
                f"um bundle de CAs confiável. A verificação TLS permanece ativa. ({error})"
            ) from error
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

    @contextmanager
    def _trusted_ca_bundle(self) -> Iterator[str]:
        """Combina CAs do Requests com o intermediário ausente na cadeia do IBGE."""
        configured_bundle = (
            os.environ.get("REQUESTS_CA_BUNDLE")
            or os.environ.get("CURL_CA_BUNDLE")
            or requests.certs.where()
        )
        with tempfile.TemporaryDirectory(prefix="desafio-ibge-ca-") as directory:
            bundle = Path(directory) / "ca-bundle.pem"
            try:
                bundle.write_bytes(
                    Path(configured_bundle).read_bytes()
                    + b"\n"
                    + SECTIGO_INTERMEDIATE_CERTIFICATE.read_bytes()
                    + b"\n"
                )
            except OSError as error:
                raise MunicipalityCatalogError(
                    "Não foi possível preparar o bundle de certificados TLS: "
                    f"{error}"
                ) from error
            yield str(bundle)

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
