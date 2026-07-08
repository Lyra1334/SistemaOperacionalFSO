# Conflito de PID e Permissões de Arquivos (cenario_conflito_pid)

Este cenário avalia a robustez do Gerenciador de Arquivos do pseudo-SO e seu tratamento de permissões de acesso, propriedade de arquivos e validação de PIDs fornecidos nas operações de disco.

## Regras de Negócio Testadas
- Processos de tempo real (Prioridade 0) podem criar e deletar qualquer arquivo (mesmo aqueles pré-alocados pelo sistema ou por outros processos).
- Processos de usuário (Prioridades 1, 2, 3) só podem deletar arquivos dos quais eles são donos (criados por eles próprios).
- Operações de disco só podem ser realizadas por PIDs válidos e existentes no sistema.

## Abusos Cometidos no `files.txt`
1. **Duplicação de arquivos:** `1, 0, A, 5` (P1 cria A) e depois `1, 0, A, 3` (P1 tenta recriar A). Deve gerar erro de arquivo já existente.
2. **Violação de Propriedade por Usuário:** `2, 1, A` (P2 tenta deletar o arquivo A pertencente a P1). Deve falhar porque P2 não é dono de A.
3. **Violação de Exclusão de Arquivo do Sistema:** `1, 1, Y` (P1 tenta deletar o arquivo Y pré-carregado no disco e pertencente ao sistema). Deve falhar por falta de permissão de usuário comum.
4. **Superpoderes do Processo de Tempo Real:** `0, 1, Y` (P0 - Tempo Real - tenta deletar o arquivo Y do sistema). Deve ter sucesso.
5. **PID Inexistente:** `99, 0, B, 4` e `-1, 0, C, 2` (Operações de PIDs inválidos ou inexistentes). Devem falhar explicitamente.

## Comportamento Esperado
- Operações com PIDs `99` e `-1` devem falhar com erro "O processo X não existe".
- A operação de exclusão do arquivo `A` pelo processo `2` deve falhar com erro de falta de permissão/propriedade.
- A exclusão do arquivo `Y` pelo processo `1` deve falhar por falta de permissão.
- A exclusão de `Y` pelo processo `0` (tempo real) deve ter sucesso.
- O pseudo-SO deve permanecer consistente e exibir o mapa de ocupação correto no final da execução.
