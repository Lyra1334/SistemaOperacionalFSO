import unittest
from io import StringIO
from unittest.mock import patch
import Main

class TestSOIntegration(unittest.TestCase):

    def test_run_default_case(self) -> None:
        """
        Executa o pseudo-SO usando os casos de teste padrão
        e garante que executa até o fim com sucesso (código de saída 0).
        """
        argv = [
            "Main.py",
            "testes/casosDeTeste/processes.txt",
            "testes/casosDeTeste/files.txt",
            "testes/casosDeTeste/string.txt"
        ]
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        
        # O P0 e P1 devem finalizar com SIGINT
        self.assertIn("P0 return SIGINT", text)
        self.assertIn("P1 return SIGINT", text)
        
        # Deve ter o mapa do disco
        self.assertIn("Mapa de ocupação do disco:", text)
        self.assertIn("D D D Y 0 Z Z Z", text)
        
        # Deve ter o contador de page faults correto
        self.assertIn("P0 = 6 faltas de páginas", text)
        self.assertIn("P1 = 14 faltas de páginas", text)

    def test_run_timesharing_case(self) -> None:
        """
        Executa o pseudo-SO usando o caso de teste de time-sharing
        e garante que executa até o fim com sucesso.
        """
        argv = [
            "Main.py",
            "testes/casosDeTeste/1/processes.txt",
            "testes/casosDeTeste/1/files.txt",
            "testes/casosDeTeste/1/string.txt"
        ]
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            exit_code = Main.main(argv)

        self.assertEqual(exit_code, 0)
        text = output.getvalue()

        # Ambos os processos devem terminar
        self.assertIn("P0 return SIGINT", text)
        self.assertIn("P1 return SIGINT", text)
        
        # Mapa do disco esperado para este caso
        self.assertIn("Mapa de ocupação do disco:", text)
        self.assertIn("X X 0 Y 0 Z Z Z", text)
        
        # Contagem de page faults esperada
        self.assertIn("P0 = 10 faltas de páginas", text)
        self.assertIn("P1 = 23 faltas de páginas", text)

if __name__ == '__main__':
    unittest.main()
