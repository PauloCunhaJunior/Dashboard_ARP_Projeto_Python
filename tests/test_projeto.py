import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import banco
from rede import dados_demonstracao, interpretar_arp
from relatorio import gerar_html


class TestesDashboardARP(unittest.TestCase):
    def test_interpretacao_em_portugues(self):
        texto = """Interface: 192.168.1.100 --- 0x9
          Endereço IP  Endereço físico  Tipo
          192.168.1.1 AA-BB-CC-12-34-56 dinâmico
          192.168.1.4 00-11-22-33-44-55 estático
          224.0.0.22 01-00-5E-00-00-16 estático
          255.255.255.255 FF-FF-FF-FF-FF-FF estático
"""
        resultado = interpretar_arp(texto)
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]["tipo"], "Dinâmico")
        self.assertEqual(resultado[1]["tipo"], "Estático")
        self.assertEqual(resultado[0]["interface"], "192.168.1.100")

    def test_interpretacao_em_ingles(self):
        texto = """Interface: 10.1.2.3 --- 0xf
          Internet Address  Physical Address Type
          10.1.2.1 01-23-45-67-89-AB dynamic
          10.1.2.2 01-23-45-67-89-AC static
"""
        resultado = interpretar_arp(texto)
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]["tipo"], "Dinâmico")
        self.assertEqual(resultado[1]["tipo"], "Estático")

    def test_exemplo_ficticio(self):
        self.assertEqual(len(dados_demonstracao()), 4)

    def test_banco_e_relatorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            with patch.object(banco, "ARQUIVO_BANCO", Path(pasta) / "teste.sqlite"):
                banco.inicializar_banco()
                amostra = dados_demonstracao()
                banco.salvar_coleta(amostra, "demo")
                banco.salvar_coleta(amostra, "demo")
                ultimo, linhas = banco.ultima_coleta("demo")
                self.assertEqual(ultimo["total"], 4)
                self.assertEqual(len(linhas), 4)
                registro = linhas[0]
                historico = banco.obter_historico(registro["ip"], registro["mac"], "demo")
                self.assertEqual(historico["quantidade_coletas"], 2)
                html = gerar_html(registro, historico, ficticio=True)
                self.assertIn("Relatório executivo", html)
                self.assertIn("DADOS FICTÍCIOS", html)
                self.assertIn(registro["ip"], html)
                self.assertIsNone(banco.ultima_coleta("real")[0])


if __name__ == "__main__":
    unittest.main()
