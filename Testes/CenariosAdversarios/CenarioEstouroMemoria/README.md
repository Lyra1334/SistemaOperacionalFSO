# Estouro de Memória (cenario_estouro_memoria)

Este cenário avalia a robustez do Gerenciador de Memória e do despachante do pseudo-SO diante de requisições de working set (tamanho máximo do conjunto de trabalho) que excedem os limites físicos/lógicos definidos na especificação.

## Limites da Especificação
- A memória principal tem 20 frames de 1k cada.
- **Processos de Tempo Real:** Alocação de no máximo 8 frames.
- **Processos de Usuário:** Alocação de no máximo 12 frames.

## Abusos Cometidos
- **P0 (Tempo Real):** Solicita um working set de **9** frames no arquivo `processes.txt` (limite máximo é 8).
- **P1 (Usuário):** Solicita um working set de **13** frames no arquivo `processes.txt` (limite máximo é 12).

## Comportamento Esperado
O despachante do pseudo-SO deve detectar que a requisição de memória excede o limite físico alocado para o respectivo tipo de processo e deve agir de forma segura, lançando uma exceção amigável, abortando a criação do processo correspondente ou limitando o working set dinamicamente para o teto físico, dependendo do design defensivo da implementação.
