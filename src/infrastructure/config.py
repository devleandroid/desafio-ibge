"""Carrega e valida configurações externas antes de iniciar a aplicação."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SupabaseSettings:
    """Credenciais necessárias para autenticar e publicar estatísticas."""

    url: str
    anon_key: str
    email: str
    password: str


@dataclass(frozen=True)
class AppSettings:
    """Configuração do fluxo e caminhos de dados do projeto."""

    supabase: SupabaseSettings | None
    project_root: Path

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> "AppSettings":
        """Lê variáveis de ambiente e falha explicitamente quando incompletas."""
        values = os.environ if environment is None else environment
        project_root = Path(__file__).resolve().parents[2]
        required_keys = (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "MY_EMAIL",
            "MY_PASSWORD",
        )
        provided = [key for key in required_keys if values.get(key)]
        if not provided:
            return cls(supabase=None, project_root=project_root)
        missing = [key for key in required_keys if not values.get(key)]
        if missing:
            raise ValueError(
                "Configuração incompleta do Supabase; faltam: "
                + ", ".join(missing)
            )

        url = values["SUPABASE_URL"].strip().rstrip("/")
        if not url.startswith("https://"):
            raise ValueError("SUPABASE_URL deve usar HTTPS.")
        return cls(
            supabase=SupabaseSettings(
                url=url,
                anon_key=values["SUPABASE_ANON_KEY"].strip(),
                email=values["MY_EMAIL"].strip(),
                password=values["MY_PASSWORD"],
            ),
            project_root=project_root,
        )
