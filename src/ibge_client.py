"""Compatibilidade para a função histórica de carregamento do catálogo IBGE."""

from infrastructure.ibge_client import IbgeMunicipalityClient


def carregar_municipios_ibge():
    """Carrega o catálogo remoto e converte entidades ao formato de dicionário."""
    return [
        municipality.to_mapping()
        for municipality in IbgeMunicipalityClient().load()
    ]
