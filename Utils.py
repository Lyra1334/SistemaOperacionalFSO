"""
Utils.py

Funções auxiliares usadas em várias partes do pseudo-SO.
"""

from typing import List

from Errors import InputError


def split_csv(line: str) -> List[str]:
    """
    Divide uma linha CSV simples, removendo espaços extras.
    """
    return [part.strip() for part in line.strip().split(",") if part.strip() != ""]


def parse_int(value: str, field_name: str = "valor") -> int:
    """
    Converte um valor para inteiro, lançando InputError em caso de erro.
    """
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise InputError(f"{field_name} inválido: {value!r}") from exc


def parse_01(value: str, field_name: str = "valor") -> int:
    """
    Aceita estritamente representações de booleanos equivalentes a 0 ou 1,
    garantindo que qualquer outro valor inteiro ou tipo de dado seja rejeitado.
    """
    cleaned = str(value).strip()
    try:
        val_int = int(cleaned)
        if val_int == 1:
            return 1
        if val_int == 0:
            return 0
        raise InputError(f"{field_name} deve ser estritamente 0 ou 1: {value!r}")
    except ValueError:
        text = cleaned.lower()
        truthy = {"true", "t", "yes", "y", "sim", "s"}
        falsy = {"false", "f", "no", "n", "nao", "não"}

        if text in truthy:
            return 1

        if text in falsy:
            return 0

        raise InputError(f"{field_name} deve ser bool/int equivalente a 0 ou 1: {value!r}")


def read_non_empty_lines(path: str) -> List[str]:
    """
    Lê um arquivo e retorna apenas as linhas não vazias.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError as exc:
        raise InputError(f"Arquivo não encontrado: {path}") from exc


def format_blocks(blocks: List[int]) -> str:
    """
    Formata uma lista de blocos no padrão:
    0
    0 e 1
    0, 1 e 2
    """
    if not blocks:
        return ""

    if len(blocks) == 1:
        return str(blocks[0])

    return ", ".join(str(block) for block in blocks[:-1]) + f" e {blocks[-1]}"


def format_page_faults(count: int) -> str:
    """
    Formata a quantidade de faltas de página com singular/plural.
    """
    if count == 1:
        return "1 falta de página"

    return f"{count} faltas de páginas"