import unittest
from Storage.Disk import Disk
from Errors import FileSystemError

class TestDisk(unittest.TestCase):

    def test_disk_initialization_with_occupied_segments(self) -> None:
        """
        Verifica se os segmentos iniciais são gravados corretamente no disco.
        """
        # Disco com 10 blocos
        # X ocupa 0, tamanho 2 -> blocos 0 e 1
        # Y ocupa 3, tamanho 1 -> bloco 3
        occupied = [("X", 0, 2), ("Y", 3, 1)]
        disk = Disk(10, occupied)
        
        self.assertEqual(disk.disk, ["X", "X", "0", "Y", "0", "0", "0", "0", "0", "0"])

    def test_disk_first_fit_allocation(self) -> None:
        """
        Verifica o algoritmo First-Fit contíguo para criação de novos arquivos.
        """
        # Disco inicial: ["X", "X", "0", "Y", "0", "0", "0", "0", "0", "0"]
        disk = Disk(10, [("X", 0, 2), ("Y", 3, 1)])
        
        # Cria arquivo A de tamanho 3
        # Os espaços livres são: bloco 2 (tam 1) e blocos 4-9 (tam 6)
        # O A deve ser alocado nos blocos 4, 5 e 6
        success, msg = disk.create(pid=1, filename="A", length=3)
        self.assertTrue(success)
        self.assertEqual(disk.disk[4], "A")
        self.assertEqual(disk.disk[5], "A")
        self.assertEqual(disk.disk[6], "A")
        self.assertEqual(disk.disk[2], "0")

    def test_create_file_uniqueness(self) -> None:
        """
        Garante que arquivos com nomes iguais ou já existentes não possam ser criados.
        """
        disk = Disk(10, [("X", 0, 2)])
        # Tenta criar arquivo com nome X (já ocupado)
        success, msg = disk.create(pid=1, filename="X", length=2)
        self.assertFalse(success)

    def test_delete_permissions_rt_vs_user(self) -> None:
        """
        Garante as permissões de deleção corretas:
        - Tempo Real (can_delete_any=True) pode deletar qualquer arquivo.
        - Usuário Comum (can_delete_any=False) só deleta o que ele próprio criou.
        """
        disk = Disk(10, [])
        
        # Usuário 1 cria o arquivo A
        disk.create(pid=1, filename="A", length=2)
        
        # Usuário 2 tenta deletar o arquivo A. Deve falhar
        success_u2, msg_u2 = disk.delete(pid=2, filename="A", can_delete_any=False)
        self.assertFalse(success_u2)
        self.assertIn("não é o dono", msg_u2)

        # Usuário 1 tenta deletar o arquivo A. Deve ter sucesso
        success_u1, msg_u1 = disk.delete(pid=1, filename="A", can_delete_any=False)
        self.assertTrue(success_u1)

        # Tempo Real tenta deletar o arquivo inicial carregado no boot (dono None). Deve ter sucesso
        disk2 = Disk(10, [("B", 0, 2)])
        success_rt, msg_rt = disk2.delete(pid=0, filename="B", can_delete_any=True)
        self.assertTrue(success_rt)

    def test_map_as_text_trimming(self) -> None:
        """
        Testa a formatação e remoção de zeros à direita no mapa de blocos.
        """
        disk = Disk(10, [("A", 0, 2), ("B", 4, 1)])
        # Vetor: ["A", "A", "0", "0", "B", "0", "0", "0", "0", "0"]
        # Deve remover zeros à direita, restando apenas até o "B"
        text = disk.map_as_text()
        self.assertEqual(text, "A A 0 0 B")

if __name__ == '__main__':
    unittest.main()
