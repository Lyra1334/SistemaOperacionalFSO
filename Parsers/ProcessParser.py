"""
ProcessParser.py

Lê e valida Processes.txt e String.txt.
"""

from typing import List

import Config

from Errors import InputError
from Models.Process import Process
from Utils import parse_int, parse_01, read_non_empty_lines, split_csv


class ProcessParser:

    @staticmethod
    def load(processes_path: str, strings_path: str) -> List[Process]:
        process_lines = read_non_empty_lines(processes_path)
        string_lines = read_non_empty_lines(strings_path)

        if len(process_lines) > 1000:
            raise InputError(
                f"Quantidade de processos ({len(process_lines)}) excede o limite do sistema (máximo 1000)."
            )

        if len(process_lines) != len(string_lines):
            raise InputError(
                f"Quantidade de processos ({len(process_lines)}) diferente "
                f"da quantidade de strings ({len(string_lines)})."
            )

        processes: List[Process] = []

        for pid, line in enumerate(process_lines):
            parts = split_csv(line)

            if len(parts) != 8:
                raise InputError(
                    f"Linha {pid + 1} de processos deve ter 8 campos."
                )

            arrival_time = parse_int(parts[0], "tempo de inicialização")
            priority = parse_int(parts[1], "prioridade")
            cpu_time = parse_int(parts[2], "tempo de processador")
            working_set = min(parse_int(parts[3], "working set"), Config.USER_MEMORY_FRAMES) if priority != 0 else min(parse_int(parts[3], "working set"), Config.REALTIME_MEMORY_FRAMES)

            printer = parse_01(parts[4], "requisição de impressora")
            scanner = parse_01(parts[5], "requisição de scanner")
            modem = parse_01(parts[6], "requisição de modem")
            sata = parse_01(parts[7], "requisição de SATA")

            if arrival_time < 0:
                raise InputError("Tempo de inicialização não pode ser negativo.")
            if arrival_time > 1000000:
                raise InputError("Tempo de inicialização muito grande.")

            if cpu_time <= 0:
                raise InputError("Tempo de processador deve ser maior que zero.")
            if cpu_time > 1000000:
                raise InputError("Tempo de processador muito grande.")

            if working_set <= 0:
                raise InputError("Working set deve ser maior que zero.")

            if priority < Config.REALTIME_PRIORITY or priority > Config.MAX_USER_PRIORITY:
                raise InputError("Prioridade deve ser 0, 1, 2 ou 3.")

            if priority == Config.REALTIME_PRIORITY:
                printer = 0
                scanner = 0
                modem = 0
                sata = 0

            references = []
            for page_str in split_csv(string_lines[pid]):
                page = parse_int(page_str, "página")
                if page < 0:
                    raise InputError(f"Número de página não pode ser negativo: {page}")
                
                # Limitação teórica de endereçamento virtual de 16 bits (máximo 64 páginas de 1 KB).
                # Caso haja necessidade de suportar referências a páginas lógicas maiores que 63 na simulação,
                # a restrição abaixo pode ser comentada ou removida.
                if page > 63:
                    raise InputError(f"Número de página excede o limite de endereçamento virtual de 16 bits (máximo 63): {page}")
                
                references.append(page)

            processes.append(
                Process(
                    pid=pid,
                    arrival_time=arrival_time,
                    priority=priority,
                    cpu_time=cpu_time,
                    working_set=working_set,
                    printer=printer,
                    scanner=scanner,
                    modem=modem,
                    sata=sata,
                    references=references
                )
            )

        return processes