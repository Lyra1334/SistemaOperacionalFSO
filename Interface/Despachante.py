"""
Despachante.py

Responsável por exibir as informações do processo antes da execução.
"""

import Config

from Models.Processo import Processo


class Despachante:

    @staticmethod
    def exibirInformacoesProcesso(processo: Processo) -> None:
        print(Config.ROTULO_DESPACHANTE)
        print(f" PID: {processo.pid}")
        print(f" frames: {processo.workingSet}")
        print(f" priority: {processo.prioridade}")
        print(f" time: {processo.tempoCpu}")
        print(f" printers: {processo.impressora}")
        print(f" scanners: {processo.scanner}")
        print(f" modems: {processo.modem}")
        print(f" drives: {processo.sata}")