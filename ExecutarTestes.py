#!/usr/bin/env python3
"""
ExecutarTestes.py
Script utilitário para executar toda a suite de testes unitários do pseudo-SO.
"""

import sys
import unittest

def main() -> int:
    print("Iniciando a execução da suite de testes unitários em 'Testes/'...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='Testes', pattern='Teste*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nTodos os testes passaram com sucesso!")
        return 0
    else:
        print("\nHouve falhas em alguns testes.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
