from dataclasses import dataclass, field
from typing import Dict, List

import Config


@dataclass
class Processo:
    pid: int
    tempoChegada: int
    prioridade: int
    tempoCpu: int
    workingSet: int
    impressora: int
    scanner: int
    modem: int
    sata: int
    referencias: List[int] = field(default_factory=list)

    tempoRestante: int = field(init=False)
    prioridadeOriginal: int = field(init=False)

    faltasPagina: int = 0
    quadros: List[int] = field(default_factory=list)
    ultimoUso: Dict[int, int] = field(default_factory=dict)

    memoriaSimulada: bool = False
    rejeitado: bool = False

    def __post_init__(self) -> None:
        self.tempoRestante = self.tempoCpu
        self.prioridadeOriginal = self.prioridade

    @property
    def ehTempoReal(self) -> bool:
        return self.prioridade == Config.PRIORIDADE_TEMPO_REAL