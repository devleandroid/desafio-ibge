"""Testes das fronteiras entre domínio, aplicação e adaptadores Python."""

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from application.errors import CsvInputError, StatisticsPublishingError
from application.use_cases import ProcessMunicipalityCsv
from domain.models import Municipality, MunicipalityInput, MunicipalityResult, MunicipalityStatus
from domain.services import calculate_statistics, find_municipality
from infrastructure.config import AppSettings
from infrastructure.csv_gateway import CsvFileGateway
from infrastructure.ibge_client import IbgeMunicipalityClient


class DomainRulesTest(unittest.TestCase):
    """Verifica regras de domínio sem carregar dependências externas."""

    def test_classifica_nomes_ausentes_duplicados_e_unicos(self):
        """Diferencia município único, inexistente e ambíguo."""
        catalog = [
            Municipality("São Paulo", "SP", "Sudeste", 3550308),
            Municipality("Niterói", "RJ", "Sudeste", 3303302),
            Municipality("Niteroi", "AM", "Norte", 1300000),
        ]

        status, municipality = find_municipality("  Sao Paulo ", catalog)
        self.assertEqual(status, MunicipalityStatus.OK)
        self.assertEqual(municipality.name, "São Paulo")
        self.assertEqual(
            find_municipality("Niteroi", catalog),
            (MunicipalityStatus.AMBIGUOUS, None),
        )
        self.assertEqual(
            find_municipality("Curitiba", catalog),
            (MunicipalityStatus.NOT_FOUND, None),
        )

    def test_calcula_totais_e_medias_apenas_para_correspondencias(self):
        """Ignora municípios não encontrados ao calcular população e médias."""
        rows = [
            MunicipalityResult(
                "Niteroi", "100", MunicipalityStatus.OK,
                Municipality("Niterói", "RJ", "Sudeste", 3303302),
            ),
            MunicipalityResult("Ausente", "999", MunicipalityStatus.NOT_FOUND),
        ]

        self.assertEqual(
            calculate_statistics(rows).to_mapping(),
            {
                "total_municipios": 2,
                "total_ok": 1,
                "total_nao_encontrado": 1,
                "total_ambiguo": 0,
                "total_erro_api": 0,
                "pop_total_ok": 100,
                "medias_por_regiao": {"Sudeste": 100.0},
            },
        )


class CsvGatewayTest(unittest.TestCase):
    """Valida leitura, dados inválidos e geração do CSV processado."""

    def test_le_e_escreve_csv_com_acentos_e_cabecalhos_padrao(self):
        """Mantém os dados do município e as colunas públicas do resultado."""
        gateway = CsvFileGateway()
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "input.csv"
            target = Path(temporary_directory) / "out" / "resultado.csv"
            source.write_text("municipio,populacao\nNiterói,100\n", encoding="utf-8")
            input_rows = gateway.read(source)
            result = MunicipalityResult(
                input_rows[0].name,
                input_rows[0].population,
                MunicipalityStatus.OK,
                Municipality("Niterói", "RJ", "Sudeste", 3303302),
            )

            gateway.write(target, [result])

            with target.open(encoding="utf-8", newline="") as saved:
                output = list(csv.DictReader(saved))
            self.assertEqual(output[0]["municipio_ibge"], "Niterói")
            self.assertEqual(output[0]["id_ibge"], "3303302")
            self.assertEqual(output[0]["status"], "OK")

    def test_rejeita_cabecalho_ou_populacao_invalidos(self):
        """Apresenta erro de entrada claro antes de iniciar o matching."""
        gateway = CsvFileGateway()
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "input.csv"
            source.write_text("cidade,pessoas\nRio,100\n", encoding="utf-8")
            with self.assertRaises(CsvInputError):
                gateway.read(source)

            source.write_text("municipio,populacao\nRio,-1\n", encoding="utf-8")
            with self.assertRaises(CsvInputError):
                gateway.read(source)


class ProcessMunicipalityCsvTest(unittest.TestCase):
    """Garante coordenação correta e independência de serviços reais."""

    def setUp(self):
        """Prepara adaptadores falsos para testar o fluxo de aplicação."""
        self.authenticator = Mock()
        self.authenticator.authenticate.return_value = "token-de-teste"
        self.catalog = Mock()
        self.catalog.load.return_value = [
            Municipality("Niterói", "RJ", "Sudeste", 3303302)
        ]
        self.csv_gateway = Mock()
        self.csv_gateway.read.return_value = [MunicipalityInput("Niteroi", "100")]
        self.publisher = Mock()
        self.use_case = ProcessMunicipalityCsv(
            authenticator=self.authenticator,
            catalog=self.catalog,
            csv_gateway=self.csv_gateway,
            statistics_publisher=self.publisher,
            email="user@example.com",
            password="senha",
        )

    def test_processa_grava_e_publica_estatisticas(self):
        """Executa as portas na sequência e retorna o lote calculado."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "input.csv"
            input_path.touch()
            output_path = Path(temporary_directory) / "resultado.csv"

            result = self.use_case.execute(input_path, output_path)

        self.authenticator.authenticate.assert_called_once_with(
            "user@example.com", "senha"
        )
        self.csv_gateway.write.assert_called_once()
        self.publisher.publish.assert_called_once_with(
            "token-de-teste", result.statistics
        )
        self.assertEqual(result.results[0].status, MunicipalityStatus.OK)

    def test_falha_no_envio_preserva_resultado_local(self):
        """Retém o resultado local e comunica falha de publicação."""
        self.publisher.publish.side_effect = StatisticsPublishingError(
            "serviço indisponível"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "input.csv"
            input_path.touch()
            result = self.use_case.execute(
                input_path, Path(temporary_directory) / "resultado.csv"
            )

        self.csv_gateway.write.assert_called_once()
        self.assertEqual(result.publishing_error, "serviço indisponível")

    def test_arquivo_ausente_nao_autentica(self):
        """Valida o caminho de entrada antes de chamar qualquer serviço."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(CsvInputError):
                self.use_case.execute(
                    Path(temporary_directory) / "missing.csv",
                    Path(temporary_directory) / "out.csv",
                )
        self.authenticator.authenticate.assert_not_called()


class ConfigurationAndIbgeAdapterTest(unittest.TestCase):
    """Verifica configuração Supabase e conversão da resposta do IBGE."""

    def test_rejeita_configuracao_supabase_parcial(self):
        """Falha cedo em vez de inicializar integrações sem credenciais completas."""
        with self.assertRaisesRegex(ValueError, "SUPABASE_ANON_KEY"):
            AppSettings.from_environment(
                {
                    "SUPABASE_URL": "https://projeto.supabase.co",
                    "MY_EMAIL": "usuario",
                    "MY_PASSWORD": "senha",
                }
            )

    def test_converte_hierarquia_ibge_e_distrito_federal(self):
        """Converte municípios comuns e DF, que não possui microrregião."""
        session = Mock()
        session.get.return_value.json.return_value = [
            {
                "id": 3303302,
                "nome": "Niterói",
                "microrregiao": {
                    "mesorregiao": {
                        "UF": {
                            "sigla": "RJ",
                            "regiao": {"nome": "Sudeste"},
                        }
                    }
                },
            },
            {"id": 5300108, "nome": "Brasília", "microrregiao": None},
        ]
        municipalities = IbgeMunicipalityClient(session=session).load()

        self.assertEqual(municipalities[0].region, "Sudeste")
        self.assertEqual(municipalities[1].state, "DF")
        self.assertEqual(municipalities[1].region, "Centro-Oeste")


if __name__ == "__main__":
    unittest.main()
