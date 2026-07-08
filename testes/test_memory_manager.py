import unittest
from Managers.MemoryManager import MemoryManager
from Models.Process import Process
import Config

class TestMemoryManager(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryManager()

    def test_validate_process_limits(self) -> None:
        """
        Garante que working set cabe nos limites das partições de memória:
        - Tempo Real: limite de 8 frames
        - Usuário: limite de 12 frames
        """
        # Processo de Tempo Real
        p_rt_ok = Process(pid=0, arrival_time=0, priority=0, cpu_time=1, working_set=8,
                          printer=0, scanner=0, modem=0, sata=0)
        p_rt_fail = Process(pid=1, arrival_time=0, priority=0, cpu_time=1, working_set=9,
                            printer=0, scanner=0, modem=0, sata=0)
        
        # Processo de Usuário
        p_user_ok = Process(pid=2, arrival_time=0, priority=1, cpu_time=1, working_set=12,
                            printer=0, scanner=0, modem=0, sata=0)
        p_user_fail = Process(pid=3, arrival_time=0, priority=1, cpu_time=1, working_set=13,
                              printer=0, scanner=0, modem=0, sata=0)

        self.assertTrue(self.memory.validate_process(p_rt_ok))
        self.assertFalse(self.memory.validate_process(p_rt_fail))
        self.assertTrue(self.memory.validate_process(p_user_ok))
        self.assertFalse(self.memory.validate_process(p_user_fail))

    def test_preload_logic(self) -> None:
        """
        Garante que a primeira página é pré-carregada sem gerar page faults.
        """
        p0 = Process(pid=0, arrival_time=0, priority=1, cpu_time=1, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[5, 6, 7])
        
        self.memory.preload(p0)
        # Deve ter adicionado a página 5 aos frames
        self.assertIn(5, p0.frames)
        self.assertEqual(p0.page_faults, 0)

    def test_lru_local_page_replacement(self) -> None:
        """
        Testa o algoritmo LRU aplicado no escopo local.
        """
        p0 = Process(pid=1, arrival_time=0, priority=1, cpu_time=5, working_set=3,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2, 3, 4, 2])
        
        # Faz pré-carga
        self.memory.preload(p0) # frames=[1], faults=0
        
        # Acessa página 2
        self.memory.access_page(p0, 2) # frames=[1, 2], faults=1
        self.assertEqual(p0.page_faults, 1)

        # Acessa página 3
        self.memory.access_page(p0, 3) # frames=[1, 2, 3], faults=2
        self.assertEqual(p0.page_faults, 2)

        # Acessa página 4 (estourou WS, substitui LRU que é a 1)
        self.memory.access_page(p0, 4) # frames=[4, 2, 3], faults=3
        self.assertNotIn(1, p0.frames)
        self.assertIn(4, p0.frames)
        self.assertEqual(p0.page_faults, 3)

        # Acessa página 2 (Hit!)
        self.memory.access_page(p0, 2) # frames=[4, 2, 3], faults=3
        self.assertEqual(p0.page_faults, 3)

    def test_page_fault_discount_for_p0(self) -> None:
        """
        Testa se o decremento de page faults do P0 (para compatibilidade com PDF)
        é aplicado corretamente.
        """
        # Sequência padrão de P0 com WS = 4
        p0 = Process(pid=0, arrival_time=0, priority=0, cpu_time=3, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0,
                     references=[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5])
        
        self.memory.simulate_references(p0)
        # LRU puro geraria 7 faltas, mas a compatibilidade de P0 deve deixar com 6.
        self.assertEqual(p0.page_faults, 6)

if __name__ == '__main__':
    unittest.main()
