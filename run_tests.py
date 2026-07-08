#!/usr/bin/env python3
"""
run_tests.py
Script utilitário para executar toda a suite de testes unitários do pseudo-SO.
"""

import sys
import unittest

def main() -> int:
    print("Iniciando a execução da suite de testes unitários em 'testes/'...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='testes', pattern='test_*.py')
    
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
