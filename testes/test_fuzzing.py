import unittest
from unittest.mock import patch
from Parsers.ProcessParser import ProcessParser
from Parsers.FileSystemParser import FileSystemParser
from Managers.ResourceManager import ResourceManager
from Managers.MemoryManager import MemoryManager
from Storage.Disk import Disk
from Models.Process import Process
from Models.FileOperation import FileOperation
from Errors import InputError, FileSystemError, ResourceManagerError, MemoryManagerError

class TestFuzzingAdversarial(unittest.TestCase):

    def test_page_bounds_references(self) -> None:
        """
        Garante que páginas fora dos limites (negativas ou maiores que 63) são rejeitadas.
        """
        # Página negativa (-1)
        with patch('Parsers.ProcessParser.read_non_empty_lines') as mock_read:
            mock_read.side_effect = [
                ["0, 0, 1, 2, 0, 0, 0, 0"],
                ["1, -1, 2"]
            ]
            with self.assertRaises(InputError):
                ProcessParser.load("p", "s")

        # Página > 63 (ex: 64)
        with patch('Parsers.ProcessParser.read_non_empty_lines') as mock_read:
            mock_read.side_effect = [
                ["0, 0, 1, 2, 0, 0, 0, 0"],
                ["1, 64, 2"]
            ]
            with self.assertRaises(InputError):
                ProcessParser.load("p", "s")

    def test_filenames_with_spaces_and_control_chars(self) -> None:
        """
        Garante que nomes de arquivos com espaços, tabs ou novas linhas são rejeitados
        pois corrompem a formatação de saída e o mapa de blocos.
        """
        disk = Disk(10, [])
        
        # Nome com espaço
        success, msg = disk.create(pid=1, filename="Arq A", length=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

        # Nome com tab
        success, msg = disk.create(pid=1, filename="Arq\tB", length=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

        # Nome com quebra de linha
        success, msg = disk.create(pid=1, filename="Arq\nC", length=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

    def test_double_release_resources(self) -> None:
        """
        Garante que a liberação dupla de recursos ou liberação sem alocação prévia
        seja detectada e não cause duplicação/vazamento de recursos (gerar recursos extras).
        """
        resources = ResourceManager()
        p0 = Process(pid=1, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=1, scanner=1, modem=0, sata=0)
        
        # Liberação sem alocação prévia deve levantar erro ou ser ignorada com segurança
        # (não deve aumentar a quantidade de recursos acima do limite físico inicial)
        with self.assertRaises(ResourceManagerError):
            resources.release(p0)

        # Aloca uma vez
        self.assertTrue(resources.allocate(p0))
        self.assertEqual(resources.available["scanner"], 0) # 1 - 1 = 0
        
        # Libera uma vez
        resources.release(p0)
        self.assertEqual(resources.available["scanner"], 1) # 0 + 1 = 1

        # Liberação dupla subsequente deve falhar
        with self.assertRaises(ResourceManagerError):
            resources.release(p0)

    def test_invalid_working_set_and_cpu_time(self) -> None:
        """
        Garante que valores absurdos como working set <= 0 ou cpu_time <= 0
        são adequadamente validados e rejeitados no parser.
        """
        with patch('Parsers.ProcessParser.read_non_empty_lines') as mock_read:
            mock_read.side_effect = [
                ["0, 1, -2, 4, 0, 0, 0, 0"], # cpu_time negativo (-2)
                ["1, 2"]
            ]
            with self.assertRaises(InputError):
                ProcessParser.load("p", "s")

        with patch('Parsers.ProcessParser.read_non_empty_lines') as mock_read:
            mock_read.side_effect = [
                ["0, 1, 3, -1, 0, 0, 0, 0"], # working_set negativo (-1)
                ["1, 2"]
            ]
            with self.assertRaises(InputError):
                ProcessParser.load("p", "s")

    def test_extremely_large_numbers_overflow(self) -> None:
        """
        Testa o comportamento do sistema com inteiros extremamente grandes
        que poderiam causar estouro de memória ou laços infinitos.
        """
        with patch('Parsers.ProcessParser.read_non_empty_lines') as mock_read:
            # CPU time gigantesco (10^18)
            mock_read.side_effect = [
                [f"0, 1, {10**18}, 4, 0, 0, 0, 0"],
                ["1, 2"]
            ]
            with self.assertRaises(InputError):
                ProcessParser.load("p", "s")

        with patch('Parsers.FileSystemParser.read_non_empty_lines') as mock_read:
            # Tamanho do disco gigantesco
            mock_read.return_value = [
                f"{10**18}",
                "0"
            ]
            with self.assertRaises(InputError):
                FileSystemParser.load("f")

    def test_strict_boolean_parsing(self) -> None:
        """
        Garante que apenas as representações equivalentes a 0 ou 1 sejam aceitas,
        enquanto outros valores inteiros (como 2, 10 ou negativos) sejam estritamente rejeitados.
        """
        from Utils import parse_01
        
        # Válidos
        self.assertEqual(parse_01("1"), 1)
        self.assertEqual(parse_01("0"), 0)
        self.assertEqual(parse_01("true"), 1)
        self.assertEqual(parse_01("false"), 0)

        # Inválidos (devem lançar erro)
        with self.assertRaises(InputError):
            parse_01("2")
        
        with self.assertRaises(InputError):
            parse_01("10")
        
        with self.assertRaises(InputError):
            parse_01("-1")
        
        with self.assertRaises(InputError):
            parse_01("-5")

if __name__ == '__main__':
    unittest.main()
