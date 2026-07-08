import unittest
from unittest.mock import patch
from Parsers.ProcessParser import ProcessParser
from Errors import InputError
import Config

class TestProcessParser(unittest.TestCase):

    @patch('Parsers.ProcessParser.read_non_empty_lines')
    def test_load_valid_process(self, mock_read) -> None:
        """
        Verifica se um arquivo de processo válido é parseado corretamente.
        """
        # mock das linhas lidas dos arquivos
        # tempo_init, priority, cpu_time, working_set, printer, scanner, modem, sata
        mock_read.side_effect = [
            ["2, 0, 3, 4, 0, 0, 0, 0", "8, 1, 2, 8, 1, 0, 0, 0"], # processes.txt
            ["1,2,3,4,1,2,5,1,2,3,4,5", "7,0,1,2"] # string.txt
        ]

        processes = ProcessParser.load("dummy_proc_path", "dummy_str_path")
        
        self.assertEqual(len(processes), 2)
        
        # P0 (Tempo Real)
        p0 = processes[0]
        self.assertEqual(p0.pid, 0)
        self.assertEqual(p0.arrival_time, 2)
        self.assertEqual(p0.priority, 0)
        self.assertTrue(p0.is_realtime)
        self.assertEqual(p0.references, [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5])
        # P0 tempo real força todos os recursos para 0
        self.assertEqual(p0.printer, 0)
        self.assertEqual(p0.scanner, 0)

        # P1 (Usuário)
        p1 = processes[1]
        self.assertEqual(p1.pid, 1)
        self.assertEqual(p1.priority, 1)
        self.assertFalse(p1.is_realtime)
        self.assertEqual(p1.printer, 1)
        self.assertEqual(p1.references, [7, 0, 1, 2])

    @patch('Parsers.ProcessParser.read_non_empty_lines')
    def test_load_mismatch_lines_error(self, mock_read) -> None:
        """
        Garante que lança erro se a quantidade de linhas for diferente.
        """
        mock_read.side_effect = [
            ["2, 0, 3, 4, 0, 0, 0, 0"],
            ["1,2,3", "4,5,6"]
        ]
        with self.assertRaises(InputError):
            ProcessParser.load("p", "s")

    @patch('Parsers.ProcessParser.read_non_empty_lines')
    def test_load_invalid_column_count_error(self, mock_read) -> None:
        """
        Garante que lança erro se faltarem colunas de parâmetros de processo.
        """
        mock_read.side_effect = [
            ["2, 0, 3, 4"], # apenas 4 colunas em vez de 8
            ["1,2,3"]
        ]
        with self.assertRaises(InputError):
            ProcessParser.load("p", "s")

    @patch('Parsers.ProcessParser.read_non_empty_lines')
    def test_load_invalid_types_error(self, mock_read) -> None:
        """
        Garante que lança erro se houver valores não numéricos.
        """
        mock_read.side_effect = [
            ["abc, 0, 3, 4, 0, 0, 0, 0"],
            ["1,2,3"]
        ]
        with self.assertRaises(InputError):
            ProcessParser.load("p", "s")

if __name__ == '__main__':
    unittest.main()
