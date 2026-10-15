"""Compatibilidade para consumidores das funções anteriores de processamento."""

from pathlib import Path

from domain.models import Municipality, MunicipalityInput, MunicipalityResult
from domain.services import find_municipality, normalize_municipality_name
from infrastructure.csv_gateway import CsvFileGateway


def normalizar(texto: str) -> str:
    """Normaliza o texto mantendo o nome público da função legado."""
    return normalize_municipality_name(texto)


def encontrar_municipio(nome_input, lista_ibge):
    """Executa matching e mantém o retorno legado de status e dicionário."""
    catalog = [Municipality.from_mapping(item) for item in lista_ibge]
    status, municipality = find_municipality(nome_input, catalog)
    return status.value, municipality.to_mapping() if municipality else None


def processar(input_csv_path, output_csv_path, lista_ibge):
    """Processa CSV com o novo domínio e mantém a assinatura histórica."""
    input_path = Path(input_csv_path)
    output_path = Path(output_csv_path)
    project_root = Path(__file__).resolve().parent.parent
    if not input_path.is_absolute():
        input_path = project_root / input_path
    if not output_path.is_absolute():
        output_path = project_root / output_path

    gateway = CsvFileGateway()
    input_rows = gateway.read(input_path)
    catalog = [Municipality.from_mapping(item) for item in lista_ibge]
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
    gateway.write(output_path, results)
    return [result.to_mapping() for result in results]
