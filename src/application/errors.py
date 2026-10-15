"""Exceções explícitas para falhas esperadas ao executar casos de uso."""


class ApplicationError(Exception):
    """Erro-base apresentado pela camada de aplicação."""


class CsvInputError(ApplicationError):
    """O CSV está ausente, malformado ou não contém os dados esperados."""


class CsvOutputError(ApplicationError):
    """O arquivo de resultados não pôde ser gravado."""


class AuthenticationError(ApplicationError):
    """A autenticação do usuário no Supabase não foi concluída."""


class MunicipalityCatalogError(ApplicationError):
    """O catálogo de municípios não pôde ser consultado."""


class StatisticsPublishingError(ApplicationError):
    """As estatísticas não puderam ser enviadas ao Supabase."""
