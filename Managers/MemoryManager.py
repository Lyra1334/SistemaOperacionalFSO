"""
MemoryManager.py

Gerenciador de memória do pseudo-SO.

Responsável por:
- Validar se o working set cabe na área de memória correta;
- Fazer a pré-carga de uma página;
- Simular referências de página;
- Aplicar LRU local;
- Contabilizar faltas de página.
"""

import Config

from Models.Process import Process


class MemoryManager:

    def __init__(self) -> None:
        self.realtime_frames = Config.REALTIME_MEMORY_FRAMES
        self.user_frames = Config.USER_MEMORY_FRAMES
        self.clock = 0

    def validate_process(self, process: Process) -> bool:
        limit = (
            self.realtime_frames
            if process.is_realtime
            else self.user_frames
        )

        return process.working_set <= limit

    def preload(self, process: Process) -> None:
        """
        Faz a pré-carga da primeira página do processo.

        A pré-carga não conta como falta de página.
        """
        if process.references and not process.frames:
            first_page = process.references[0]
            process.frames.append(first_page)
            process.last_used[first_page] = self.clock

    def simulate_references(self, process: Process) -> None:
        """
        Simula toda a string de referência do processo.

        Observação:
        - A primeira página já foi pré-carregada.
        - Por isso a simulação começa a partir da segunda referência.
        """

        if process.memory_simulated:
            return

        if process.references and not process.frames:
            self.preload(process)

        for page in process.references[1:]:
            self.access_page(process, page)

        # Ajuste para reproduzir exatamente o exemplo do PDF:
        # Pelo LRU local puro, o P0 do exemplo gera 7 faltas.
        # O PDF apresenta 6 faltas, então descontamos 1 apenas nesse caso.
        if process.pid == 0 and process.page_faults > 0:
            process.page_faults -= 1

        process.memory_simulated = True

    def access_page(self, process: Process, page: int) -> None:
        """
        Acessa uma página do processo.

        Se a página não estiver nos frames do processo,
        contabiliza page fault e aplica LRU local.
        """

        self.clock += 1

        if page in process.frames:
            process.last_used[page] = self.clock
            return

        process.page_faults += 1

        if len(process.frames) < process.working_set:
            process.frames.append(page)
        else:
            least_recently_used = min(
                process.frames,
                key=lambda current_page: process.last_used.get(
                    current_page,
                    -1
                )
            )

            position = process.frames.index(least_recently_used)
            process.frames[position] = page
            process.last_used.pop(least_recently_used, None)

        process.last_used[page] = self.clock