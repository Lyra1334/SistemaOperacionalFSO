# BDD - Gerenciamento de Processos e Admissão

Especificação de comportamento sobre o ciclo de vida do processo, carga do arquivo de entrada (parser), validações lógicas e admissão em filas.

---

## 1. Parseamento e Validação Lógica de Arquivos

### História de Usuário:
Como subsistema de carga (parser),
Eu quero ler e validar as linhas do arquivo de processos e referências de páginas,
Para impedir que parâmetros inválidos ou tipos incoerentes iniciem na simulação.

#### Cenário 1: Validação de integridade de colunas e tipos
* **Dado** que o arquivo `processes.txt` contém uma linha com apenas 6 colunas ou com valores não numéricos (como `A, B, C`);
* **Quando** o parser de processos é executado;
* **Então** o parser marca aquele processo específico como pré-rejeitado (`rejeitado = True`) com a causa apropriada, evitando parar a execução do SO por completo;
* **Implementação**: [ProcessoParser.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Parsers/ProcessoParser.py)

#### Cenário 2: Validação de booleanos estritos para dispositivos
* **Dado** que o campo de impressoras de um processo está preenchido com `2` (valor inválido para dispositivo binário);
* **Quando** a função de parseamento é chamada;
* **Então** o processo é gerado em estado pré-rejeitado e o erro é exibido na fase de admissão do dispatcher sem derrubar o Kernel;
* **Implementação**: [converterBooleano em PseudoSO.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/PseudoSO.py) e [converterBooleano em Utils.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Utils.py)

---

## 2. Validação e Triagem na Admissão do Sistema (Dispatcher)

### História de Usuário:
Como dispatcher do pseudo-SO,
Eu quero avaliar os limites e parâmetros lógicos de cada processo ao atingir seu tempo de chegada,
Para garantir a integridade de segurança da memória e dos recursos do sistema.

#### Cenário 1: Rejeição por tamanho de Working Set excedente
* **Dado** que o Processo 1 (de usuário) chega no tempo de simulação $T$ com solicitação de working set de 15 frames (limite de usuário é 12);
* **Quando** o escalonador tenta admitir o processo;
* **Então** o processo é rejeitado, imprimindo a mensagem `Processo 1 rejeitado: working set maior que a área de memória permitida.`;
* **E** o processo é movido diretamente para a lista de finalizados;
* **Implementação**: [_admitirNovosProcessos em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py) e [validarProcesso em GerenciadorMemoria.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorMemoria.py)

#### Cenário 2: Rejeição por acesso fora dos limites de página (Segmentation Fault)
* **Dado** que o Processo 2 possui referências a páginas maiores que 63 ou menores que 0;
* **Quando** o processo atinge seu tempo de chegada e é processado para admissão;
* **Então** o dispatcher detecta o estouro de limites lógico e rejeita o processo com a mensagem: `Processo 2 rejeitado: acesso de memória fora dos limites (Segmentation Fault).`;
* **Implementação**: [validarProcesso em GerenciadorMemoria.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorMemoria.py)

#### Cenário 3: Rejeição por requisição estática de recursos superior ao físico do sistema
* **Dado** que o sistema possui fisicamente no máximo 2 impressoras e o Processo 3 solicita 3 impressoras;
* **Quando** o processo tenta ser admitido;
* **Então** o dispatcher o rejeita com a mensagem: `Processo 3 rejeitado: requer mais recursos do que o possúido pelo sistema.`;
* **Implementação**: [verificarProcesso em GerenciadorRecurso.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorRecurso.py)

---

## 3. Direcionamento para Filas de Execução e Bloqueios

### História de Usuário:
Como escalonador de CPU,
Eu quero enfileirar processos admitidos nas filas corretas e desviar processos que aguardam E/S temporariamente,
Para manter a CPU ativa com processos prontos e respeitar a exclusão mútua dos periféricos.

#### Cenário 1: Enfileiramento por níveis de prioridade
* **Dado** que o Processo 1 possui prioridade 0 (Tempo Real) e o Processo 2 possui prioridade 2 (Usuário);
* **Quando** ambos são admitidos com sucesso no sistema;
* **Então** o Processo 1 é inserido na `filaTempoReal` (política FIFO);
* **E** o Processo 2 é inserido na fila de realimentação correspondente `filasUsuario[2]`;
* **Implementação**: [_enfileirar em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

#### Cenário 2: Bloqueio por recursos de E/S temporariamente indisponíveis
* **Dado** que a única impressora física do sistema está em uso pelo Processo 1;
* **Quando** o Processo 2 chega e solicita o uso de 1 impressora;
* **Então** o gerenciador de recursos nega a alocação;
* **E** o Processo 2 é colocado na fila de bloqueados (`aguardando`) marcando a flag `bloqueadoPorRecurso = True`, aguardando a liberação do dispositivo no final de ciclo do Processo 1;
* **Implementação**: [_admitirNovosProcessos em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)
