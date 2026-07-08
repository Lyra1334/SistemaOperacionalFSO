#!/usr/bin/env python3
"""
Main.py

Ponto de entrada do pseudo-SO.
"""

import sys
from typing import List

import Config

from Erros import ErroEntrada
from Parsers.ProcessoParser import ProcessoParser
from Parsers.SistemaArquivosParser import SistemaArquivosParser
from Gerenciadores.GerenciadorMemoria import GerenciadorMemoria
from Gerenciadores.GerenciadorRecurso import GerenciadorRecurso
from Gerenciadores.GerenciadorSistemaArquivos import GerenciadorSistemaArquivos
from Escalonamento.Escalonador import Escalonador
from Utils import formatarFaltasPagina


def main(argv: List[str]) -> int:
    if len(argv) == 4:
        caminhoProcessos = argv[1]
        caminhoArquivos = argv[2]
        caminhoStrings = argv[3]
    else:
        caminhoProcessos = Config.ARQUIVO_PROCESSOS_PADRAO
        caminhoArquivos = Config.ARQUIVO_SISTEMA_ARQUIVOS_PADRAO
        caminhoStrings = Config.ARQUIVO_REFERENCIAS_PADRAO

    try:
        processos = ProcessoParser.carregar(caminhoProcessos, caminhoStrings)
        disco, operacoes = SistemaArquivosParser.carregar(caminhoArquivos)

        memoria = GerenciadorMemoria()
        recursos = GerenciadorRecurso()

        escalonador = Escalonador(processos, memoria, recursos)
        escalonador.executar()

        sistemaArquivos = GerenciadorSistemaArquivos(
            disco=disco,
            operacoes=operacoes,
            processos=processos,
            modoCompatibilidade=Config.HABILITAR_COMPATIBILIDADE_PDF
        )
        sistemaArquivos.executar()

        print(Config.ROTULO_FALTAS_PAGINA)

        for processo in sorted(processos, key=lambda p: p.pid):
            print(f"P{processo.pid} = {formatarFaltasPagina(processo.faltasPagina)}")

        return 0

    except ErroEntrada as exc:
        print(f"ERRO DE ENTRADA: {exc}")
        return 1

    except Exception as exc:
        print(f"ERRO INESPERADO: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))