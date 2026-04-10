# Desafio Técnico - IBGE + Supabase

![Status](https://img.shields.io/badge/status-completed-brightgreen)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Supabase](https://img.shields.io/badge/supabase-integrated-green)
![License](https://img.shields.io/badge/license-private-red)

## 📋 Sobre o Projeto

Este projeto implementa uma solução completa para o desafio técnico que consiste em:

1. Autenticação no Supabase (criação de conta e login)
2. Leitura de um CSV com municípios e populações
3. Enriquecimento dos dados via API de Localidades do IBGE
4. Geração de um CSV com resultados detalhados
5. Cálculo de estatísticas (totais e médias por região)
6. Envio automático das estatísticas para uma Edge Function no Supabase

## 🚀 Tecnologias Utilizadas

- **Python 3.13** - Linguagem principal
- **Requests** - Chamadas HTTP para APIs
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **Supabase** - Backend e autenticação
- **IBGE API** - Dados de localidades

## 📦 Instalação

### 1. Clone o repositório

git clone https://github.com/seu-usuario/desafio-ibge.git
cd desafio-ibge

2. Crie um ambiente virtual


python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

3. Instale as dependências


pip install -r requirements.txt

4. Configure as variáveis de ambiente

Crie um arquivo .env na raiz do projeto:


SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anon
MY_EMAIL=seu_email
MY_PASSWORD=sua_senha

🎯 Como Executar


python src/main.py

📊 Resultados
Estatísticas Geradas

    Total de municípios processados: 10

    Municípios encontrados (OK): 7

    Municípios não encontrados: 2 (Santoo Andre, Curitba)

    População total dos municípios encontrados: 26.863.879

Médias por Região

    Sudeste: 4.650.606,00

    Sul: 516.524,00

    Centro-Oeste: 3.094.325,00

Arquivos Gerados

    data/resultado.csv - CSV com matching e status de cada município

    data/estatisticas.json - Estatísticas em formato JSON (se configurado)

🏗️ Estrutura do Projeto


desafio_ibge/
├── src/
│   ├── auth.py          # Autenticação Supabase
│   ├── ibge_client.py   # API do IBGE
│   ├── processor.py     # Matching e geração CSV
│   ├── stats.py         # Cálculo de estatísticas
│   ├── submitter.py     # Envio para Edge Function
│   └── main.py          # Orquestrador
├── data/
│   ├── input.csv        # Dados de entrada
│   └── resultado.csv    # Resultado gerado
├── .env                 # Configurações (não commitado)
├── requirements.txt     # Dependências
└── README.md           # Documentação

🔧 Decisões Técnicas
1. Matching de Municípios

    Normalização de texto (remoção de acentos, lower case)

    Busca exata após normalização

    Status possíveis: OK, NAO_ENCONTRADO, AMBIGUO, ERRO_API

2. Tratamento de Erros

    Timeout de 30 segundos para APIs externas

    Fallback para valores padrão quando dados do IBGE estão incompletos

    Logs detalhados para debug

3. Segurança

    Credenciais armazenadas em .env

    Token JWT enviado no header Authorization: Bearer

    Validação de token na Edge Function

🧪 Testes Realizados

✅ Criação de conta no Supabase
✅ Login e obtenção de token
✅ Leitura do CSV de entrada
✅ Consulta à API do IBGE (5.571 municípios)
✅ Matching e geração do resultado.csv
✅ Cálculo de estatísticas
✅ Envio para Edge Function
📝 Notas Importantes

    O projeto foi desenvolvido seguindo boas práticas de arquitetura limpa

    Cada módulo tem uma única responsabilidade

    Código comentado e documentado

    Tratamento robusto de erros e casos especiais

👨‍💻 Autor

Seu Nome - Leandro Marques

📄 Licença

Este projeto é privado e confidencial.
🎓 Agradecimentos

    Nasajon pelo desafio técnico

    Supabase pela infraestrutura

    IBGE pela API pública
