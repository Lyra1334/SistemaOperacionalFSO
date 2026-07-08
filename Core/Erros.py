"""
Erros.py
Exceções personalizadas utilizadas pelo pseudo-SO.
"""

class ErroPseudoSO(Exception):
    pass

class ErroEntrada(ErroPseudoSO):
    pass

class ErroGerenciadorMemoria(ErroPseudoSO):
    pass

class ErroGerenciadorRecurso(ErroPseudoSO):
    pass

class ErroSistemaArquivos(ErroPseudoSO):
    pass

class ErroEscalonador(ErroPseudoSO):
    pass