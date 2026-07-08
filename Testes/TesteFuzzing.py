import unittest
from unittest.mock import patch
from Parsers.ProcessoParser import ProcessoParser
from Parsers.SistemaArquivosParser import SistemaArquivosParser
from Gerenciadores.GerenciadorRecurso import GerenciadorRecurso
from Gerenciadores.GerenciadorMemoria import GerenciadorMemoria
from Armazenamento.Disco import Disco
from Models.Processo import Processo
from Models.OperacaoArquivo import OperacaoArquivo
from Erros import ErroEntrada, ErroSistemaArquivos, ErroGerenciadorRecurso, ErroGerenciadorMemoria

class TestFuzzingAdversarial(unittest.TestCase):

    def test_page_bounds_references(self) -> None:
        """
        Garante que páginas fora dos limites (negativas ou maiores que 63) são rejeitadas.
        """
        # Página negativa (-1)
        with patch('Parsers.ProcessoParser.lerLinhasNaoVazias') as mock_read:
            mock_read.side_effect = [
                ["0, 0, 1, 2, 0, 0, 0, 0"],
                ["1, -1, 2"]
            ]
            with self.assertRaises(ErroEntrada):
                ProcessoParser.carregar("p", "s")

        # Página > 63 (ex: 64)
        with patch('Parsers.ProcessoParser.lerLinhasNaoVazias') as mock_read:
            mock_read.side_effect = [
                ["0, 0, 1, 2, 0, 0, 0, 0"],
                ["1, 64, 2"]
            ]
            with self.assertRaises(ErroEntrada):
                ProcessoParser.carregar("p", "s")

    def test_filenames_with_spaces_and_control_chars(self) -> None:
        """
        Garante que nomes de arquivos com espaços, tabs ou novas linhas são rejeitados
        pois corrompem a formatação de saída e o mapa de blocos.
        """
        disco = Disco(10, [])
        
        # Nome com espaço
        success, msg = disco.criar(pid=1, nomeArquivo="Arq A", comprimento=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

        # Nome com tab
        success, msg = disco.criar(pid=1, nomeArquivo="Arq\tB", comprimento=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

        # Nome com quebra de linha
        success, msg = disco.criar(pid=1, nomeArquivo="Arq\nC", comprimento=2)
        self.assertFalse(success)
        self.assertIn("inválido", msg.lower())

    def test_double_release_resources(self) -> None:
        """
        Garante que a liberação dupla de recursos ou liberação sem alocação prévia
        seja detectada e não cause duplicação/vazamento de recursos (gerar recursos extras).
        """
        recursos = GerenciadorRecurso()
        p0 = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                      impressora=1, scanner=1, modem=0, sata=0)
        
        # Liberação sem alocação prévia deve levantar erro ou ser ignorada com segurança
        # (não deve aumentar a quantidade de recursos acima do limite físico inicial)
        with self.assertRaises(ErroGerenciadorRecurso):
            recursos.liberar(p0)

        # Aloca uma vez
        self.assertTrue(recursos.alocar(p0))
        self.assertEqual(recursos.disponiveis["impressora"], 1) # 2 - 1 = 1
        
        # Libera uma vez
        recursos.liberar(p0)
        self.assertEqual(recursos.disponiveis["impressora"], 2) # 1 + 1 = 2

        # Liberação dupla subsequente deve falhar
        with self.assertRaises(ErroGerenciadorRecurso):
            recursos.liberar(p0)

    def test_invalid_working_set_and_cpu_time(self) -> None:
        """
        Garante que valores absurdos como working set <= 0 ou cpu_time <= 0
        são adequadamente validados e rejeitados no parser.
        """
        with patch('Parsers.ProcessoParser.lerLinhasNaoVazias') as mock_read:
            mock_read.side_effect = [
                ["0, 1, -2, 4, 0, 0, 0, 0"], # cpu_time negativo (-2)
                ["1, 2"]
            ]
            with self.assertRaises(ErroEntrada):
                ProcessoParser.carregar("p", "s")

        with patch('Parsers.ProcessoParser.lerLinhasNaoVazias') as mock_read:
            mock_read.side_effect = [
                ["0, 1, 3, -1, 0, 0, 0, 0"], # working_set negativo (-1)
                ["1, 2"]
            ]
            with self.assertRaises(ErroEntrada):
                ProcessoParser.carregar("p", "s")

    def test_extremely_large_numbers_overflow(self) -> None:
        """
        Testa o comportamento do sistema com inteiros extremamente grandes
        que poderiam causar estouro de memória ou laços infinitos.
        """
        with patch('Parsers.ProcessoParser.lerLinhasNaoVazias') as mock_read:
            # CPU time gigantesco (10^18)
            mock_read.side_effect = [
                [f"0, 1, {10**18}, 4, 0, 0, 0, 0"],
                ["1, 2"]
            ]
            with self.assertRaises(ErroEntrada):
                ProcessoParser.carregar("p", "s")

        with patch('Parsers.SistemaArquivosParser.lerLinhasNaoVazias') as mock_read:
            # Tamanho do disco gigantesco
            mock_read.return_value = [
                f"{10**18}",
                "0"
            ]
            with self.assertRaises(ErroEntrada):
                SistemaArquivosParser.carregar("f")

    def test_strict_boolean_parsing(self) -> None:
        """
        Garante que apenas as representações equivalentes a 0 ou 1 sejam aceitas,
        enquanto outros valores inteiros (como 2, 10 ou negativos) sejam estritamente rejeitados.
        """
        from Utils import converterBooleano
        
        # Válidos
        self.assertEqual(converterBooleano("1"), 1)
        self.assertEqual(converterBooleano("0"), 0)
        self.assertEqual(converterBooleano("true"), 1)
        self.assertEqual(converterBooleano("false"), 0)

        # Inválidos (devem lançar erro)
        with self.assertRaises(ErroEntrada):
            converterBooleano("2")
        
        with self.assertRaises(ErroEntrada):
            converterBooleano("10")
        
        with self.assertRaises(ErroEntrada):
            converterBooleano("-1")
        
        with self.assertRaises(ErroEntrada):
            converterBooleano("-5")

if __name__ == '__main__':
    unittest.main()
