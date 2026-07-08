import unittest
from Gerenciadores.GerenciadorRecurso import GerenciadorRecurso
from Models.Processo import Processo
import Config

class TestResourceManager(unittest.TestCase):

    def setUp(self) -> None:
        self.recursos = GerenciadorRecurso()

    def test_verify_process_limits(self) -> None:
        """
        Garante que verificarProcesso recusa processos que excedem o limite total físico:
        - Scanners: 1
        - Impressoras: 2
        - Modems: 1
        - SATA: 2
        """
        # Processo solicitando recursos dentro do limite físico
        p_ok = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                        impressora=2, scanner=1, modem=1, sata=2)
        
        # Processo solicitando mais impressoras que o limite (3 > 2)
        p_fail_printer = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                                 impressora=3, scanner=1, modem=1, sata=2)

        self.assertTrue(self.recursos.verificarProcesso(p_ok))
        self.assertFalse(self.recursos.verificarProcesso(p_fail_printer))

    def test_realtime_needs_no_resources(self) -> None:
        """
        Garante que processos de tempo real (prioridade 0)
        são isentos de alocação de recursos físicos de E/S.
        """
        p_rt = Processo(pid=0, tempoChegada=0, prioridade=0, tempoCpu=1, workingSet=2,
                        impressora=2, scanner=1, modem=1, sata=2) # Parâmetros ignorados
        
        req = self.recursos.necessarios(p_rt)
        self.assertEqual(req, {"scanner": 0, "impressora": 0, "modem": 0, "sata": 0})
        self.assertTrue(self.recursos.podeAlocar(p_rt))

    def test_allocate_and_release(self) -> None:
        """
        Testa o fluxo básico de alocação e liberação de recursos.
        """
        p0 = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                     impressora=2, scanner=1, modem=0, sata=1)

        p1 = Processo(pid=2, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                     impressora=1, scanner=0, modem=0, sata=0)

        # Inicialmente há 2 impressoras, 1 scanner, 2 SATAs
        # p0 pede: 2 impressoras, 1 scanner, 1 SATA
        self.assertTrue(self.recursos.alocar(p0))
        
        # Recursos restantes: impressora=0, scanner=0, sata=1
        # p1 pede 1 impressora. Deve falhar
        self.assertFalse(self.recursos.podeAlocar(p1))
        self.assertFalse(self.recursos.alocar(p1))

        # Libera p0
        self.recursos.liberar(p0)

        # p1 agora deve conseguir alocar
        self.assertTrue(self.recursos.podeAlocar(p1))
        self.assertTrue(self.recursos.alocar(p1))

if __name__ == '__main__':
    unittest.main()
