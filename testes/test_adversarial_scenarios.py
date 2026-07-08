import unittest
from io import StringIO
from unittest.mock import patch
import Main

class TestSOAdversarialScenarios(unittest.TestCase):

    def test_cenario_otimo(self) -> None:
        argv = [
            "Main.py",
            "testes/cenarios_adversarios/cenario_otimo/processes.txt",
            "testes/cenarios_adversarios/cenario_otimo/files.txt",
            "testes/cenarios_adversarios/cenario_otimo/string.txt"
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
            "testes/cenarios_adversarios/cenario_estouro_memoria/processes.txt",
            "testes/cenarios_adversarios/cenario_estouro_memoria/files.txt",
            "testes/cenarios_adversarios/cenario_estouro_memoria/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("P0 = 8 faltas de páginas", text)
        self.assertIn("P1 = 13 faltas de páginas", text)
        self.assertIn("O processo 0 criou o arquivo A", text)

    def test_cenario_acesso_memoria_proibido(self) -> None:
        argv = [
            "Main.py",
            "testes/cenarios_adversarios/cenario_acesso_memoria_proibido/processes.txt",
            "testes/cenarios_adversarios/cenario_acesso_memoria_proibido/files.txt",
            "testes/cenarios_adversarios/cenario_acesso_memoria_proibido/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 1)
        self.assertIn("ERRO DE ENTRADA: Número de página excede o limite de endereçamento virtual de 16 bits (máximo 63): 64", output.getvalue())

    def test_cenario_recursos_indisponiveis(self) -> None:
        argv = [
            "Main.py",
            "testes/cenarios_adversarios/cenario_recursos_indisponiveis/processes.txt",
            "testes/cenarios_adversarios/cenario_recursos_indisponiveis/files.txt",
            "testes/cenarios_adversarios/cenario_recursos_indisponiveis/string.txt"
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)
        self.assertEqual(exit_code, 1)
        self.assertIn("ERRO DE ENTRADA: requisição de impressora deve ser estritamente 0 ou 1: '3'", output.getvalue())

    def test_cenario_conflito_pid(self) -> None:
        argv = [
            "Main.py",
            "testes/cenarios_adversarios/cenario_conflito_pid/processes.txt",
            "testes/cenarios_adversarios/cenario_conflito_pid/files.txt",
            "testes/cenarios_adversarios/cenario_conflito_pid/string.txt"
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
            "testes/cenarios_adversarios/cenario_limite_maximo/processes.txt",
            "testes/cenarios_adversarios/cenario_limite_maximo/files.txt",
            "testes/cenarios_adversarios/cenario_limite_maximo/string.txt"
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
