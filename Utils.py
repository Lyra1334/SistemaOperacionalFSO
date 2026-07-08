"""
Utils.py

Funções auxiliares usadas em várias partes do pseudo-SO.
"""

from typing import List

from Erros import ErroEntrada


def dividirCsv(linha: str) -> List[str]:
    """
    Divide uma linha CSV simples, removendo espaços extras.
    """
    return [parte.strip() for parte in linha.strip().split(",") if parte.strip() != ""]


def converterInteiro(valor: str, nomeCampo: str = "valor") -> int:
    """
    Converte um valor para inteiro, lançando ErroEntrada em caso de erro.
    """
    try:
        return int(str(valor).strip())
    except ValueError as exc:
        raise ErroEntrada(f"{nomeCampo} inválido: {valor!r}") from exc


def converterBooleano(valor: str, nomeCampo: str = "valor") -> int:
    """
    Aceita estritamente representações de booleanos equivalentes a 0 ou 1,
    garantindo que qualquer outro valor inteiro ou tipo de dado seja rejeitado.
    """
    limpo = str(valor).strip()
    try:
        valInt = int(limpo)
        if valInt == 1:
            return 1
        if valInt == 0:
            return 0
        raise ErroEntrada(f"{nomeCampo} deve ser estritamente 0 ou 1: {valor!r}")
    except ValueError:
        texto = limpo.lower()
        verdadeiro = {"true", "t", "yes", "y", "sim", "s"}
        falso = {"false", "f", "no", "n", "nao", "não"}

        if texto in verdadeiro:
            return 1

        if texto in falso:
            return 0

        raise ErroEntrada(f"{nomeCampo} deve ser bool/int equivalente a 0 ou 1: {valor!r}")


def lerLinhasNaoVazias(caminho: str) -> List[str]:
    """
    Lê um arquivo e retorna apenas as linhas não vazias.
    """
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return [linha.strip() for linha in arquivo if linha.strip()]
    except FileNotFoundError as exc:
        raise ErroEntrada(f"Arquivo não encontrado: {caminho}") from exc


def formatarBlocos(blocos: List[int]) -> str:
    """
    Formata uma lista de blocos no padrão:
    0
    0 e 1
    0, 1 e 2
    """
    if not blocos:
        return ""

    if len(blocos) == 1:
        return str(blocos[0])

    return ", ".join(str(bloco) for bloco in blocos[:-1]) + f" e {blocos[-1]}"


def formatarFaltasPagina(quantidade: int) -> str:
    """
    Formata a quantidade de faltas de página com singular/plural.
    """
    if quantidade == 1:
        return "1 falta de página"

    return f"{quantidade} faltas de páginas"