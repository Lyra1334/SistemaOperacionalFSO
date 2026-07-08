# BDD - Escalonamento de CPU

Especificação de comportamento do Escalonador de CPU.

## Funcionalidade: Alternância de Processos e Prioridades

### - [x] Cenário: Processo de Tempo Real corta fila (Preempção imediata)
* **Dado** que a fila de prontos tem processos de usuário (prioridade 1, 2 ou 3) rodando
* **Quando** um processo de tempo real (prioridade 0) chega ao sistema
* **Então** o processo de usuário é interrompido de imediato e o de tempo real assume a CPU
* **Implementação**: [Verificação de tempo real e quantum total em Scheduler.py:L151-L152](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L151-L152)

### - [x] Cenário: Time-sharing de Processos de Usuário (Preempção por Time-slice)
* **Dado** que há processos de usuário na fila de prontos
* **Quando** o processo ativo consome 1ms de CPU
* **Então** ele sofre preempção, tem sua prioridade rebaixada (feedback) e vai para o final da fila de prioridade inferior
* **Implementação**: [Fatiamento de tempo de usuário em Scheduler.py:L154](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L154) e [feedback de prioridade em Scheduler.py:L174-L180](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L174-L180)

### - [x] Cenário: Promoção de processos antigos (Aging)
* **Dado** que um processo de usuário está parado na fila de prioridade inferior há muito tempo
* **Quando** o escalonador executa o ciclo de aging
* **Então** a prioridade do processo é promovida em 1 nível para evitar starvation
* **Implementação**: [Ciclo _aging em Scheduler.py:L184-L194](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L184-L194)

### - [x] Cenário: Impressão correta de contexto no dispatcher
* **Dado** que um processo P0 finaliza sua execução
* **Quando** o próximo processo P1 assume a CPU
* **Então** o cabeçalho do despachante `dispatcher =>` deve ser impresso obrigatoriamente (evitando omitir logs)
* **Implementação**: [Despacho em Scheduler.py:L143-L148](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L143-L148) e [reset do last_pid em Scheduler.py:L171](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L171)

### - [x] Cenário: Rejeição de Processo por Estouro de Memória
* **Dado** que o processo P0 solicita um working set maior que a partição de memória disponível (12 frames para usuário, 8 para tempo real)
* **Quando** o escalonador tenta admitir o processo
* **Então** o processo é rejeitado com um log de erro do despachante e movido direto para finalizados
* **Implementação**: [Validação de tamanho em Scheduler.py:L80-L86](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L80-L86) e [MemoryManager.py:L26-L33](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/MemoryManager.py#L26-L33)
