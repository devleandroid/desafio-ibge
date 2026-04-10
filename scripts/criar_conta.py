from src.auth import criar_conta
from dotenv import load_dotenv

load_dotenv()

email = "leandro.hdsl@gmail.com"
senha = "@Senha23"
nome = "Leandro Marques"

criar_conta(email, senha, nome)