"""Testes unitários para envio de estatísticas ao Supabase."""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock

# Permite executar este módulo isoladamente, sem depender da ordem de descoberta.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.config import SupabaseSettings
from infrastructure.supabase_submitter import SupabaseStatisticsPublisher
from domain.models import MunicipalityStatistics


class TestEnvioEstatisticas(unittest.TestCase):
    """Verifica a autenticação enviada à Edge Function."""

    def test_envia_token_bearer_e_chave_publica(self):
        """Envia token Bearer e chave pública com o payload esperado."""
        session = Mock()
        session.post.return_value.raise_for_status.return_value = None
        stats = MunicipalityStatistics(1, 1, 0, 0, 0, 100, {"Sul": 100.0})
        token = "jwt-de-teste"
        settings = SupabaseSettings(
            url="https://projeto.supabase.co",
            anon_key="chave-publica",
            email="user@example.com",
            password="senha",
        )

        SupabaseStatisticsPublisher(settings, session=session).publish(token, stats)

        argumentos = session.post.call_args.kwargs
        self.assertEqual(
            argumentos["headers"]["Authorization"],
            "Bearer jwt-de-teste",
        )
        self.assertEqual(argumentos["headers"]["apikey"], "chave-publica")
        self.assertEqual(argumentos["json"], {"stats": stats.to_mapping()})
        self.assertEqual(argumentos["timeout"], 10)
        self.assertEqual(
            session.post.call_args.args[0],
            "https://projeto.supabase.co/functions/v1/ibge-submit",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
