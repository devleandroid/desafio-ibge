"""Adaptador HTTP para publicar estatísticas na Edge Function do Supabase."""

import requests

from application.errors import StatisticsPublishingError
from domain.models import MunicipalityStatistics
from infrastructure.config import SupabaseSettings


class SupabaseStatisticsPublisher:
    """Envia estatísticas em nome do usuário autenticado."""

    def __init__(self, settings: SupabaseSettings, session=requests) -> None:
        """Recebe configuração e sessão HTTP, facilitando o isolamento nos testes."""
        self._settings = settings
        self._session = session

    def publish(
        self, access_token: str, statistics: MunicipalityStatistics
    ) -> None:
        """Envia o payload no formato esperado pela função `ibge-submit`."""
        if not access_token:
            raise StatisticsPublishingError("Token de acesso ausente.")
        try:
            response = self._session.post(
                f"{self._settings.url}/functions/v1/ibge-submit",
                json={"stats": statistics.to_mapping()},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "apikey": self._settings.anon_key,
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise StatisticsPublishingError(
                f"Falha ao enviar estatísticas ao Supabase: {error}"
            ) from error
