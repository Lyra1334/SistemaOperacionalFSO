"""
Scheduler.py

Escalonador do pseudo-SO.

Responsável por:
- admitir processos;
- organizar filas de tempo real e de usuário;
- aplicar FIFO para tempo real;
- aplicar múltiplas filas com realimentação para usuário;
- chamar o dispatcher;
- controlar execução e finalização dos processos.
"""

from collections import deque
from typing import Deque, Dict, List, Optional

import Config

from Interface.Dispatcher import Dispatcher
from Managers.MemoryManager import MemoryManager
from Managers.ResourceManager import ResourceManager
from Models.Process import Process


class Scheduler:

    def __init__(
        self,
        processes: List[Process],
        memory: MemoryManager,
        resources: ResourceManager
    ) -> None:
        self.processes = sorted(
            processes,
            key=lambda process: (process.arrival_time, process.pid)
        )

        self.memory = memory
        self.resources = resources

        self.dispatcher = Dispatcher()

        self.realtime_queue: Deque[Process] = deque()

        self.user_queues: Dict[int, Deque[Process]] = {
            1: deque(),
            2: deque(),
            3: deque()
        }

        self.waiting: Deque[Process] = deque()

        self.clock = 0
        self.next_arrival_index = 0
        self.finished: List[Process] = []
        self.last_pid = None

    def run(self) -> None:
        while len(self.finished) < len(self.processes):
            self._admit_new_processes()
            self._retry_waiting_processes()

            process = self._pick_next_process()

            if process is None:
                self.clock += 1
                continue

            self._execute(process)

    def _admit_new_processes(self) -> None:
        while (
            self.next_arrival_index < len(self.processes)
            and self.processes[self.next_arrival_index].arrival_time <= self.clock
        ):
            process = self.processes[self.next_arrival_index]
            self.next_arrival_index += 1

            if not self.memory.validate_process(process):
                print(
                    f"dispatcher => Processo {process.pid} rejeitado: "
                    "working set maior que a área de memória permitida."
                )
                process.is_rejected = True
                self.finished.append(process)
                continue

            if not self.resources.verify_process(process):
                print(
                    f"dispatcher => Processo {process.pid} rejeitado: "
                    "requer mais recursos do que o possúido pelo sistema."
                )
                process.is_rejected = True
                self.finished.append(process)
                continue

            self.memory.preload(process)

            if not self.resources.allocate(process):
                print(
                    f"dispatcher => Processo {process.pid} aguardando recursos de E/S."
                )
                self.waiting.append(process)
                continue

            self._enqueue(process)

    def _retry_waiting_processes(self) -> None:
        if not self.waiting:
            return

        remaining: Deque[Process] = deque()

        while self.waiting:
            process = self.waiting.popleft()

            if self.resources.allocate(process):
                self._enqueue(process)
            else:
                remaining.append(process)

        self.waiting = remaining

    def _enqueue(self, process: Process) -> None:
        if process.is_realtime:
            self.realtime_queue.append(process)
            return

        priority = min(max(process.priority, 1), Config.MAX_USER_PRIORITY)
        self.user_queues[priority].append(process)

    def _pick_next_process(self) -> Optional[Process]:
        if self.realtime_queue:
            return self.realtime_queue.popleft()

        for priority in range(1, Config.MAX_USER_PRIORITY + 1):
            if self.user_queues[priority]:
                return self.user_queues[priority].popleft()

        return None

    def _execute(self, process: Process) -> None:

        if self.last_pid != process.pid:
            self.dispatcher.show_process_info(process)

            print(f"process {process.pid} =>")
            print(f"P{process.pid} STARTED")

        self.memory.simulate_references(process)

        if process.is_realtime:
            quantum = process.remaining_time
        else:
            quantum = min(Config.USER_QUANTUM, process.remaining_time)

        for _ in range(quantum):
            instruction_number = process.cpu_time - process.remaining_time + 1

            print(f"P{process.pid} instruction {instruction_number}")

            process.remaining_time -= 1
            self.clock += 1

            self._admit_new_processes()

        if process.remaining_time <= 0:
            print(f"P{process.pid} return SIGINT")
            self.resources.release(process)
            self.finished.append(process)
            self._aging()
            self.last_pid = None
            return

        if not process.is_realtime:
            process.priority = min(
                Config.MAX_USER_PRIORITY,
                process.priority + 1
            )

        self._enqueue(process)
        self._aging()
        self.last_pid = process.pid

    def _aging(self) -> None:
        """
        Aging simples:
        se houver acúmulo de processos nas filas mais baixas,
        promove um processo para evitar starvation.
        """
        for lower_priority, higher_priority in ((3, 2), (2, 1)):
            if len(self.user_queues[lower_priority]) > 2:
                promoted_process = self.user_queues[lower_priority].popleft()
                promoted_process.priority = higher_priority
                self.user_queues[higher_priority].append(promoted_process)