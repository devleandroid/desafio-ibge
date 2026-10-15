# Desafio técnico IBGE + Supabase (Python)

Esta pasta contém a implementação original em Python. A versão Kotlin com
servidor web e interface de upload foi desacoplada para
`../desafio-ibge-kotlin`.

## Configuração

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Crie `.env` com a URL e chave do projeto Supabase e as credenciais do usuário:

```dotenv
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anon
MY_EMAIL=seu_email
MY_PASSWORD=sua_senha
```

O arquivo `data/input.csv` precisa conter as colunas `municipio,populacao`.

## Executar e testar

```bash
python src/main.py
python -m unittest discover -v
```

O programa consulta a API do IBGE, grava `data/resultado.csv`, calcula as
estatísticas e tenta enviá-las à Edge Function `ibge-submit` do Supabase. São
necessários acesso à internet, credenciais válidas e a função implantada.

## Arquitetura e organização

O fluxo Python foi separado em camadas com dependências apontadas para regras
de negócio:

```text
src/
├── domain/          # Entidades, matching de municípios e estatísticas
├── application/     # Caso de uso e contratos (ports) para integrações
├── infrastructure/  # CSV, API IBGE, autenticação e publicação Supabase
├── presentation/    # Saída e interação de linha de comando
└── main.py          # Composição das dependências
```

O domínio não depende de HTTP, CSV ou Supabase. O caso de uso
`ProcessMunicipalityCsv` recebe os adaptadores por interfaces, o que permite
testá-lo com dependências simuladas. Os módulos `auth.py`, `processor.py`,
`stats.py`, `ibge_client.py` e `submitter.py` mantêm as funções públicas
anteriores como uma camada de compatibilidade. As funções públicas e regras
principais possuem docstrings descrevendo seu propósito.

Os testes usam a biblioteca `unittest` e não fazem chamadas reais às APIs.
A versão mínima de Python é 3.10.
