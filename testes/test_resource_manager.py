import unittest
from Managers.ResourceManager import ResourceManager
from Models.Process import Process
import Config

class TestResourceManager(unittest.TestCase):

    def setUp(self) -> None:
        self.resources = ResourceManager()

    def test_verify_process_limits(self) -> None:
        """
        Garante que verify_process recusa processos que excedem o limite total físico:
        - Scanners: 1
        - Impressoras: 2
        - Modems: 1
        - SATA: 2
        """
        # Processo solicitando recursos dentro do limite físico
        p_ok = Process(pid=0, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                        printer=2, scanner=1, modem=1, sata=2)
        
        # Processo solicitando mais impressoras que o limite (3 > 2)
        p_fail_printer = Process(pid=1, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                                 printer=3, scanner=1, modem=1, sata=2)

        self.assertTrue(self.resources.verify_process(p_ok))
        self.assertFalse(self.resources.verify_process(p_fail_printer))

    def test_realtime_needs_no_resources(self) -> None:
        """
        Garante que processos de tempo real (prioridade 0)
        são isentos de alocação de recursos físicos de E/S.
        """
        p_rt = Process(pid=0, arrival_time=0, priority=0, cpu_time=1, working_set=2,
                        printer=2, scanner=1, modem=1, sata=2) # Parâmetros ignorados
        
        req = self.resources.required(p_rt)
        self.assertEqual(req, {"scanner": 0, "printer": 0, "modem": 0, "sata": 0})
        self.assertTrue(self.resources.can_allocate(p_rt))

    def test_allocate_and_release(self) -> None:
        """
        Testa o fluxo básico de alocação e liberação de recursos.
        """
        p0 = Process(pid=1, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=2, scanner=1, modem=0, sata=1)

        p1 = Process(pid=2, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=1, scanner=0, modem=0, sata=0)

        # Inicialmente há 2 impressoras, 1 scanner, 2 SATAs
        # p0 pede: 2 impressoras, 1 scanner, 1 SATA
        self.assertTrue(self.resources.allocate(p0))
        
        # Recursos restantes: impressoras=0, scanner=0, sata=1
        # p1 pede 1 impressora. Deve falhar
        self.assertFalse(self.resources.can_allocate(p1))
        self.assertFalse(self.resources.allocate(p1))

        # Libera p0
        self.resources.release(p0)

        # p1 agora deve conseguir alocar
        self.assertTrue(self.resources.can_allocate(p1))
        self.assertTrue(self.resources.allocate(p1))

if __name__ == '__main__':
    unittest.main()
