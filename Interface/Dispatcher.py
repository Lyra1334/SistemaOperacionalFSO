"""
Dispatcher.py

Responsável por exibir as informações do processo antes da execução.
"""

import Config

from Models.Process import Process


class Dispatcher:

    @staticmethod
    def show_process_info(process: Process) -> None:
        print(Config.DISPATCHER_LABEL)
        print(f" PID: {process.pid}")
        print(f" frames: {process.working_set}")
        print(f" priority: {process.priority}")
        print(f" time: {process.cpu_time}")
        print(f" printers: {process.printer}")
        print(f" scanners: {process.scanner}")
        print(f" modems: {process.modem}")
        print(f" drives: {process.sata}")