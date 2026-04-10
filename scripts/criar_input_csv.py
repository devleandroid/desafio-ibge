import os

# Criar pasta data
os.makedirs("data", exist_ok=True)

# Dados do CSV
cabecalho = "municipio,populacao\n"
dados = [
    "Niteroi,515317",
    "Sao Goncalo,1091737",
    "Sao Paulo,12396372",
    "Belo Horizonte,2530701",
    "Florianopolis,516524",
    "Santo Andre,723889",
    "Santoo Andre,700000",
    "Rio de Janeiro,6718903",
    "Curitba,1963726",
    "Brasilia,3094325"
]

# Escrever arquivo
with open("data/input.csv", "w", encoding="utf-8") as f:
    f.write(cabecalho)
    f.write("\n".join(dados))

print("✅ Arquivo data/input.csv criado com sucesso!")
print("\nConteúdo do arquivo:")
print("=" * 40)
with open("data/input.csv", "r") as f:
    print(f.read())
print("=" * 40)