"""Testes unitários para envio de estatísticas ao Supabase."""

import unittest
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

# Permite executar este módulo isoladamente, sem depender da ordem de descoberta.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import submitter


class TestEnvioEstatisticas(unittest.TestCase):
    """Verifica a autenticação enviada à Edge Function."""

    @patch("submitter.requests.post")
    def test_envia_token_bearer_e_chave_publica(self, post):
        """Envia o token como Bearer sem expô-lo nos logs."""
        post.return_value.status_code = 204
        post.return_value.text = ""
        stats = {"total_municipios": 1}
        token = "jwt-de-teste"

        saida = StringIO()
        with patch.object(submitter, "SUPABASE_URL", "https://projeto.supabase.co/"), \
             patch.object(submitter, "SUPABASE_ANON_KEY", "chave-publica"), \
             redirect_stdout(saida):
            submitter.enviar_estatisticas(token, stats)

        self.assertNotIn(token, saida.getvalue())
        argumentos = post.call_args.kwargs
        self.assertEqual(
            argumentos["headers"]["Authorization"],
            f"Bearer {token}",
        )
        self.assertEqual(argumentos["headers"]["apikey"], "chave-publica")
        self.assertEqual(argumentos["json"], {"stats": stats})
        self.assertEqual(argumentos["timeout"], 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
