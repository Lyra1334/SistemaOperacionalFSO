import unittest
from unittest.mock import patch
from Parsers.FileSystemParser import FileSystemParser
from Errors import InputError
import Config

class TestFileSystemParser(unittest.TestCase):

    @patch('Parsers.FileSystemParser.read_non_empty_lines')
    def test_load_valid_filesystem(self, mock_read) -> None:
        """
        Verifica se um arquivo de configuração de arquivos válido é parseado corretamente.
        """
        mock_read.return_value = [
            "10",       # tamanho do disco
            "2",        # 2 segmentos ocupados iniciais
            "X, 0, 2",  # X nos blocos 0 e 1
            "Y, 3, 1",  # Y no bloco 3
            "0, 0, A, 5", # op: PID 0 cria A com tamanho 5
            "1, 1, X"    # op: PID 1 deleta X
        ]

        disk, operations = FileSystemParser.load("dummy_files_path")
        
        # Verifica o disco
        self.assertEqual(disk.size, 10)
        self.assertEqual(disk.disk, ["X", "X", "0", "Y", "0", "0", "0", "0", "0", "0"])

        # Verifica as operações
        self.assertEqual(len(operations), 2)
        
        op0 = operations[0]
        self.assertEqual(op0.pid, 0)
        self.assertEqual(op0.op_code, 0)
        self.assertEqual(op0.filename, "A")
        self.assertEqual(op0.size, 5)

        op1 = operations[1]
        self.assertEqual(op1.pid, 1)
        self.assertEqual(op1.op_code, 1)
        self.assertEqual(op1.filename, "X")
        self.assertIsNone(op1.size)

    @patch('Parsers.FileSystemParser.read_non_empty_lines')
    def test_load_too_few_lines_error(self, mock_read) -> None:
        """
        Garante que lança erro se o arquivo tiver menos de 2 linhas.
        """
        mock_read.return_value = ["10"]
        with self.assertRaises(InputError):
            FileSystemParser.load("f")

    @patch('Parsers.FileSystemParser.read_non_empty_lines')
    def test_load_invalid_occupied_count_error(self, mock_read) -> None:
        """
        Garante que lança erro se o número de segmentos descritos não bater com a linha 2.
        """
        mock_read.return_value = [
            "10",
            "3", # promete 3 segmentos
            "X, 0, 2" # mas só passa 1
        ]
        with self.assertRaises(InputError):
            FileSystemParser.load("f")

if __name__ == '__main__':
    unittest.main()
