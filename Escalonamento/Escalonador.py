"""
Escalonador.py

Escalonador do pseudo-SO.

Responsável por:
- admitir processos;
- organizar filas de tempo real e de usuário;
- aplicar FIFO para tempo real;
- aplicar múltiplas filas com realimentação para usuário;
- chamar o despachante;
- controlar execução e finalização dos processos.
"""

from collections import deque
from typing import Deque, Dict, List, Optional

import Config

from Interface.Despachante import Despachante
from Gerenciadores.GerenciadorMemoria import GerenciadorMemoria
from Gerenciadores.GerenciadorRecurso import GerenciadorRecurso
from Models.Processo import Processo


class Escalonador:

    def __init__(
        self,
        processos: List[Processo],
        memoria: GerenciadorMemoria,
        recursos: GerenciadorRecurso
    ) -> None:
        self.processos = sorted(
            processos,
            key=lambda processo: (processo.tempoChegada, processo.pid)
        )

        self.memoria = memoria
        self.recursos = recursos

        self.despachante = Despachante()

        self.filaTempoReal: Deque[Processo] = deque()

        self.filasUsuario: Dict[int, Deque[Processo]] = {
            1: deque(),
            2: deque(),
            3: deque()
        }

        self.aguardando: Deque[Processo] = deque()

        self.relogio = 0
        self.indiceProximaChegada = 0
        self.finalizados: List[Processo] = []
        self.ultimoPid = None

    def executar(self) -> None:
        while len(self.finalizados) < len(self.processos):
            self._admitirNovosProcessos()
            self._retentarProcessosAguardando()

            processo = self._escolherProximoProcesso()

            if processo is None:
                self.relogio += 1
                continue

            self._executar(processo)

    def _admitirNovosProcessos(self) -> None:
        while (
            self.indiceProximaChegada < len(self.processos)
            and self.processos[self.indiceProximaChegada].tempoChegada <= self.relogio
        ):
            processo = self.processos[self.indiceProximaChegada]
            self.indiceProximaChegada += 1

            if not self.memoria.validarProcesso(processo):
                print(
                    f"dispatcher => Processo {processo.pid} rejeitado: "
                    "working set maior que a área de memória permitida."
                )
                processo.rejeitado = True
                self.finalizados.append(processo)
                continue

            if not self.recursos.verificarProcesso(processo):
                print(
                    f"dispatcher => Processo {processo.pid} rejeitado: "
                    "requer mais recursos do que o possúido pelo sistema."
                )
                processo.rejeitado = True
                self.finalizados.append(processo)
                continue

            self.memoria.preCarregar(processo)

            if not self.recursos.alocar(processo):
                print(
                    f"dispatcher => Processo {processo.pid} aguardando recursos de E/S."
                )
                self.aguardando.append(processo)
                continue

            self._enfileirar(processo)

    def _retentarProcessosAguardando(self) -> None:
        if not self.aguardando:
            return

        restantes: Deque[Processo] = deque()

        while self.aguardando:
            processo = self.aguardando.popleft()

            if self.recursos.alocar(processo):
                self._enfileirar(processo)
            else:
                restantes.append(processo)

        self.aguardando = restantes

    def _enfileirar(self, processo: Processo) -> None:
        if processo.ehTempoReal:
            self.filaTempoReal.append(processo)
            return

        prioridade = min(max(processo.prioridade, 1), Config.MAX_PRIORIDADE_USUARIO)
        self.filasUsuario[prioridade].append(processo)

    def _escolherProximoProcesso(self) -> Optional[Processo]:
        if self.filaTempoReal:
            return self.filaTempoReal.popleft()

        for prioridade in range(1, Config.MAX_PRIORIDADE_USUARIO + 1):
            if self.filasUsuario[prioridade]:
                return self.filasUsuario[prioridade].popleft()

        return None

    def _executar(self, processo: Processo) -> None:

        if self.ultimoPid != processo.pid:
            if self.relogio > 0:
                print()
            self.despachante.exibirInformacoesProcesso(processo)
            print()
            print(f"process {processo.pid} =>")
            print(f"P{processo.pid} STARTED")

        self.memoria.simularReferencias(processo)

        if processo.ehTempoReal:
            quantum = processo.tempoRestante
        else:
            quantum = min(Config.QUANTUM_USUARIO, processo.tempoRestante)

        for _ in range(quantum):
            numeroInstrucao = processo.tempoCpu - processo.tempoRestante + 1

            print(f"P{processo.pid} instruction {numeroInstrucao}")

            processo.tempoRestante -= 1
            self.relogio += 1

            self._admitirNovosProcessos()

        if processo.tempoRestante <= 0:
            print(f"P{processo.pid} return SIGINT")
            self.recursos.liberar(processo)
            self.finalizados.append(processo)
            self._envelhecimento()
            self.ultimoPid = None
            return

        if not processo.ehTempoReal:
            processo.prioridade = min(
                Config.MAX_PRIORIDADE_USUARIO,
                processo.prioridade + 1
            )

        self._enfileirar(processo)
        self._envelhecimento()
        self.ultimoPid = processo.pid

    def _envelhecimento(self) -> None:
        """
        Aging simples:
        se houver acúmulo de processos nas filas mais baixas,
        promove um processo para evitar starvation.
        """
        for prioridadeMaisBaixa, prioridadeMaisAlta in ((3, 2), (2, 1)):
            if len(self.filasUsuario[prioridadeMaisBaixa]) > 2:
                processoPromovido = self.filasUsuario[prioridadeMaisBaixa].popleft()
                processoPromovido.prioridade = prioridadeMaisAlta
                self.filasUsuario[prioridadeMaisAlta].append(processoPromovido)