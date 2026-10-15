"""Adaptador de leitura e escrita CSV para os modelos da aplicação."""

import csv
from pathlib import Path

from application.errors import CsvInputError, CsvOutputError
from domain.models import MunicipalityInput, MunicipalityResult

INPUT_HEADERS = ("municipio", "populacao")
OUTPUT_HEADERS = (
    "municipio_input",
    "populacao_input",
    "municipio_ibge",
    "uf",
    "regiao",
    "id_ibge",
    "status",
)


class CsvFileGateway:
    """Implementa acesso ao CSV usando a biblioteca padrão do Python."""

    def read(self, path: Path) -> list[MunicipalityInput]:
        """Valida cabeçalhos e converte cada linha em uma entrada tipada."""
        try:
            with path.open(mode="r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                if reader.fieldnames is None or not set(INPUT_HEADERS).issubset(
                    reader.fieldnames
                ):
                    raise CsvInputError(
                        "O CSV deve conter as colunas municipio e populacao."
                    )
                rows = []
                for line_number, row in enumerate(reader, start=2):
                    name = (row.get("municipio") or "").strip()
                    population = (row.get("populacao") or "").strip()
                    if not name:
                        raise CsvInputError(
                            f"A linha {line_number} não informa o município."
                        )
                    try:
                        if int(population) < 0:
                            raise ValueError
                    except ValueError as error:
                        raise CsvInputError(
                            f"População inválida na linha {line_number}: "
                            "informe um inteiro não negativo."
                        ) from error
                    rows.append(MunicipalityInput(name, population))
        except UnicodeDecodeError as error:
            raise CsvInputError("O arquivo precisa estar codificado em UTF-8.") from error
        except OSError as error:
            raise CsvInputError(f"Não foi possível ler o arquivo: {path}") from error

        if not rows:
            raise CsvInputError("O CSV não contém linhas de dados.")
        return rows

    def write(self, path: Path, results: list[MunicipalityResult]) -> None:
        """Cria diretórios necessários e grava todas as colunas de resultado."""
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open(mode="w", encoding="utf-8", newline="") as destination:
                writer = csv.DictWriter(destination, fieldnames=OUTPUT_HEADERS)
                writer.writeheader()
                writer.writerows(result.to_mapping() for result in results)
        except OSError as error:
            raise CsvOutputError(
                f"Não foi possível gravar o arquivo: {path}"
            ) from error
