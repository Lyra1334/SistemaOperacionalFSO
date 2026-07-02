#!/usr/bin/env python3
"""
Main.py

Ponto de entrada do pseudo-SO.
"""

import sys
from typing import List

import Config

from Errors import InputError
from Parsers.ProcessParser import ProcessParser
from Parsers.FileSystemParser import FileSystemParser
from Managers.MemoryManager import MemoryManager
from Managers.ResourceManager import ResourceManager
from Managers.FileSystemManager import FileSystemManager
from Scheduling.Scheduler import Scheduler
from Utils import format_page_faults


def main(argv: List[str]) -> int:
    if len(argv) == 4:
        processes_path = argv[1]
        files_path = argv[2]
        strings_path = argv[3]
    else:
        processes_path = Config.DEFAULT_PROCESSES_FILE
        files_path = Config.DEFAULT_FILESYSTEM_FILE
        strings_path = Config.DEFAULT_REFERENCES_FILE

    try:
        processes = ProcessParser.load(processes_path, strings_path)
        disk, operations = FileSystemParser.load(files_path)

        memory = MemoryManager()
        resources = ResourceManager()

        scheduler = Scheduler(processes, memory, resources)
        scheduler.run()

        file_system = FileSystemManager(disk, operations, processes)
        file_system.run()

        print(Config.PAGEFAULT_LABEL)

        for process in sorted(processes, key=lambda p: p.pid):
            print(f"P{process.pid} = {format_page_faults(process.page_faults)}")

        return 0

    except InputError as exc:
        print(f"ERRO DE ENTRADA: {exc}")
        return 1

    except Exception as exc:
        print(f"ERRO INESPERADO: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))