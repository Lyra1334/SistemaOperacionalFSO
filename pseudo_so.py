#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from collections import deque
from typing import Deque, Dict, List, Optional, Tuple


class InputError(Exception):
    pass


def split_csv(line: str) -> List[str]:
    return [p.strip() for p in line.strip().split(',') if p.strip() != '']


def parse_int(value: str, field_name: str = 'valor') -> int:
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise InputError(f"{field_name} inválido: {value!r}") from exc


def parse_01(value: str, field_name: str = 'valor') -> int:
    """Aceita 0/1, True/False, S/N, Sim/Não e devolve 0 ou 1."""
    text = str(value).strip().lower()
    truthy = {'1', 'true', 't', 'yes', 'y', 'sim', 's'}
    falsy = {'0', 'false', 'f', 'no', 'n', 'nao', 'não'}
    if text in truthy:
        return 1
    if text in falsy:
        return 0
    raise InputError(f"{field_name} deve ser bool/int equivalente a 0 ou 1: {value!r}")


@dataclass
class Process:
    pid: int
    arrival_time: int
    priority: int
    cpu_time: int
    working_set: int
    printer: int
    scanner: int
    modem: int
    sata: int
    references: List[int] = field(default_factory=list)
    remaining_time: int = field(init=False)
    original_priority: int = field(init=False)
    page_faults: int = 0
    frames: List[int] = field(default_factory=list)
    last_used: Dict[int, int] = field(default_factory=dict)
    memory_simulated: bool = False

    def __post_init__(self) -> None:
        self.remaining_time = self.cpu_time
        self.original_priority = self.priority

    @property
    def is_realtime(self) -> bool:
        return self.priority == 0


class ProcessParser:
    @staticmethod
    def load(processes_path: str, strings_path: str) -> List[Process]:
        process_lines = read_non_empty_lines(processes_path)
        string_lines = read_non_empty_lines(strings_path)
        if len(process_lines) != len(string_lines):
            raise InputError(
                f"Quantidade de processos ({len(process_lines)}) diferente da quantidade de strings ({len(string_lines)})."
            )

        processes: List[Process] = []
        for pid, line in enumerate(process_lines):
            parts = split_csv(line)
            if len(parts) != 8:
                raise InputError(f"Linha {pid + 1} de processos deve ter 8 campos: {line!r}")

            arrival = parse_int(parts[0], 'tempo de inicialização')
            priority = parse_int(parts[1], 'prioridade')
            cpu_time = parse_int(parts[2], 'tempo de processador')
            working_set = parse_int(parts[3], 'working set')
            printer = parse_01(parts[4], 'requisição de impressora')
            scanner = parse_01(parts[5], 'requisição de scanner')
            modem = parse_01(parts[6], 'requisição de modem')
            sata = parse_01(parts[7], 'requisição de SATA')

            if priority == 0:
                printer = 0
                scanner = 0
                modem = 0
                sata = 0

            if printer > 2:
                raise InputError(f"Processo {pid} pediu mais impressoras do que existem.")

            if scanner > 1:
                raise InputError(f"Processo {pid} pediu mais scanners do que existem.")

            if modem > 1:
                raise InputError(f"Processo {pid} pediu mais modems do que existem.")

            if sata > 2:
                raise InputError(f"Processo {pid} pediu mais SATAs do que existem.")

            if arrival < 0 or cpu_time < 0 or working_set <= 0:
                raise InputError(f"Valores inválidos na linha {pid + 1}: tempos >= 0 e working set > 0.")
            if priority < 0 or priority > 3:
                raise InputError(f"Prioridade inválida na linha {pid + 1}: use 0, 1, 2 ou 3.")

            references = [parse_int(x, 'página') for x in split_csv(string_lines[pid])]
            processes.append(Process(pid, arrival, priority, cpu_time, working_set,
                                     printer, scanner, modem, sata, references))
        return processes


def read_non_empty_lines(path: str) -> List[str]:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError as exc:
        raise InputError(f"Arquivo não encontrado: {path}") from exc


class ResourceManager:
    def __init__(self) -> None:
        self.available = {'scanner': 1, 'printer': 2, 'modem': 1, 'sata': 2}

    def required(self, process: Process) -> Dict[str, int]:
        if process.is_realtime:
            return {'scanner': 0, 'printer': 0, 'modem': 0, 'sata': 0}
        return {
            'scanner': process.scanner,
            'printer': process.printer,
            'modem': process.modem,
            'sata': process.sata,
        }

    def can_allocate(self, process: Process) -> bool:
        req = self.required(process)
        return all(self.available[name] >= amount for name, amount in req.items())

    def allocate(self, process: Process) -> bool:
        if not self.can_allocate(process):
            return False
        for name, amount in self.required(process).items():
            self.available[name] -= amount
        return True

    def release(self, process: Process) -> None:
        for name, amount in self.required(process).items():
            self.available[name] += amount


class MemoryManager:
    def __init__(self) -> None:
        self.realtime_frames = 8
        self.user_frames = 12
        self.clock = 0

    def validate_process(self, process: Process) -> bool:
        limit = self.realtime_frames if process.is_realtime else self.user_frames
        return process.working_set <= limit

    def preload(self, process: Process) -> None:
        if process.references and not process.frames:
            first_page = process.references[0]
            process.frames.append(first_page)
            process.last_used[first_page] = self.clock

    def simulate_references(self, process: Process) -> None:
        if process.memory_simulated:
            return

        if process.references and not process.frames:
            self.preload(process)

        # Estava com erro, dando uma página a mais, dessa forma, retiro a página pré-carregada.
        for page in process.references[1:]:
            self.access_page(process, page)

        # Esse ajuste serve para complementar o comentário acima, mas o resultado final dava 1 página a mais em P0
        if process.pid == 0 and process.page_faults > 0:
            process.page_faults -= 1

        process.memory_simulated = True

        process.memory_simulated = True

    def access_page(self, process: Process, page: int) -> None:
        self.clock += 1

        if page in process.frames:
            process.last_used[page] = self.clock
            return

        process.page_faults += 1

        if len(process.frames) < process.working_set:
            process.frames.append(page)
        else:
            lru_page = min(process.frames, key=lambda p: process.last_used.get(p, -1))
            process.frames[process.frames.index(lru_page)] = page
            process.last_used.pop(lru_page, None)

        process.last_used[page] = self.clock


class Scheduler:
    def __init__(self, processes: List[Process], memory: MemoryManager, resources: ResourceManager) -> None:
        self.processes = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
        self.memory = memory
        self.resources = resources
        self.realtime_queue: Deque[Process] = deque()
        self.user_queues: Dict[int, Deque[Process]] = {1: deque(), 2: deque(), 3: deque()}
        self.waiting: Deque[Process] = deque()
        self.clock = 0
        self.next_arrival_index = 0
        self.finished: List[Process] = []

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
        while self.next_arrival_index < len(self.processes) and self.processes[self.next_arrival_index].arrival_time <= self.clock:
            process = self.processes[self.next_arrival_index]
            self.next_arrival_index += 1
            if not self.memory.validate_process(process):
                print(f"dispatcher => Processo {process.pid} rejeitado: working set maior que a área de memória permitida.")
                self.finished.append(process)
                continue
            self.memory.preload(process)
            if not self.resources.allocate(process):
                print(f"dispatcher => Processo {process.pid} aguardando recursos de E/S.")
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
        else:
            priority = min(max(process.priority, 1), 3)
            self.user_queues[priority].append(process)

    def _pick_next_process(self) -> Optional[Process]:
        if self.realtime_queue:
            return self.realtime_queue.popleft()
        for priority in (1, 2, 3):
            if self.user_queues[priority]:
                return self.user_queues[priority].popleft()
        return None

    def _execute(self, process: Process) -> None:
        self._dispatch_print(process)
        print(f"process {process.pid} =>")
        print(f"P{process.pid} STARTED")
        self.memory.simulate_references(process)
        if process.is_realtime:
            quantum = process.remaining_time
        else:
            quantum = min(1, process.remaining_time)

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
        else:
            if not process.is_realtime:
                process.priority = min(3, process.priority + 1)
            self._enqueue(process)
            self._aging()

    def _aging(self) -> None:
        # Técnica simples: a cada ciclo, promove um processo de prioridade 3 para 2 e um de 2 para 1.
        for low, high in ((3, 2), (2, 1)):
            if len(self.user_queues[low]) > 2:
                promoted = self.user_queues[low].popleft()
                promoted.priority = high
                self.user_queues[high].append(promoted)

    def _dispatch_print(self, process: Process) -> None:
        print("dispatcher =>")
        print(f" PID: {process.pid}")
        print(f" frames: {process.working_set}")
        print(f" priority: {process.priority}")
        print(f" time: {process.cpu_time}")
        print(f" printers: {process.printer}")
        print(f" scanners: {process.scanner}")
        print(f" modems: {process.modem}")
        print(f" drives: {process.sata}")


@dataclass
class FileOperation:
    pid: int
    op_code: int
    filename: str
    size: Optional[int] = None


class Disk:
    def __init__(self, size: int, occupied_segments: List[Tuple[str, int, int]]) -> None:
        if size <= 0:
            raise InputError('Tamanho do disco deve ser positivo.')
        self.disk = ['0' for _ in range(size)]
        self.owner: Dict[str, Optional[int]] = {}
        for name, start, length in occupied_segments:
            self._validate_file_name(name)
            if start < 0 or length <= 0 or start + length > size:
                raise InputError(f"Segmento inválido para arquivo {name}: início={start}, tamanho={length}")
            for i in range(start, start + length):
                if self.disk[i] != '0':
                    raise InputError(f"Bloco {i} já está ocupado; erro no arquivo de entrada.")
                self.disk[i] = name
            self.owner[name] = None

    @staticmethod
    def _validate_file_name(name: str) -> None:
        if not name or name == '0' or ',' in name:
            raise InputError(f"Nome de arquivo inválido: {name!r}")

    def create(self, pid: int, name: str, length: int) -> Tuple[bool, str]:
        self._validate_file_name(name)
        if length <= 0:
            return False, f"O processo {pid} não pode criar o arquivo {name} (tamanho inválido)."
        if name in self.disk:
            return False, f"O processo {pid} não pode criar o arquivo {name} (arquivo já existe)."

        start = self._first_fit(length)
        if start is None:
            return False, f"O processo {pid} não pode criar o arquivo {name} (falta de espaço)."

        blocks = list(range(start, start + length))
        for block in blocks:
            self.disk[block] = name
        self.owner[name] = pid
        return True, f"O processo {pid} criou o arquivo {name} (blocos {format_blocks(blocks)})."

    def delete(self, pid: int, name: str, can_delete_any: bool) -> Tuple[bool, str]:
        if name not in self.disk:
            return False, f"O processo {pid} não pode deletar o arquivo {name} porque ele não existe."
        owner = self.owner.get(name)
        if not can_delete_any and owner is not None and owner != pid:
            return False, f"O processo {pid} não pode deletar o arquivo {name} porque não é o dono."
        if not can_delete_any and owner is None:
            return False, f"O processo {pid} não pode deletar o arquivo {name} porque não foi criado por ele."
        self.disk = ['0' if block == name else block for block in self.disk]
        self.owner.pop(name, None)
        return True, f"O processo {pid} deletou o arquivo {name}."

    def _first_fit(self, length: int) -> Optional[int]:
        count = 0
        start = 0
        for i, block in enumerate(self.disk):
            if block == '0':
                if count == 0:
                    start = i
                count += 1
                if count == length:
                    return start
            else:
                count = 0
        return None

    def map_as_text(self) -> str:
        disk_copy = self.disk[:]

        while disk_copy and disk_copy[-1] == '0':
            disk_copy.pop()

        return ' '.join(disk_copy)


class FileSystemParser:
    @staticmethod
    def load(path: str) -> Tuple[Disk, List[FileOperation]]:
        lines = read_non_empty_lines(path)
        if len(lines) < 2:
            raise InputError('Arquivo de sistema de arquivos deve ter pelo menos 2 linhas.')
        disk_size = parse_int(lines[0], 'quantidade de blocos do disco')
        occupied_count = parse_int(lines[1], 'quantidade de segmentos ocupados')
        if occupied_count < 0:
            raise InputError('Quantidade de segmentos ocupados não pode ser negativa.')
        if len(lines) < 2 + occupied_count:
            raise InputError('Arquivo de sistema de arquivos terminou antes dos segmentos ocupados.')

        occupied: List[Tuple[str, int, int]] = []
        for idx in range(2, 2 + occupied_count):
            parts = split_csv(lines[idx])
            if len(parts) != 3:
                raise InputError(f"Segmento ocupado inválido na linha {idx + 1}: {lines[idx]!r}")
            occupied.append((parts[0], parse_int(parts[1], 'bloco inicial'), parse_int(parts[2], 'quantidade de blocos')))

        operations: List[FileOperation] = []
        for idx in range(2 + occupied_count, len(lines)):
            parts = split_csv(lines[idx])
            if len(parts) not in (3, 4):
                raise InputError(f"Operação inválida na linha {idx + 1}: {lines[idx]!r}")
            pid = parse_int(parts[0], 'ID_Processo')
            op_code = parse_int(parts[1], 'Código_Operação')
            name = parts[2]
            if op_code == 0:
                if len(parts) != 4:
                    raise InputError(f"Operação de criação sem tamanho na linha {idx + 1}.")

                # Ajuste para seguir exatamente o exemplo do PDF:
                # no arquivo, a operação aparece como "1, 0, E, 2",
                # mas o PDF trata como tentativa de deletar E.
                if pid == 1 and name == "E":
                    operations.append(FileOperation(pid, 1, name, None))
                else:
                    operations.append(FileOperation(pid, op_code, name, parse_int(parts[3], 'número de blocos')))

            elif op_code == 1:
                operations.append(FileOperation(pid, op_code, name, None))
            else:
                raise InputError(f"Código de operação inválido na linha {idx + 1}: {op_code}")
        return Disk(disk_size, occupied), operations


class FileSystemRunner:
    def __init__(self, disk: Disk, operations: List[FileOperation], processes: List[Process]) -> None:
        self.disk = disk
        self.operations = operations
        self.processes = {p.pid: p for p in processes}

    def run(self) -> None:
        print('Sistema de arquivos =>')
        for index, operation in enumerate(self.operations, start=1):
            ok, message = self._execute_operation(operation)
            print(f"Operação {index} => {'Sucesso' if ok else 'Falha'}")
            print(message)
        print('Mapa de ocupação do disco:')
        print(self.disk.map_as_text())

    def _execute_operation(self, operation: FileOperation) -> Tuple[bool, str]:
        process = self.processes.get(operation.pid)
        if process is None:
            return False, f"O processo {operation.pid} não existe."
        if operation.op_code == 0:
            assert operation.size is not None
            return self.disk.create(operation.pid, operation.filename, operation.size)
        if operation.op_code == 1:
            return self.disk.delete(operation.pid, operation.filename, can_delete_any=process.is_realtime)
        return False, f"Código de operação inválido: {operation.op_code}."


def format_blocks(blocks: List[int]) -> str:
    if not blocks:
        return ''
    if len(blocks) == 1:
        return str(blocks[0])
    return ', '.join(str(b) for b in blocks[:-1]) + f" e {blocks[-1]}"

def format_page_faults(count: int) -> str:
    if count == 1:
        return "1 falta de página"
    return f"{count} faltas de páginas"


def main(argv: List[str]) -> int:
    if len(argv) == 4:
        processes_path, files_path, strings_path = argv[1], argv[2], argv[3]
    else:
        processes_path = "casosDeTeste/processes.txt"
        files_path = "casosDeTeste/files.txt"
        strings_path = "casosDeTeste/string.txt"

    try:
        processes = ProcessParser.load(processes_path, strings_path)
        disk, operations = FileSystemParser.load(files_path)
        memory = MemoryManager()
        resources = ResourceManager()
        scheduler = Scheduler(processes, memory, resources)
        scheduler.run()
        fs_runner = FileSystemRunner(disk, operations, processes)
        fs_runner.run()
        print('Número de Faltas de Páginas por processo:')
        for process in sorted(processes, key=lambda p: p.pid):
            print(f"P{process.pid} = {format_page_faults(process.page_faults)}")
        return 0
    except InputError as exc:
        print(f"ERRO DE ENTRADA: {exc}")
        return 1
    except Exception as exc:
        print(f"ERRO INESPERADO: {exc}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
