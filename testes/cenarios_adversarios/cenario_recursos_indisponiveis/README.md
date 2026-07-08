# Recursos Indisponíveis (cenario_recursos_indisponiveis)

Este cenário testa o comportamento do Gerenciador de Recursos (E/S) do pseudo-SO diante de requisições inválidas de dispositivos físicos, seja por ultrapassar a quantidade de hardware existente ou por desrespeitar as restrições de classe de processos.

## Recursos Físicos Existentes
- **Scanner:** 1
- **Impressora:** 2
- **Modem:** 1
- **SATA (Disco):** 2

## Abusos Cometidos
1. **P0 (Tempo Real, Prioridade 0):** Requisita 1 Scanner.
   - *Violação:* Processos de tempo real não podem requerer nem possuir recursos de E/S.
2. **P1 (Usuário, Prioridade 1):** Requisita 3 Impressoras (Sendo que só existem 2).
3. **P2 (Usuário, Prioridade 2):** Requisita 2 Scanners (Sendo que só existe 1).
4. **P3 (Usuário, Prioridade 2):** Requisita 2 Modems (Sendo que só existe 1).
5. **P4 (Usuário, Prioridade 3):** Requisita 3 Dispositivos SATA (Sendo que só existem 2).

## Comportamento Esperado
O Gerenciador de E/S deve tratar essas requisições como inválidas/impossíveis:
- P0 deve falhar ou ser abortado porque processos de tempo real não têm suporte a recursos de E/S.
- P1, P2, P3 e P4 devem ser impedidos de rodar ou suas solicitações de alocação de E/S devem ser negadas na origem, pois demandam mais dispositivos físicos do que a máquina real possui. O sistema deve abortar a execução com um diagnóstico claro, em vez de travar o SO.
