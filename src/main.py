"""Composição das dependências e início da execução pela linha de comando."""

from pathlib import Path

from dotenv import load_dotenv

from application.use_cases import ProcessMunicipalityCsv
from infrastructure.config import AppSettings
from infrastructure.csv_gateway import CsvFileGateway
from infrastructure.ibge_client import IbgeMunicipalityClient
from infrastructure.supabase_auth import SupabaseAuthenticator
from infrastructure.supabase_submitter import SupabaseStatisticsPublisher
from presentation.cli import run_challenge


def main() -> int:
    """Monta dependências concretas e entrega o fluxo à interface de terminal."""
    load_dotenv()
    try:
        settings = AppSettings.from_environment()
    except ValueError as error:
        print(f"❌ {error}")
        return 1
    if settings.supabase is None:
        print(
            "❌ Configure SUPABASE_URL, SUPABASE_ANON_KEY, MY_EMAIL e "
            "MY_PASSWORD no arquivo .env."
        )
        return 1

    data_directory = settings.project_root / "data"
    input_path = data_directory / "input.csv"
    output_path = data_directory / "resultado.csv"
    use_case = ProcessMunicipalityCsv(
        authenticator=SupabaseAuthenticator(settings.supabase),
        catalog=IbgeMunicipalityClient(),
        csv_gateway=CsvFileGateway(),
        statistics_publisher=SupabaseStatisticsPublisher(settings.supabase),
        email=settings.supabase.email,
        password=settings.supabase.password,
    )
    return run_challenge(use_case, input_path, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
