"""
FileSystemParser.py

Responsável por ler e validar o arquivo Files.txt,
criando o disco e a lista de operações do sistema de arquivos.
"""

from typing import List, Tuple

import Config

from Errors import InputError
from Models.FileOperation import FileOperation
from Storage.Disk import Disk
from Utils import (
    parse_int,
    read_non_empty_lines,
    split_csv,
)


class FileSystemParser:

    @staticmethod
    def load(path: str) -> Tuple[Disk, List[FileOperation]]:
        """
        Lê o arquivo do sistema de arquivos e retorna:

        - Objeto Disk
        - Lista de operações (FileOperation)
        """

        lines = read_non_empty_lines(path)

        if len(lines) < 2:
            raise InputError(
                "Arquivo do sistema de arquivos deve possuir pelo menos duas linhas."
            )

        disk_size = parse_int(lines[0], "Quantidade de blocos do disco")
        
        # Restrição física do tamanho do disco simulado (máximo de 32 MB / 32768 blocos de 1 KB).
        # Este limite pode ser alterado se houver necessidade de simular capacidades maiores.
        if disk_size <= 0 or disk_size > 32768:
            raise InputError(
                "Quantidade de blocos do disco deve ser entre 1 e 32768."
            )

        occupied_count = parse_int(
            lines[1],
            "Quantidade de segmentos ocupados"
        )

        if occupied_count < 0:
            raise InputError(
                "Quantidade de segmentos ocupados não pode ser negativa."
            )

        if len(lines) < occupied_count + 2:
            raise InputError(
                "Arquivo terminou antes da definição dos segmentos ocupados."
            )

        occupied_segments = []

        for line_number in range(2, occupied_count + 2):

            parts = split_csv(lines[line_number])

            if len(parts) != 3:
                raise InputError(
                    f"Segmento inválido na linha {line_number + 1}."
                )

            filename = parts[0]
            first_block = parse_int(parts[1], "Primeiro bloco")
            block_count = parse_int(parts[2], "Quantidade de blocos")

            if first_block < 0 or first_block >= disk_size:
                raise InputError(f"Bloco inicial {first_block} fora dos limites do disco (0-{disk_size-1}).")
            if block_count <= 0:
                raise InputError("Quantidade de blocos do segmento deve ser maior que zero.")
            if first_block + block_count > disk_size:
                raise InputError(f"Segmento do arquivo {filename} excede o tamanho do disco.")

            occupied_segments.append(
                (
                    filename,
                    first_block,
                    block_count
                )
            )

        operations = []

        for line_number in range(occupied_count + 2, len(lines)):

            parts = split_csv(lines[line_number])

            if len(parts) not in (3, 4):
                raise InputError(
                    f"Operação inválida na linha {line_number + 1}."
                )

            pid = parse_int(parts[0], "ID do processo")
            operation = parse_int(parts[1], "Código da operação")
            filename = parts[2]

            if operation == Config.CREATE_OPERATION:

                if len(parts) != 4:
                    raise InputError(
                        f"Operação CREATE sem tamanho na linha {line_number + 1}."
                    )

                blocks = parse_int(
                    parts[3],
                    "Quantidade de blocos"
                )

                if blocks <= 0:
                    raise InputError("Quantidade de blocos para criação deve ser maior que zero.")
                if blocks > disk_size:
                    raise InputError(f"Tentativa de criar arquivo '{filename}' com tamanho maior que a capacidade total do disco.")

                operations.append(
                    FileOperation(
                        pid=pid,
                        op_code=operation,
                        filename=filename,
                        size=blocks
                    )
                )

            elif operation == Config.DELETE_OPERATION:

                operations.append(
                    FileOperation(
                        pid=pid,
                        op_code=operation,
                        filename=filename
                    )
                )

            else:
                raise InputError(
                    f"Código de operação inválido ({operation}) na linha {line_number + 1}."
                )

        disk = Disk(
            size=disk_size,
            occupied_segments=occupied_segments
        )

        return disk, operations