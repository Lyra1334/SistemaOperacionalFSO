import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from Scheduling.Scheduler import Scheduler
from Models.Process import Process
from Managers.MemoryManager import MemoryManager
from Managers.ResourceManager import ResourceManager
import Config

class TestScheduler(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryManager()
        self.resources = ResourceManager()

    def test_realtime_fifo(self) -> None:
        """
        Garante que processos de tempo real (prioridade 0)
        rodam usando FIFO sem preempção por quantum.
        """
        # Processo de tempo real de 3ms
        p0 = Process(pid=0, arrival_time=0, priority=0, cpu_time=3, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2, 3])
        
        # Processo de tempo real de 2ms
        p1 = Process(pid=1, arrival_time=0, priority=0, cpu_time=2, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2])

        scheduler = Scheduler([p0, p1], self.memory, self.resources)
        
        # Redirecionar stdout para não poluir
        with patch('sys.stdout', new=StringIO()):
            scheduler.run()

        self.assertEqual(p0.remaining_time, 0)
        self.assertEqual(p1.remaining_time, 0)
        self.assertIn(p0, scheduler.finished)
        self.assertIn(p1, scheduler.finished)

    def test_user_preemption_and_feedback(self) -> None:
        """
        Verifica a preempção de 1ms para processos de usuário
        e o rebaixamento de fila por realimentação (feedback).
        """
        # Processo com prioridade 1 e tempo de CPU 2ms
        p0 = Process(pid=0, arrival_time=0, priority=1, cpu_time=2, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2])

        scheduler = Scheduler([p0], self.memory, self.resources)

        with patch('sys.stdout', new=StringIO()):
            # Executa apenas um passo do loop (admit e 1 rodada do escalonador)
            scheduler._admit_new_processes()
            scheduler._retry_waiting_processes()
            process = scheduler._pick_next_process()
            self.assertIsNotNone(process)
            scheduler._execute(process)

        # O processo executou 1ms (quantum), então resta 1ms
        self.assertEqual(p0.remaining_time, 1)
        # Deve ter sido rebaixado para prioridade 2
        self.assertEqual(p0.priority, 2)
        # Deve estar de volta na fila correspondente
        self.assertIn(p0, scheduler.user_queues[2])

    def test_aging(self) -> None:
        """
        Verifica se o mecanismo de aging promove processos
        quando há acúmulo na fila de menor prioridade.
        """
        p0 = Process(pid=0, arrival_time=0, priority=3, cpu_time=2, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2])
        p1 = Process(pid=1, arrival_time=0, priority=3, cpu_time=2, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2])
        p2 = Process(pid=2, arrival_time=0, priority=3, cpu_time=2, working_set=4,
                     printer=0, scanner=0, modem=0, sata=0, references=[1, 2])

        scheduler = Scheduler([p0, p1, p2], self.memory, self.resources)
        scheduler.user_queues[3].append(p0)
        scheduler.user_queues[3].append(p1)
        scheduler.user_queues[3].append(p2)

        # Chama aging: com tamanho da fila 3 > 2, deve promover o primeiro
        scheduler._aging()
        
        self.assertEqual(p0.priority, 2)
        self.assertIn(p0, scheduler.user_queues[2])
        self.assertNotIn(p0, scheduler.user_queues[3])

    def test_context_switch_prints(self) -> None:
        """
        Garante que o dispatcher exibe cabeçalho após finalização de processo.
        """
        p0 = Process(pid=0, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=0, scanner=0, modem=0, sata=0, references=[1])
        p1 = Process(pid=1, arrival_time=0, priority=1, cpu_time=1, working_set=2,
                     printer=0, scanner=0, modem=0, sata=0, references=[1])

        scheduler = Scheduler([p0, p1], self.memory, self.resources)
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            scheduler.run()
        
        text = output.getvalue()
        # Deve ter impresso "dispatcher =>" duas vezes, uma para p0 e outra para p1
        self.assertEqual(text.count("dispatcher =>"), 2)

    def test_reject_process_exceeding_memory(self) -> None:
        """
        Garante que o escalonador rejeita o processo se ele solicitar um
        working set maior que a capacidade da partição disponível (e o move para finished).
        """
        # Processo de usuário solicitando 13 frames (limite é 12)
        p0 = Process(pid=0, arrival_time=0, priority=1, cpu_time=3, working_set=13,
                     printer=0, scanner=0, modem=0, sata=0, references=[1])

        scheduler = Scheduler([p0], self.memory, self.resources)
        
        output = StringIO()
        with patch('sys.stdout', new=output):
            scheduler.run()
        
        # O processo deve ter sido rejeitado, movido para finalizados sem executar
        self.assertIn(p0, scheduler.finished)
        self.assertEqual(p0.remaining_time, 3) # Tempo intocado (não executou)
        self.assertIn("rejeitado", output.getvalue())

if __name__ == '__main__':
    unittest.main()
