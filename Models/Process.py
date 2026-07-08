from dataclasses import dataclass, field
from typing import Dict, List

import Config


@dataclass
class Process:
    pid: int
    arrival_time: int
    priority: int
    cpu_time: int
    working_set: int
    printer: int
    scanner: int
    modem: int
    sata: int
    references: List[int] = field(default_factory=list)

    remaining_time: int = field(init=False)
    original_priority: int = field(init=False)

    page_faults: int = 0
    frames: List[int] = field(default_factory=list)
    last_used: Dict[int, int] = field(default_factory=dict)

    memory_simulated: bool = False
    is_rejected: bool = False

    def __post_init__(self) -> None:
        self.remaining_time = self.cpu_time
        self.original_priority = self.priority

    @property
    def is_realtime(self) -> bool:
        return self.priority == Config.REALTIME_PRIORITY