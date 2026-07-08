# Cenário Ótimo (cenario_otimo)

Este cenário valida o comportamento do pseudo-SO em um caso ideal e bem-comportado, onde todos os recursos físicos e limites de memória estão dentro das especificações e não há erros de execução. Ele serve como teste de fumaça (smoke test) para atestar a funcionalidade básica correta.

## Componentes Testados
- **Escalonamento:** Mistura de processo de tempo real (PID 0) e processos de usuário com prioridades variadas (PID 1, 2, 3).
- **Gerenciador de E/S:** Processos de usuário (P1, P2, P3) solicitam recursos disponíveis sem exceder a capacidade física (1 scanner, 2 impressoras, 1 modem, 2 SATAs). 
- **Gerenciador de Memória:** O tamanho do working set solicitado para todos os processos é de 4 frames (válido e <= 8 para tempo real e <= 12 para processos de usuário). As strings de referência contêm páginas de 0 a 6 válidas.
- **Gerenciador de Arquivos:** 
  - O disco inicia com 20 blocos e 2 arquivos ocupados (X e Y).
  - P0 (tempo real) deleta com sucesso o arquivo X.
  - P1 cria o arquivo A (4 blocos) e posteriormente o deleta.
  - P2 cria o arquivo B (3 blocos).
  - P3 cria o arquivo C (5 blocos).
  - Todas as operações devem ser concluídas com sucesso.
