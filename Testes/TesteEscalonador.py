import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from Escalonamento.Escalonador import Escalonador
from Models.Processo import Processo
from Gerenciadores.GerenciadorMemoria import GerenciadorMemoria
from Gerenciadores.GerenciadorRecurso import GerenciadorRecurso
import Config

class TestScheduler(unittest.TestCase):

    def setUp(self) -> None:
        self.memoria = GerenciadorMemoria()
        self.recursos = GerenciadorRecurso()

    def test_realtime_fifo(self) -> None:
        """
        Garante que processos de tempo real (prioridade 0)
        rodam usando FIFO sem preempção por quantum.
        """
        # Processo de tempo real de 3ms
        p0 = Processo(pid=0, tempoChegada=0, prioridade=0, tempoCpu=3, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2, 3])
        
        # Processo de tempo real de 2ms
        p1 = Processo(pid=1, tempoChegada=0, prioridade=0, tempoCpu=2, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2])

        escalonador = Escalonador([p0, p1], self.memoria, self.recursos)
        
        # Redirecionar stdout para não poluir
        with patch('sys.stdout', new=StringIO()):
            escalonador.executar()

        self.assertEqual(p0.tempoRestante, 0)
        self.assertEqual(p1.tempoRestante, 0)
        self.assertIn(p0, escalonador.finalizados)
        self.assertIn(p1, escalonador.finalizados)

    def test_user_preemption_and_feedback(self) -> None:
        """
        Verifica a preempção de 1ms para processos de usuário
        e o rebaixamento de fila por realimentação (feedback).
        """
        # Processo com prioridade 1 e tempo de CPU 2ms
        p0 = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=2, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2])

        escalonador = Escalonador([p0], self.memoria, self.recursos)

        with patch('sys.stdout', new=StringIO()):
            # Executa apenas um passo do loop (admit e 1 rodada do escalonador)
            escalonador._admitirNovosProcessos()
            escalonador._retentarProcessosAguardando()
            processo = escalonador._escolherProximoProcesso()
            self.assertIsNotNone(processo)
            escalonador._executar(processo)

        # O processo executou 1ms (quantum), então resta 1ms
        self.assertEqual(p0.tempoRestante, 1)
        # Deve ter sido rebaixado para prioridade 2
        self.assertEqual(p0.prioridade, 2)
        # Deve estar de volta na fila correspondente
        self.assertIn(p0, escalonador.filasUsuario[2])

    def test_aging(self) -> None:
        """
        Verifica se o mecanismo de aging promove processos
        quando há acúmulo na fila de menor prioridade.
        """
        p0 = Processo(pid=0, tempoChegada=0, prioridade=3, tempoCpu=2, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2])
        p1 = Processo(pid=1, tempoChegada=0, prioridade=3, tempoCpu=2, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2])
        p2 = Processo(pid=2, tempoChegada=0, prioridade=3, tempoCpu=2, workingSet=4,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1, 2])

        escalonador = Escalonador([p0, p1, p2], self.memoria, self.recursos)
        escalonador.filasUsuario[3].append(p0)
        escalonador.filasUsuario[3].append(p1)
        escalonador.filasUsuario[3].append(p2)

        # Chama aging: com tamanho da fila 3 > 2, deve promover o primeiro
        escalonador._envelhecimento()
        
        self.assertEqual(p0.prioridade, 2)
        self.assertIn(p0, escalonador.filasUsuario[2])
        self.assertNotIn(p0, escalonador.filasUsuario[3])

    def test_context_switch_prints(self) -> None:
        """
        Garante que o despachante exibe cabeçalho após finalização de processo.
        """
        p0 = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1])
        p1 = Processo(pid=1, tempoChegada=0, prioridade=1, tempoCpu=1, workingSet=2,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1])

        escalonador = Escalonador([p0, p1], self.memoria, self.recursos)
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            escalonador.executar()
        
        text = output.getvalue()
        # Deve ter impresso "dispatcher =>" duas vezes, uma para p0 e outra para p1
        self.assertEqual(text.count("dispatcher =>"), 2)

    def test_reject_process_exceeding_memory(self) -> None:
        """
        Garante que o escalonador rejeita o processo se ele solicitar um
        working set maior que a capacidade da partição disponível (e o move para finished).
        """
        # Processo de usuário solicitando 13 quadros (limite é 12)
        p0 = Processo(pid=0, tempoChegada=0, prioridade=1, tempoCpu=3, workingSet=13,
                     impressora=0, scanner=0, modem=0, sata=0, referencias=[1])

        escalonador = Escalonador([p0], self.memoria, self.recursos)
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            escalonador.executar()
        
        # O processo deve ter sido rejeitado, movido para finalizados sem executar
        self.assertIn(p0, escalonador.finalizados)
        self.assertEqual(p0.tempoRestante, 3) # Tempo intocado (não executou)
        self.assertIn("rejeitado", output.getvalue())

if __name__ == '__main__':
    unittest.main()
