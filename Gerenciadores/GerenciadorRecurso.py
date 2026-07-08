"""
GerenciadorRecurso.py

Gerenciador de recursos de Entrada/Saída.

Responsável por:
- Verificar disponibilidade dos recursos;
- Alocar recursos;
- Liberar recursos;
- Informar o estado atual dos dispositivos.
"""

from typing import Dict

import Config

from Erros import ErroGerenciadorRecurso
from Models.Processo import Processo


class GerenciadorRecurso:

    def __init__(self) -> None:

        self.disponiveis: Dict[str, int] = {
            "scanner": Config.TOTAL_SCANNERS,
            "impressora": Config.TOTAL_IMPRESSORAS,
            "modem": Config.TOTAL_MODEMS,
            "sata": Config.TOTAL_DRIVES_SATA,
        }
        self.alocacoesAtivas: Dict[int, Dict[str, int]] = {}

    def verificarProcesso(self, processo: Processo) -> bool:
        """
        Verifica se um processo pede mais recursos que o fisicamente disponível.
        """
        if (processo.scanner > Config.TOTAL_SCANNERS or
            processo.impressora > Config.TOTAL_IMPRESSORAS or
            processo.modem > Config.TOTAL_MODEMS or
            processo.sata > Config.TOTAL_DRIVES_SATA):
            return False
        return True

    def necessarios(self, processo: Processo) -> Dict[str, int]:
        """
        Retorna os recursos necessários para um processo.

        Processos de tempo real não utilizam recursos de E/S.
        """

        if processo.ehTempoReal:
            return {
                "scanner": 0,
                "impressora": 0,
                "modem": 0,
                "sata": 0,
            }

        return {
            "scanner": processo.scanner,
            "impressora": processo.impressora,
            "modem": processo.modem,
            "sata": processo.sata,
        }

    def podeAlocar(self, processo: Processo) -> bool:
        """
        Verifica se todos os recursos necessários estão disponíveis.
        """

        recursosNecessarios = self.necessarios(processo)

        return all(
            self.disponiveis[recurso] >= quantidade
            for recurso, quantidade in recursosNecessarios.items()
        )

    def alocar(self, processo: Processo) -> bool:
        """
        Tenta alocar os recursos do processo.

        Retorna:
            True  -> recursos alocados.
            False -> recursos indisponíveis.
        """

        if not self.podeAlocar(processo):
            return False

        recursosNecessarios = self.necessarios(processo)

        for recurso, quantidade in recursosNecessarios.items():
            self.disponiveis[recurso] -= quantidade

        if any(quantidade > 0 for quantidade in recursosNecessarios.values()):
            self.alocacoesAtivas[processo.pid] = recursosNecessarios

        return True

    def liberar(self, processo: Processo) -> None:
        """
        Libera todos os recursos utilizados pelo processo.
        """

        recursosNecessarios = self.necessarios(processo)
        possuiRecursos = any(quantidade > 0 for quantidade in recursosNecessarios.values())

        if possuiRecursos:
            if processo.pid not in self.alocacoesAtivas:
                raise ErroGerenciadorRecurso(
                    f"Tentativa de liberar recursos não alocados para o processo {processo.pid}."
                )
            self.alocacoesAtivas.pop(processo.pid)

        for recurso, quantidade in recursosNecessarios.items():
            self.disponiveis[recurso] += quantidade

    def reiniciar(self) -> None:
        """
        Restaura o estado inicial dos recursos.
        """

        self.disponiveis = {
            "scanner": Config.TOTAL_SCANNERS,
            "impressora": Config.TOTAL_IMPRESSORAS,
            "modem": Config.TOTAL_MODEMS,
            "sata": Config.TOTAL_DRIVES_SATA,
        }
        self.alocacoesAtivas.clear()

    def obterRecursosDisponiveis(self) -> Dict[str, int]:
        """
        Retorna uma cópia da quantidade de recursos disponíveis.
        """

        return self.disponiveis.copy()