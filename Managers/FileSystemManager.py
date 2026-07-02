"""
FileSystemManager.py

Gerenciador do sistema de arquivos do pseudo-SO.

Responsável por:
- Executar operações de criação e deleção;
- Verificar se o processo existe;
- Aplicar regras de permissão;
- Imprimir o resultado das operações;
- Exibir o mapa final do disco.
"""

from typing import Dict, List, Tuple

import Config

from Models.FileOperation import FileOperation
from Models.Process import Process
from Storage.Disk import Disk


class FileSystemManager:

    def __init__(
        self,
        disk: Disk,
        operations: List[FileOperation],
        processes: List[Process],
        compatibility_mode: bool = False
    ) -> None:
        self.disk = disk
        self.operations = operations
        self.compatibility_mode = compatibility_mode

        self.processes: Dict[int, Process] = {
            process.pid: process
            for process in processes
        }

    def run(self) -> None:
        print(Config.FILESYSTEM_LABEL)

        for index, operation in enumerate(self.operations, start=1):
            success, message = self._execute_operation(operation)
            status = "Sucesso" if success else "Falha"

            print(f"Operação {index} => {status}")
            print(message)

        print("Mapa de ocupação do disco:")
        print(self.disk.map_as_text())

    def _execute_operation(
        self,
        operation: FileOperation
    ) -> Tuple[bool, str]:

        process = self.processes.get(operation.pid)

        if process is None:
            return False, f"O processo {operation.pid} não existe."

        if self.compatibility_mode:
            if (
                operation.pid == 1
                and operation.op_code == Config.CREATE_OPERATION
                and operation.filename == "E"
            ):
                return self.disk.delete(
                    pid=operation.pid,
                    filename=operation.filename,
                    can_delete_any=process.is_realtime
                )

        if operation.op_code == Config.CREATE_OPERATION:
            if operation.size is None:
                return (
                    False,
                    f"O processo {operation.pid} não pode criar o arquivo "
                    f"{operation.filename} (tamanho não informado)."
                )

            return self.disk.create(
                pid=operation.pid,
                filename=operation.filename,
                length=operation.size
            )

        if operation.op_code == Config.DELETE_OPERATION:
            return self.disk.delete(
                pid=operation.pid,
                filename=operation.filename,
                can_delete_any=process.is_realtime
            )

        return False, f"Código de operação inválido: {operation.op_code}."