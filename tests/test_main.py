"""Testes unitários para o desafio IBGE."""

import unittest
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processor import normalizar, encontrar_municipio
from stats import calcular_estatisticas


class TestNormalizacao(unittest.TestCase):
    """Testes para função de normalização de texto."""
    
    def test_remover_acentos(self):
        """Testa remoção de acentos."""
        self.assertEqual(normalizar("São Paulo"), "sao paulo")
        self.assertEqual(normalizar("João Pessoa"), "joao pessoa")
        self.assertEqual(normalizar("Cuiabá"), "cuiaba")
    
    def test_lowercase(self):
        """Testa conversão para minúsculas."""
        self.assertEqual(normalizar("NITEROI"), "niteroi")
        self.assertEqual(normalizar("Rio De Janeiro"), "rio de janeiro")
    
    def test_texto_com_espacos(self):
        """Testa remoção de espaços externos e compactação dos espaços internos."""
        self.assertEqual(normalizar("  Santo  André  "), "santo andre")
    
    def test_caracteres_especiais(self):
        """Testa remoção de caracteres especiais."""
        self.assertEqual(normalizar("São Gonçalo"), "sao goncalo")
        self.assertEqual(normalizar("Presidente Prudente"), "presidente prudente")


class TestMatching(unittest.TestCase):
    """Testes para função de matching de municípios."""
    
    def setUp(self):
        """Configura dados de exemplo do IBGE."""
        self.lista_ibge = [
            {"nome": "Niterói", "uf": "RJ", "regiao": "Sudeste", "id_ibge": 3303300},
            {"nome": "São Paulo", "uf": "SP", "regiao": "Sudeste", "id_ibge": 3550308},
            {"nome": "Rio de Janeiro", "uf": "RJ", "regiao": "Sudeste", "id_ibge": 3304557},
            {"nome": "Belo Horizonte", "uf": "MG", "regiao": "Sudeste", "id_ibge": 3106200},
        ]
    
    def test_match_exato(self):
        """Testa matching exato após normalização."""
        status, dados = encontrar_municipio("Niteroi", self.lista_ibge)
        self.assertEqual(status, "OK")
        self.assertEqual(dados["nome"], "Niterói")
    
    def test_match_sem_acento(self):
        """Testa matching sem acentos no input."""
        status, dados = encontrar_municipio("Sao Paulo", self.lista_ibge)
        self.assertEqual(status, "OK")
        self.assertEqual(dados["nome"], "São Paulo")
    
    def test_nao_encontrado(self):
        """Testa município não encontrado."""
        status, dados = encontrar_municipio("Cidade Inexistente", self.lista_ibge)
        self.assertEqual(status, "NAO_ENCONTRADO")
        self.assertIsNone(dados)

    def test_municipio_ambiguo(self):
        """Testa que nomes repetidos são reportados como ambíguos."""
        lista_duplicada = self.lista_ibge + [
            {"nome": "Niterói", "uf": "AM", "regiao": "Norte", "id_ibge": 1300000}
        ]
        status, dados = encontrar_municipio("Niteroi", lista_duplicada)
        self.assertEqual(status, "AMBIGUO")
        self.assertIsNone(dados)


class TestEstatisticas(unittest.TestCase):
    """Testes para cálculo de estatísticas."""
    
    def test_calculo_basico(self):
        """Testa cálculo básico de estatísticas."""
        resultados = [
            {"status": "OK", "populacao_input": "1000", "regiao": "Sudeste"},
            {"status": "OK", "populacao_input": "2000", "regiao": "Sudeste"},
            {"status": "NAO_ENCONTRADO", "populacao_input": "3000", "regiao": ""},
            {"status": "OK", "populacao_input": "3000", "regiao": "Sul"},
        ]
        
        stats = calcular_estatisticas(resultados)
        
        self.assertEqual(stats["total_municipios"], 4)
        self.assertEqual(stats["total_ok"], 3)
        self.assertEqual(stats["total_nao_encontrado"], 1)
        self.assertEqual(stats["total_ambiguo"], 0)
        self.assertEqual(stats["pop_total_ok"], 6000)
        self.assertEqual(stats["medias_por_regiao"]["Sudeste"], 1500.0)
        self.assertEqual(stats["medias_por_regiao"]["Sul"], 3000.0)
    
    def test_sem_municipios_ok(self):
        """Testa quando nenhum município é encontrado."""
        resultados = [
            {"status": "NAO_ENCONTRADO", "populacao_input": "1000", "regiao": ""},
            {"status": "ERRO_API", "populacao_input": "2000", "regiao": ""},
        ]
        
        stats = calcular_estatisticas(resultados)
        
        self.assertEqual(stats["total_ok"], 0)
        self.assertEqual(stats["total_ambiguo"], 0)
        self.assertEqual(stats["pop_total_ok"], 0)
        self.assertEqual(stats["medias_por_regiao"], {})

    def test_contagem_de_municipio_ambiguo(self):
        """Testa a contagem de entradas com nome ambíguo."""
        stats = calcular_estatisticas([
            {"status": "AMBIGUO", "populacao_input": "1000", "regiao": ""}
        ])
        self.assertEqual(stats["total_ambiguo"], 1)

    def test_multiplas_regioes(self):
        """Testa cálculo de médias para múltiplas regiões."""
        resultados = [
            {"status": "OK", "populacao_input": "1000", "regiao": "Sudeste"},
            {"status": "OK", "populacao_input": "3000", "regiao": "Sudeste"},
            {"status": "OK", "populacao_input": "2000", "regiao": "Sul"},
            {"status": "OK", "populacao_input": "4000", "regiao": "Sul"},
        ]
        
        stats = calcular_estatisticas(resultados)
        
        self.assertEqual(len(stats["medias_por_regiao"]), 2)
        self.assertEqual(stats["medias_por_regiao"]["Sudeste"], 2000.0)
        self.assertEqual(stats["medias_por_regiao"]["Sul"], 3000.0)


if __name__ == "__main__":
    # Executar testes
    unittest.main(verbosity=2)
