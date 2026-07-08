import unittest
from io import StringIO
from unittest.mock import patch
import Main

class TestSOAdversarialScenarios(unittest.TestCase):

    def test_cenario_otimo(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioOtimo/processes.txt",
            "Testes/CenariosAdversarios/CenarioOtimo/files.txt",
            "Testes/CenariosAdversarios/CenarioOtimo/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        self.assertIn("P0 = 2 faltas de páginas", output.getvalue())
        self.assertIn("P1 = 7 faltas de páginas", output.getvalue())

    def test_cenario_estouro_memoria(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioEstouroMemoria/processes.txt",
            "Testes/CenariosAdversarios/CenarioEstouroMemoria/files.txt",
            "Testes/CenariosAdversarios/CenarioEstouroMemoria/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("dispatcher => Processo 0 rejeitado: working set maior que a área de memória permitida.", text)

    def test_cenario_acesso_memoria_proibido(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioAcessoMemoriaProibido/processes.txt",
            "Testes/CenariosAdversarios/CenarioAcessoMemoriaProibido/files.txt",
            "Testes/CenariosAdversarios/CenarioAcessoMemoriaProibido/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        self.assertIn("dispatcher => Processo 0 rejeitado: acesso de memória fora dos limites (Segmentation Fault).", output.getvalue())

    def test_cenario_recursos_indisponiveis(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioRecursosIndisponiveis/processes.txt",
            "Testes/CenariosAdversarios/CenarioRecursosIndisponiveis/files.txt",
            "Testes/CenariosAdversarios/CenarioRecursosIndisponiveis/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        self.assertIn("dispatcher => Processo 0 rejeitado: requer mais recursos do que o possúido pelo sistema.", output.getvalue())

    def test_cenario_conflito_pid(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioConflitoPid/processes.txt",
            "Testes/CenariosAdversarios/CenarioConflitoPid/files.txt",
            "Testes/CenariosAdversarios/CenarioConflitoPid/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("O processo 2 não pode deletar o arquivo A porque não é o dono.", text)
        self.assertIn("O processo 1 não pode deletar o arquivo Y porque não foi criado por ele.", text)
        self.assertIn("O processo 0 deletou o arquivo Y.", text)
        self.assertIn("O processo 99 não existe.", text)
        self.assertIn("O processo -1 não existe.", text)
        self.assertIn("O processo 1 não pode criar o arquivo A (arquivo já existe).", text)

    def test_cenario_limite_maximo(self) -> None:
        argv = [
            "Main.py",
            "Testes/CenariosAdversarios/CenarioLimiteMaximo/processes.txt",
            "Testes/CenariosAdversarios/CenarioLimiteMaximo/files.txt",
            "Testes/CenariosAdversarios/CenarioLimiteMaximo/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("O processo 1 criou o arquivo A (blocos 1023).", text)
        self.assertIn("O processo 1 não pode criar o arquivo B (falta de espaço).", text)
        self.assertIn("O processo 2 criou o arquivo C (blocos 1023).", text)
        self.assertIn("P999 = 0 faltas de páginas", text)

if __name__ == '__main__':
    unittest.main()
