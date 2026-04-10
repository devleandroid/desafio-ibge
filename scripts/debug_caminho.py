import os

print("Diretório atual:", os.getcwd())
print("Arquivos na pasta atual:", os.listdir("."))

if os.path.exists("data"):
    print("✅ Pasta 'data' existe")
    print("Conteúdo de 'data':", os.listdir("data"))
    
    if os.path.exists("data/input.csv"):
        print("✅ Arquivo data/input.csv existe")
        with open("data/input.csv", "r") as f:
            print("Conteúdo:")
            print(f.read())
    else:
        print("❌ data/input.csv NÃO existe")
else:
    print("❌ Pasta 'data' NÃO existe")