"""
ResourceManager.py

Gerenciador de recursos de Entrada/Saída.

Responsável por:
- Verificar disponibilidade dos recursos;
- Alocar recursos;
- Liberar recursos;
- Informar o estado atual dos dispositivos.
"""

from typing import Dict

import Config

from Models.Process import Process


class ResourceManager:

    def __init__(self) -> None:

        self.available: Dict[str, int] = {
            "scanner": Config.TOTAL_SCANNERS,
            "printer": Config.TOTAL_PRINTERS,
            "modem": Config.TOTAL_MODEMS,
            "sata": Config.TOTAL_SATA_DRIVES,
        }
    
    def verify_process(self, process:Process):
        if (process.scanner > Config.TOTAL_SCANNERS or
            process.printer > Config.TOTAL_PRINTERS or
            process.modem > Config.TOTAL_MODEMS or
            process.sata > Config.TOTAL_SATA_DRIVES):
            return False
        else:
            return True


    def required(self, process: Process) -> Dict[str, int]:
        """
        Retorna os recursos necessários para um processo.

        Processos de tempo real não utilizam recursos de E/S.
        """

        if process.is_realtime:
            return {
                "scanner": 0,
                "printer": 0,
                "modem": 0,
                "sata": 0,
            }

        return {
            "scanner": process.scanner,
            "printer": process.printer,
            "modem": process.modem,
            "sata": process.sata,
        }

    def can_allocate(self, process: Process) -> bool:
        """
        Verifica se todos os recursos necessários estão disponíveis.
        """

        required = self.required(process)

        return all(
            self.available[resource] >= quantity
            for resource, quantity in required.items()
        )

    def allocate(self, process: Process) -> bool:
        """
        Tenta alocar os recursos do processo.

        Retorna:
            True  -> recursos alocados.
            False -> recursos indisponíveis.
        """

        if not self.can_allocate(process):
            return False

        required = self.required(process)

        for resource, quantity in required.items():
            self.available[resource] -= quantity

        return True

    def release(self, process: Process) -> None:
        """
        Libera todos os recursos utilizados pelo processo.
        """

        required = self.required(process)

        for resource, quantity in required.items():
            self.available[resource] += quantity

    def reset(self) -> None:
        """
        Restaura o estado inicial dos recursos.
        """

        self.available = {
            "scanner": Config.TOTAL_SCANNERS,
            "printer": Config.TOTAL_PRINTERS,
            "modem": Config.TOTAL_MODEMS,
            "sata": Config.TOTAL_SATA_DRIVES,
        }

    def get_available_resources(self) -> Dict[str, int]:
        """
        Retorna uma cópia da quantidade de recursos disponíveis.
        """

        return self.available.copy()