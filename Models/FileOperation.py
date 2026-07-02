"""
FileOperation.py

Representa uma operação do sistema de arquivos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FileOperation:
    """
    Representa uma operação de criação ou remoção de arquivo.

    Attributes:
        pid (int): ID do processo responsável pela operação.
        op_code (int): Código da operação (0 = criar, 1 = deletar).
        filename (str): Nome do arquivo.
        size (Optional[int]): Quantidade de blocos do arquivo.
                              Utilizado apenas na operação de criação.
    """

    pid: int
    op_code: int
    filename: str
    size: Optional[int] = None