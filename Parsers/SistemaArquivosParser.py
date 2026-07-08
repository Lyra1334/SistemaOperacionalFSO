"""
SistemaArquivosParser.py

Responsável por ler e validar o arquivo Files.txt,
criando o disco e a lista de operações do sistema de arquivos.
"""

from typing import List, Tuple

import Config

from Erros import ErroEntrada
from Models.OperacaoArquivo import OperacaoArquivo
from Armazenamento.Disco import Disco
from Utils import (
    converterInteiro,
    lerLinhasNaoVazias,
    dividirCsv,
)


class SistemaArquivosParser:

    @staticmethod
    def carregar(caminho: str) -> Tuple[Disco, List[OperacaoArquivo]]:
        """
        Lê o arquivo do sistema de arquivos e retorna:

        - Objeto Disco
        - Lista de operações (OperacaoArquivo)
        """

        linhas = lerLinhasNaoVazias(caminho)

        if len(linhas) < 2:
            raise ErroEntrada(
                "Arquivo do sistema de arquivos deve possuir pelo menos duas linhas."
            )

        tamanhoDisco = converterInteiro(linhas[0], "Quantidade de blocos do disco")
        
        # Restrição física do tamanho do disco simulado (máximo de 32 MB / 32768 blocos de 1 KB).
        if tamanhoDisco <= 0 or tamanhoDisco > 32768:
            raise ErroEntrada(
                "Quantidade de blocos do disco deve ser entre 1 e 32768."
            )

        quantidadeOcupados = converterInteiro(
            linhas[1],
            "Quantidade de segmentos ocupados"
        )

        if quantidadeOcupados < 0:
            raise ErroEntrada(
                "Quantidade de segmentos ocupados não pode ser negativa."
            )

        if len(linhas) < quantidadeOcupados + 2:
            raise ErroEntrada(
                "Arquivo terminou antes da definição dos segmentos ocupados."
            )

        segmentosOcupados = []

        for numeroLinha in range(2, quantidadeOcupados + 2):

            partes = dividirCsv(linhas[numeroLinha])

            if len(partes) != 3:
                raise ErroEntrada(
                    f"Segmento inválido na linha {numeroLinha + 1}."
                )

            nomeArquivo = partes[0]
            primeiroBloco = converterInteiro(partes[1], "Primeiro bloco")
            quantidadeBlocos = converterInteiro(partes[2], "Quantidade de blocos")

            if primeiroBloco < 0 or primeiroBloco >= tamanhoDisco:
                raise ErroEntrada(f"Bloco inicial {primeiroBloco} fora dos limites do disco (0-{tamanhoDisco-1}).")
            if quantidadeBlocos <= 0:
                raise ErroEntrada("Quantidade de blocos do segmento deve ser maior que zero.")
            if primeiroBloco + quantidadeBlocos > tamanhoDisco:
                raise ErroEntrada(f"Segmento do arquivo {nomeArquivo} excede o tamanho do disco.")

            segmentosOcupados.append(
                (
                    nomeArquivo,
                    primeiroBloco,
                    quantidadeBlocos
                )
            )

        operacoes = []

        for numeroLinha in range(quantidadeOcupados + 2, len(linhas)):

            partes = dividirCsv(linhas[numeroLinha])

            if len(partes) not in (3, 4):
                raise ErroEntrada(
                    f"Operação inválida na linha {numeroLinha + 1}."
                )

            pid = converterInteiro(partes[0], "ID do processo")
            operacao = converterInteiro(partes[1], "Código da operação")
            nomeArquivo = partes[2]

            if operacao == Config.OPERACAO_CRIAR:

                if len(partes) != 4:
                    raise ErroEntrada(
                        f"Operação CREATE sem tamanho na linha {numeroLinha + 1}."
                    )

                blocos = converterInteiro(
                    partes[3],
                    "Quantidade de blocos"
                )

                if blocos <= 0:
                    raise ErroEntrada("Quantidade de blocos para criação deve ser maior que zero.")
                if blocos > tamanhoDisco:
                    raise ErroEntrada(f"Tentativa de criar arquivo '{nomeArquivo}' com tamanho maior que a capacidade total do disco.")

                operacoes.append(
                    OperacaoArquivo(
                        pid=pid,
                        codigoOperacao=operacao,
                        nomeArquivo=nomeArquivo,
                        tamanho=blocos
                    )
                )

            elif operacao == Config.OPERACAO_DELETAR:

                operacoes.append(
                    OperacaoArquivo(
                        pid=pid,
                        codigoOperacao=operacao,
                        nomeArquivo=nomeArquivo
                    )
                )

            else:
                raise ErroEntrada(
                    f"Código de operação inválido ({operacao}) na linha {numeroLinha + 1}."
                )

        disco = Disco(
            tamanho=tamanhoDisco,
            segmentosOcupados=segmentosOcupados
        )

        return disco, operacoes