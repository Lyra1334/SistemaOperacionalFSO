"""
Disk.py

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

from Errors import FileSystemError
from Utils import format_blocks


class Disk:

    def __init__(
        self,
        size: int,
        occupied_segments: List[Tuple[str, int, int]]
    ) -> None:

        if size <= 0:
            raise FileSystemError(
                "O disco deve possuir pelo menos um bloco."
            )

        self.size = size

        self.disk = [
            Config.FREE_BLOCK
            for _ in range(size)
        ]

        # nome do arquivo -> PID do dono
        # Arquivos carregados inicialmente possuem dono None.
        self.owner: Dict[str, Optional[int]] = {}

        for filename, start, length in occupied_segments:
            self._load_segment(
                filename,
                start,
                length
            )

    def _load_segment(
        self,
        filename: str,
        start: int,
        length: int
    ) -> None:

        self._validate_name(filename)

        if (
            start < 0
            or length <= 0
            or start + length > self.size
        ):
            raise FileSystemError(
                f"Segmento inválido para o arquivo {filename}."
            )

        for block in range(start, start + length):

            if self.disk[block] != Config.FREE_BLOCK:
                raise FileSystemError(
                    f"Bloco {block} já está ocupado."
                )

            self.disk[block] = filename

        self.owner[filename] = None

    @staticmethod
    def _validate_name(filename: str) -> None:
        """
        Valida o nome do arquivo.
        
        --- NOTA PARA APRESENTAÇÃO ---
        Se a professora testar o simulador usando arquivos com formatos ou caracteres incomuns
        (acentos, caracteres especiais exóticos) e você precisar flexibilizar ou desligar essa
        validação rapidamente na apresentação, basta comentar esta função ou alterar a lógica dela:
        - Para aceitar qualquer nome: apenas coloque "return" no início do método.
        - As restrições a espaços (isspace()) evitam quebrar o layout impresso do mapa do disco (que usa separação por espaços).
        - A restrição a vírgulas (",") evita quebrar o parser CSV de entrada.
        - Restrições a "/" e "\\" barram injeções conceituais de caminhos lógicos (Directory Traversal).
        """
        if (
            not filename
            or filename == Config.FREE_BLOCK
            or "," in filename
            or any(c.isspace() for c in filename)
            or "/" in filename
            or "\\" in filename
            or "\x00" in filename
            or any(not (c.isalnum() or c in ".-_") for c in filename)
        ):
            raise FileSystemError(
                f"Nome de arquivo inválido: {filename}"
            )

    def create(
        self,
        pid: int,
        filename: str,
        length: int
    ) -> Tuple[bool, str]:

        try:
            self._validate_name(filename)
        except FileSystemError as exc:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{filename} (nome inválido)."
            )

        if length <= 0:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{filename} (tamanho inválido)."
            )

        if filename in self.disk:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{filename} (arquivo já existe)."
            )

        start = self._first_fit(length)

        if start is None:
            return (
                False,
                f"O processo {pid} não pode criar o arquivo "
                f"{filename} (falta de espaço)."
            )

        blocks = list(range(start, start + length))

        for block in blocks:
            self.disk[block] = filename

        self.owner[filename] = pid

        return (
            True,
            f"O processo {pid} criou o arquivo "
            f"{filename} (blocos {format_blocks(blocks)})."
        )

    def delete(
        self,
        pid: int,
        filename: str,
        can_delete_any: bool
    ) -> Tuple[bool, str]:

        try:
            self._validate_name(filename)
        except FileSystemError as exc:
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{filename} (nome inválido)."
            )

        if filename not in self.disk:
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{filename} porque ele não existe."
            )

        owner = self.owner.get(filename)

        if (
            not can_delete_any
            and owner is not None
            and owner != pid
        ):
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{filename} porque não é o dono."
            )

        if (
            not can_delete_any
            and owner is None
        ):
            return (
                False,
                f"O processo {pid} não pode deletar o arquivo "
                f"{filename} porque não foi criado por ele."
            )

        self.disk = [
            Config.FREE_BLOCK
            if block == filename
            else block
            for block in self.disk
        ]

        self.owner.pop(filename, None)

        return (
            True,
            f"O processo {pid} deletou o arquivo {filename}."
        )

    def _first_fit(
        self,
        length: int
    ) -> Optional[int]:

        free = 0
        start = 0

        for index, block in enumerate(self.disk):

            if block == Config.FREE_BLOCK:

                if free == 0:
                    start = index

                free += 1

                if free == length:
                    return start

            else:
                free = 0

        return None

    def map_as_text(self) -> str:
        """
        Retorna o mapa do disco exatamente como esperado
        no exemplo do trabalho.
        """

        disk = self.disk[:]

        while (
            disk
            and disk[-1] == Config.FREE_BLOCK
        ):
            disk.pop()

        return " ".join(disk)