import unittest
from unittest.mock import patch
from io import StringIO
from Managers.FileSystemManager import FileSystemManager
from Storage.Disk import Disk
from Models.FileOperation import FileOperation
from Models.Process import Process

class TestFileSystemManager(unittest.TestCase):

    def test_execute_create_delete(self) -> None:
        """
        Testa a execução bem sucedida de operações de criação e deleção.
        """
        disk = Disk(10, [])
        p0 = Process(pid=0, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=0, scanner=0, modem=0, sata=0)
        
        op_create = FileOperation(pid=0, op_code=0, filename="A", size=2)
        op_delete = FileOperation(pid=0, op_code=1, filename="A")

        manager = FileSystemManager(disk, [op_create, op_delete], [p0])
        
        with patch('sys.stdout', new=StringIO()):
            manager.run()

        # O arquivo deve ter sido criado e depois removido
        self.assertNotIn("A", disk.disk)

    def test_execute_non_existing_process(self) -> None:
        """
        Garante que operações feitas por processos que não existem falham.
        """
        disk = Disk(10, [])
        op = FileOperation(pid=99, op_code=0, filename="A", size=2)
        
        manager = FileSystemManager(disk, [op], [])
        success, msg = manager._execute_operation(op)
        
        self.assertFalse(success)
        self.assertIn("não existe", msg)

    def test_compatibility_mode(self) -> None:
        """
        Garante que no modo de compatibilidade, a operação de criação
        do arquivo E pelo processo 1 é interpretada como deleção.
        """
        # Disk com E pré-carregado por outro processo (dono None)
        disk = Disk(10, [("E", 0, 2)])
        p1 = Process(pid=1, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=0, scanner=0, modem=0, sata=0)
        
        # Operação de criação de E com tamanho 2
        op_create_e = FileOperation(pid=1, op_code=0, filename="E", size=2)

        # Sem compatibilidade: deve falhar (arquivo E já existe)
        manager_no_compat = FileSystemManager(disk, [op_create_e], [p1], compatibility_mode=False)
        success, msg = manager_no_compat._execute_operation(op_create_e)
        self.assertFalse(success)
        self.assertIn("arquivo já existe", msg)

        # Com compatibilidade: vira tentativa de deleção e deve falhar
        # porque p1 não é o dono de E
        manager_compat = FileSystemManager(disk, [op_create_e], [p1], compatibility_mode=True)
        success_c, msg_c = manager_compat._execute_operation(op_create_e)
        self.assertFalse(success_c)
        self.assertIn("não foi criado por ele", msg_c)

if __name__ == '__main__':
    unittest.main()
