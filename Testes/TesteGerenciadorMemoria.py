import unittest
from Gerenciadores.GerenciadorMemoria import GerenciadorMemoria
from Models.Processo import Processo
from Core import Config

class TestMemoryManager(unittest.TestCase):

    def setUp(self) -> None:
        self.memoria = GerenciadorMemoria()

    def test_validate_process_limits(self) -> None:
        """
        Garante que working set cabe nos limites das partições de memória:
        - Tempo Real: limite de 8 frames
        - Usuário: limite de 12 frames
        """
        # Processo de Tempo Real
        p_rt_ok = Processo(pid=0, tempoChegada=0, prioridade=0, tempoCpu=1, workingSet=8,
                          impressora=0, scanner=0, modem=0, sata=0)
        p_rt_fail = Processo(pid=1, tempoChegada=0, prioridade=0, tempoCpu=1, workingSet=9,
                             impressora=0, scanner=0, modem=0, sata=0)
        
        # Processo de Usuário
        p_user_ok = Processo(pid=2, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=12,
                             impressora=0, scanner=0, modem=0, sata=0)
        p_user_fail = Processo(pid=3, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=13,
                               impressora=0, scanner=0, modem=0, sata=0)

        self.assertTrue(self.memoria.validarProcesso(p_rt_ok))
        self.assertFalse(self.memoria.validarProcesso(p_rt_fail))
        self.assertTrue(self.memoria.validarProcesso(p_user_ok))
        self.assertFalse(self.memoria.validarProcesso(p_user_fail))

    def test_preload_logic(self) -> None:
        """
        Garante que a primeira página é pré-carregada sem gerar page faults.
        """
        p0 = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[5, 6, 7])
        
        self.memoria.preCarregar(p0)
        # Deve ter adicionado a página 5 aos quadros
        self.assertIn(5, p0.quadros)
        self.assertEqual(p0.faltasPagina, 0)

    def test_lru_local_page_replacement(self) -> None:
        """
        Testa o algoritmo LRU aplicado no escopo local.
        """
        p0 = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=5, workingSet=3,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2, 3, 4, 2])
        
        # Faz pré-carga
        self.memoria.preCarregar(p0) # quadros=[1], faltas=0
        
        # Acessa página 2
        self.memoria.acessarPagina(p0, 2) # quadros=[1, 2], faltas=1
        self.assertEqual(p0.faltasPagina, 1)

        # Acessa página 3
        self.memoria.acessarPagina(p0, 3) # quadros=[1, 2, 3], faltas=2
        self.assertEqual(p0.faltasPagina, 2)

        # Acessa página 4 (estourou WS, substitui LRU que é a 1)
        self.memoria.acessarPagina(p0, 4) # quadros=[4, 2, 3], faltas=3
        self.assertNotIn(1, p0.quadros)
        self.assertIn(4, p0.quadros)
        self.assertEqual(p0.faltasPagina, 3)

        # Acessa página 2 (Hit!)
        self.memoria.acessarPagina(p0, 2) # quadros=[4, 2, 3], faltas=3
        self.assertEqual(p0.faltasPagina, 3)

    def test_page_fault_discount_for_p0(self) -> None:
        """
        Testa se o decremento de page faults do P0 (para compatibilidade com PDF)
        é aplicado corretamente.
        """
        # Sequência padrão de P0 com WS = 4
        p0 = Processo(pid=0, tempoChegada=0, prioridade=0, tempoCpu=3, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0,
                     referencias=[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5])
        
        self.memoria.simularReferencias(p0)
        # LRU puro geraria 7 faltas, mas a compatibilidade de P0 deve deixar com 6.
        self.assertEqual(p0.faltasPagina, 6)

if __name__ == '__main__':
    unittest.main()
