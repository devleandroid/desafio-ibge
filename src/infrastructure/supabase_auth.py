"""Adaptador de autenticação de usuário pela API Auth do Supabase."""

import requests

from application.errors import AuthenticationError
from infrastructure.config import SupabaseSettings


class SupabaseAuthenticator:
    """Obtém tokens de acesso usando credenciais configuradas no ambiente."""

    def __init__(self, settings: SupabaseSettings, session=requests) -> None:
        """Recebe credenciais e permite injetar uma sessão HTTP nos testes."""
        self._settings = settings
        self._session = session

    def authenticate(self, email: str, password: str) -> str:
        """Autentica o usuário e retorna o token de acesso do Supabase."""
        try:
            response = self._session.post(
                f"{self._settings.url}/auth/v1/token?grant_type=password",
                json={"email": email, "password": password},
                headers={
                    "apikey": self._settings.anon_key,
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token") if isinstance(payload, dict) else None
        except (requests.exceptions.RequestException, ValueError, AttributeError) as error:
            raise AuthenticationError(f"Falha de autenticação no Supabase: {error}") from error
        if not isinstance(token, str) or not token:
            raise AuthenticationError(
                "A resposta de login não contém um token de acesso."
            )
        return token
