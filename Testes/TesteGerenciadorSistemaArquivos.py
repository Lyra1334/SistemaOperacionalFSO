import unittest
from unittest.mock import patch
from io import StringIO
from Gerenciadores.GerenciadorSistemaArquivos import GerenciadorSistemaArquivos
from Armazenamento.Disco import Disco
from Models.OperacaoArquivo import OperacaoArquivo
from Models.Processo import Processo

class TestFileSystemManager(unittest.TestCase):

    def test_execute_create_delete(self) -> None:
        """
        Testa a execução bem sucedida de operações de criação e deleção.
        """
        disco = Disco(10, [])
        p0 = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                      impressora=0, scanner=0, modem=0, sata=0)
        
        op_create = OperacaoArquivo(pid=0, codigoOperacao=0, nomeArquivo="A", tamanho=2)
        op_delete = OperacaoArquivo(pid=0, codigoOperacao=1, nomeArquivo="A")

        manager = GerenciadorSistemaArquivos(disco, [op_create, op_delete], [p0])
        
        with patch('sys.stdout', new=StringIO()):
            manager.executar()

        # O arquivo deve ter sido criado e depois removido
        self.assertNotIn("A", disco.disco)

    def test_execute_non_existing_process(self) -> None:
        """
        Garante que operações feitas por processos que não existem falham.
        """
        disco = Disco(10, [])
        op = OperacaoArquivo(pid=99, codigoOperacao=0, nomeArquivo="A", tamanho=2)
        
        manager = GerenciadorSistemaArquivos(disco, [op], [])
        success, msg = manager._executarOperacao(op)
        
        self.assertFalse(success)
        self.assertIn("não existe", msg)

    def test_compatibility_mode(self) -> None:
        """
        Garante que no modo de compatibilidade, a operação de criação
        do arquivo E pelo processo 1 é interpretada como deleção.
        """
        # Disco com E pré-carregado por outro processo (dono None)
        disco = Disco(10, [("E", 0, 2)])
        p1 = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                      impressora=0, scanner=0, modem=0, sata=0)
        
        # Operação de criação de E com tamanho 2
        op_create_e = OperacaoArquivo(pid=1, codigoOperacao=0, nomeArquivo="E", tamanho=2)

        # Sem compatibilidade: deve falhar (arquivo E já existe)
        manager_no_compat = GerenciadorSistemaArquivos(disco, [op_create_e], [p1], modoCompatibilidade=False)
        success, msg = manager_no_compat._executarOperacao(op_create_e)
        self.assertFalse(success)
        self.assertIn("arquivo já existe", msg)

        # Com compatibilidade: vira tentativa de deleção e deve falhar
        # porque p1 não é o dono de E
        manager_compat = GerenciadorSistemaArquivos(disco, [op_create_e], [p1], modoCompatibilidade=True)
        success_c, msg_c = manager_compat._executarOperacao(op_create_e)
        self.assertFalse(success_c)
        self.assertIn("não foi criado por ele", msg_c)

if __name__ == '__main__':
    unittest.main()
