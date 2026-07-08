# BDD - Escalonamento de CPU

Especificação de comportamento do Escalonador de CPU.

## Funcionalidade: Alternância de Processos e Prioridades

### - [x] Cenário: Processo de Tempo Real corta fila (Preempção imediata)
* **Dado** que a fila de prontos tem processos de usuário (prioridade 1, 2 ou 3) rodando
* **Quando** um processo de tempo real (prioridade 0) chega ao sistema
* **Então** o processo de usuário é interrompido de imediato e o de tempo real assume a CPU
* **Implementação**: [_executar em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

### - [x] Cenário: Time-sharing de Processos de Usuário (Preempção por Time-slice)
* **Dado** que há processos de usuário na fila de prontos
* **Quando** o processo ativo consome 1ms de CPU
* **Então** ele sofre preempção, tem sua prioridade rebaixada (feedback) e vai para o final da fila de prioridade inferior
* **Implementação**: [_executar em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

### - [x] Cenário: Promoção de processos antigos (Aging)
* **Dado** que um processo de usuário está parado na fila de prioridade inferior há muito tempo
* **Quando** o escalonador executa o ciclo de envelhecimento (aging)
* **Então** a prioridade do processo é promovida em 1 nível para evitar starvation
* **Implementação**: [_envelhecimento em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

### - [x] Cenário: Impressão correta de contexto no dispatcher
* **Dado** que um processo P0 finaliza sua execução
* **Quando** o próximo processo P1 assume a CPU
* **Então** o cabeçalho do despachante `dispatcher =>` deve ser impresso obrigatoriamente (evitando omitir logs)
* **Implementação**: [_executar em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

### - [x] Cenário: Rejeição Estrita de Working Set Excedente no Boot
* **Dado** que um processo solicita no arquivo de entrada um working set maior que a partição física disponível (12 frames para usuário, 8 para tempo real)
* **Quando** o parser de processos realiza a carga do arquivo de entrada
* **Então** o simulador aborta imediatamente e levanta um `ErroEntrada`
* **E** a simulação não é executada, retornando exit code 1
* **Implementação**: [ProcessoParser.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Parsers/ProcessoParser.py)

### - [x] Cenário: Rejeição de Processo por Estouro de Memória em Instanciação Direta
* **Dado** que um processo é instanciado manualmente fora do parser com working set maior que a partição física
* **Quando** o escalonador tenta admiti-lo na fila de execução
* **Então** o processo é rejeitado com um log de erro do despachante e movido direto para finalizados sem rodar
* **Implementação**: [_admitirNovosProcessos em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py) e [validarProcesso em GerenciadorMemoria.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorMemoria.py)
