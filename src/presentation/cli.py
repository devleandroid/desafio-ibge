"""Apresenta o resultado do caso de uso no terminal."""

from pathlib import Path

from application.errors import ApplicationError
from application.use_cases import ProcessMunicipalityCsv


def run_challenge(
    use_case: ProcessMunicipalityCsv,
    input_path: Path,
    output_path: Path,
) -> int:
    """Executa o caso de uso e transforma seus resultados em mensagens ao usuário."""
    try:
        result = use_case.execute(input_path, output_path)
    except ApplicationError as error:
        print(f"❌ {error}")
        return 1

    print(f"✅ {len(result.results)} municípios processados.")
    print(f"📄 Resultado salvo em: {output_path}")
    print("Estatísticas calculadas:", result.statistics.to_mapping())
    if result.publishing_error:
        print(
            "⚠️ O resultado local foi salvo, mas o envio falhou: "
            f"{result.publishing_error}"
        )
    else:
        print("✅ Estatísticas enviadas ao Supabase.")
    return 0
