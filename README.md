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

### Persistência das estatísticas no Supabase

O diretório `supabase/` contém a migração da tabela `public.ibge_statistics`
e a Edge Function `ibge-submit`. A função valida o JWT do usuário, verifica o
payload e grava as métricas com `user_id`; RLS limita a leitura e a inserção
aos registros do próprio usuário. A chave `service_role` não é usada.

Com a Supabase CLI instalada e vinculada ao projeto correto, aplique a migração
e implante a função:

```bash
supabase link --project-ref SEU_PROJECT_REF
supabase db push
supabase functions deploy ibge-submit
```

Para conferir os dados depois de executar `python src/main.py`, use o SQL
Editor:

```sql
select id, user_id, total_municipios, total_ok, total_nao_encontrado,
       total_ambiguo, total_erro_api, pop_total_ok, medias_por_regiao, created_at
from public.ibge_statistics
order by created_at desc
limit 20;
```

Os testes da validação da Edge Function podem ser executados com
`deno test supabase/functions/ibge-submit/validation_test.ts`.

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

### Erro de certificado TLS ao consultar o IBGE

O cliente valida certificados HTTPS e respeita `REQUESTS_CA_BUNDLE`, variável
padrão do Requests. Como a API do IBGE pode não enviar o intermediário Sectigo
R36, o adaptador combina o bundle confiável do Requests (ou o caminho configurado
em `REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE`) com o certificado intermediário
versionado em `src/infrastructure/certs/`. A validação da cadeia HTTPS continua
ativa; não use `verify=False`.
