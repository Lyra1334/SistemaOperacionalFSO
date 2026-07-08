"""
Disco.py

Representa o disco do pseudo-SO.

Responsabilidades:
- Armazenar os blocos do disco;
- Implementar o algoritmo First-Fit;
- Criar arquivos;
- Remover arquivos;
- Gerar o mapa final do disco.
"""

from typing import Dict, List, Optional, Tuple

import Config

from Erros import ErroSistemaArquivos
from Utils import formatarBlocos


class Disco:

    def __init__(
        self,
        tamanho: int,
        segmentosOcupados: List[Tuple[str, int, int]]
    ) -> None:

        if tamanho <= 0:
            raise ErroSistemaArquivos(
                "O disco deve possuir pelo menos um bloco."
            )

        self.tamanho = tamanho

        self.disco = [
            Config.BLOCO_LIVRE
            for _ in range(tamanho)
        ]

        # nome do arquivo -> PID do dono
        # Arquivos carregados inicialmente possuem dono None.
        self.dono: Dict[str, Optional[int]] = {}

        for nomeArquivo, inicio, comprimento in segmentosOcupados:
            self._carregarSegmento(
                nomeArquivo,
                inicio,
                comprimento
            )

    def _carregarSegmento(
        self,
        nomeArquivo: str,
        inicio: int,
        comprimento: int
    ) -> None:

        self._validarNome(nomeArquivo)

        if (
            inicio < 0
            or comprimento <= 0
            or inicio + comprimento > self.tamanho
        ):
            raise ErroSistemaArquivos(
                f"Segmento inválido para o arquivo {nomeArquivo}."
            )

        for bloco in range(inicio, inicio + comprimento):

            if self.disco[bloco] != Config.BLOCO_LIVRE:
                raise ErroSistemaArquivos(
                    f"Bloco {bloco} já está ocupado."
                )

            self.disco[bloco] = nomeArquivo

        self.dono[nomeArquivo] = None

    @staticmethod
    def _validarNome(nomeArquivo: str) -> None:
        """
        Realiza a validação lógica do nome do arquivo simulado.
        """
        if (
            not nomeArquivo
            or nomeArquivo == Config.BLOCO_LIVRE
            or "," in nomeArquivo
            or any(c.isspace() for c in nomeArquivo)
            or "/" in nomeArquivo
            or "\\" in nomeArquivo
            or "\x00" in nomeArquivo
            or any(not (c.isalnum() or c in ".-_") for c in nomeArquivo)
        ):
            raise ErroSistemaArquivos(
                f"Nome de arquivo inválido: {nomeArquivo}"
            )

    def criar(
        self,
        pid: int,
        nomeArquivo: str,
        comprimento: int
    ) -> Tuple[bool, str]:

        try:
            self._validarNome(nomeArquivo)
        except ErroSistemaArquivos as exc:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{nomeArquivo} (nome inválido)."
            )

        if comprimento <= 0:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{nomeArquivo} (tamanho inválido)."
            )

        if nomeArquivo in self.disco:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{nomeArquivo} (arquivo já existe)."
            )

        inicio = self._primeiroEncaixe(comprimento)

        if inicio is None:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{nomeArquivo} (falta de espaço)."
            )

        blocos = list(range(inicio, inicio + comprimento))

        for bloco in blocos:
            self.disco[bloco] = nomeArquivo

        self.dono[nomeArquivo] = pid

        return (
            True,
            f"O processo {pid} criou o arquivo "
            f"{nomeArquivo} (blocos {formatarBlocos(blocos)})."
        )

    def deletar(
        self,
        pid: int,
        nomeArquivo: str,
        podeDeletarQualquerUm: bool
    ) -> Tuple[bool, str]:

        try:
            self._validarNome(nomeArquivo)
        except ErroSistemaArquivos as exc:
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{nomeArquivo} (nome inválido)."
            )

        if nomeArquivo not in self.disco:
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{nomeArquivo} porque ele não existe."
            )

        dono = self.dono.get(nomeArquivo)

        if (
            not podeDeletarQualquerUm
            and dono is not None
            and dono != pid
        ):
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{nomeArquivo} porque não é o dono."
            )

        if (
            not podeDeletarQualquerUm
            and dono is None
        ):
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{nomeArquivo} porque não foi criado por ele."
            )

        self.disco = [
            Config.BLOCO_LIVRE
            if bloco == nomeArquivo
            else bloco
            for bloco in self.disco
        ]

        self.dono.pop(nomeArquivo, None)

        return (
            True,
            f"O processo {pid} deletou o arquivo {nomeArquivo}."
        )

    def _primeiroEncaixe(
        self,
        comprimento: int
    ) -> Optional[int]:

        livre = 0
        inicio = 0

        for index, bloco in enumerate(self.disco):

            if bloco == Config.BLOCO_LIVRE:

                if livre == 0:
                    inicio = index

                livre += 1

                if livre == comprimento:
                    return inicio

            else:
                livre = 0

        return None

    def mapaComoTexto(self) -> str:
        """
        Retorna o mapa de ocupação do disco formatado com barras verticais
        e espaços para cada bloco, cobrindo a capacidade total.
        """
        partes = []
        for bloco in self.disco:
            if bloco == Config.BLOCO_LIVRE:
                partes.append("  ")
            else:
                partes.append(f" {bloco} ")
        return "|" + "|".join(partes) + "|"