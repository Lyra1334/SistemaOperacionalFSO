"""
GerenciadorProcesso.py

Gerenciador auxiliar de processos do pseudo-SO.

Responsável por:
- Armazenar processos por PID;
- Verificar existência de processos;
- Recuperar processos;
- Listar processos ordenados;
- Validar quantidade máxima de processos.
"""

from typing import Dict, List, Optional

from Core import Config

from Core.Erros import ErroEscalonador
from Models.Processo import Processo


class GerenciadorProcesso:

    def __init__(self, processos: List[Processo]) -> None:
        if len(processos) > Config.MAX_PROCESSOS:
            raise ErroEscalonador(
                f"Quantidade de processos excede o limite de {Config.MAX_PROCESSOS}."
            )

        self.processos: List[Processo] = sorted(
            processos,
            key=lambda processo: (processo.tempoChegada, processo.pid)
        )

        self.processosPorPid: Dict[int, Processo] = {
            processo.pid: processo
            for processo in self.processos
        }

    def existe(self, pid: int) -> bool:
        return pid in self.processosPorPid

    def obter(self, pid: int) -> Optional[Processo]:
        return self.processosPorPid.get(pid)

    def obterOuLancarErro(self, pid: int) -> Processo:
        processo = self.obter(pid)

        if processo is None:
            raise ErroEscalonador(f"Processo {pid} não existe.")

        return processo

    def todos(self) -> List[Processo]:
        return self.processos[:]

    def ordenadosPorPid(self) -> List[Processo]:
        return sorted(
            self.processos,
            key=lambda processo: processo.pid
        )

    def ordenadosPorChegada(self) -> List[Processo]:
        return sorted(
            self.processos,
            key=lambda processo: (processo.tempoChegada, processo.pid)
        )

    def quantidade(self) -> int:
        return len(self.processos)