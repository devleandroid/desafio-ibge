"""Casos de uso que orquestram o processamento de municípios sem I/O concreto."""

from pathlib import Path

from application.errors import CsvInputError, StatisticsPublishingError
from application.ports import (
    AuthenticationPort,
    CsvPort,
    MunicipalityCatalogPort,
    StatisticsPublisherPort,
)
from domain.models import (
    Municipality,
    MunicipalityInput,
    MunicipalityResult,
    ProcessedMunicipalities,
)
from domain.services import calculate_statistics, find_municipality


class ProcessMunicipalityCsv:
    """Autentica, processa o CSV, persiste a saída e publica as estatísticas."""

    def __init__(
        self,
        authenticator: AuthenticationPort,
        catalog: MunicipalityCatalogPort,
        csv_gateway: CsvPort,
        statistics_publisher: StatisticsPublisherPort,
        email: str,
        password: str,
    ) -> None:
        """Recebe dependências por contrato para permitir testes sem serviços reais."""
        self._authenticator = authenticator
        self._catalog = catalog
        self._csv_gateway = csv_gateway
        self._statistics_publisher = statistics_publisher
        self._email = email
        self._password = password

    def execute(self, input_path: Path, output_path: Path) -> ProcessedMunicipalities:
        """Executa o fluxo completo e devolve os resultados para apresentação."""
        if not input_path.is_file():
            raise CsvInputError(f"Arquivo não encontrado: {input_path}")

        access_token = self._authenticator.authenticate(self._email, self._password)
        catalog = self._catalog.load()
        input_rows = self._csv_gateway.read(input_path)
        results = tuple(self._match_rows(input_rows, catalog))
        statistics = calculate_statistics(results)

        self._csv_gateway.write(output_path, list(results))
        publishing_error = None
        try:
            self._statistics_publisher.publish(access_token, statistics)
        except StatisticsPublishingError as error:
            publishing_error = str(error)
        return ProcessedMunicipalities(
            results=results,
            statistics=statistics,
            publishing_error=publishing_error,
        )

    @staticmethod
    def _match_rows(
        input_rows: list[MunicipalityInput],
        catalog: list[Municipality],
    ) -> list[MunicipalityResult]:
        """Aplica matching a cada linha sem alterar os dados recebidos."""
        results = []
        for input_row in input_rows:
            status, municipality = find_municipality(input_row.name, catalog)
            results.append(
                MunicipalityResult(
                    input_name=input_row.name,
                    input_population=input_row.population,
                    status=status,
                    municipality=municipality,
                )
            )
        return results
