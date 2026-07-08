"""
OperacaoArquivo.py

Representa uma operação do sistema de arquivos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OperacaoArquivo:
    """
    Representa uma operação de criação ou remoção de arquivo.

    Attributes:
        pid (int): ID do processo responsável pela operação.
        codigoOperacao (int): Código da operação (0 = criar, 1 = deletar).
        nomeArquivo (str): Nome do arquivo.
        tamanho (Optional[int]): Quantidade de blocos do arquivo.
                              Utilizado apenas na operação de criação.
    """

    pid: int
    codigoOperacao: int
    nomeArquivo: str
    tamanho: Optional[int] = None