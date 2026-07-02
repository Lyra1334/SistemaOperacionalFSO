"""
ProcessManager.py

Gerenciador auxiliar de processos do pseudo-SO.

Responsável por:
- Armazenar processos por PID;
- Verificar existência de processos;
- Recuperar processos;
- Listar processos ordenados;
- Validar quantidade máxima de processos.
"""

from typing import Dict, List, Optional

import Config

from Errors import SchedulerError
from Models.Process import Process


class ProcessManager:

    def __init__(self, processes: List[Process]) -> None:
        if len(processes) > Config.MAX_PROCESSES:
            raise SchedulerError(
                f"Quantidade de processos excede o limite de {Config.MAX_PROCESSES}."
            )

        self.processes: List[Process] = sorted(
            processes,
            key=lambda process: (process.arrival_time, process.pid)
        )

        self.processes_by_pid: Dict[int, Process] = {
            process.pid: process
            for process in self.processes
        }

    def exists(self, pid: int) -> bool:
        return pid in self.processes_by_pid

    def get(self, pid: int) -> Optional[Process]:
        return self.processes_by_pid.get(pid)

    def get_or_raise(self, pid: int) -> Process:
        process = self.get(pid)

        if process is None:
            raise SchedulerError(f"Processo {pid} não existe.")

        return process

    def all(self) -> List[Process]:
        return self.processes[:]

    def ordered_by_pid(self) -> List[Process]:
        return sorted(
            self.processes,
            key=lambda process: process.pid
        )

    def ordered_by_arrival(self) -> List[Process]:
        return sorted(
            self.processes,
            key=lambda process: (process.arrival_time, process.pid)
        )

    def count(self) -> int:
        return len(self.processes)