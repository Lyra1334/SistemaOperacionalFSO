"""
Errors.py
Exceções personalizadas utilizadas pelo pseudo-SO.
"""

class PseudoSOError(Exception):
    pass

class InputError(PseudoSOError):
    pass

class MemoryManagerError(PseudoSOError):
    pass

class ResourceManagerError(PseudoSOError):
    pass

class FileSystemError(PseudoSOError):
    pass

class SchedulerError(PseudoSOError):
    pass