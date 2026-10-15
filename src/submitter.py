"""Compatibilidade para publicação Supabase usando a função anterior."""

from dotenv import load_dotenv

from application.errors import StatisticsPublishingError
from domain.models import MunicipalityStatistics
from infrastructure.config import AppSettings
from infrastructure.supabase_submitter import SupabaseStatisticsPublisher


def enviar_estatisticas(access_token, stats):
    """Publica estatísticas e comunica falhas sem descartar o resultado local."""
    load_dotenv()
    settings = AppSettings.from_environment().supabase
    if settings is None:
        print("❌ Configure as credenciais do Supabase no arquivo .env.")
        return
    domain_statistics = MunicipalityStatistics(
        total_municipalities=stats["total_municipios"],
        found=stats["total_ok"],
        not_found=stats["total_nao_encontrado"],
        ambiguous=stats["total_ambiguo"],
        api_errors=stats.get("total_erro_api", 0),
        total_population=stats["pop_total_ok"],
        average_by_region=stats["medias_por_regiao"],
    )
    try:
        SupabaseStatisticsPublisher(settings).publish(access_token, domain_statistics)
    except StatisticsPublishingError as error:
        print(f"❌ {error}")
        return
    print("✅ Estatísticas enviadas com sucesso!")
