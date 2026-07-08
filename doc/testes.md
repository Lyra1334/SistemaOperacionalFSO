# BDD - Suíte de Testes Automatizados (Validação & Segurança)

Este documento descreve as histórias de comportamento que guiam as asserções e testes unitários/integrados presentes no diretório `testes/` do repositório, garantindo a robustez contra erros lógicos e falhas sob estresse.

---

## 1. Execução de Suite e Integração

### História de Usuário:
Como avaliador ou desenvolvedor do sistema,
Eu quero dispor de uma ferramenta de execução automática para validar as modificações de código,
Para garantir que todas as asserções de negócio e segurança passem sem intervenções manuais.

#### Cenário 1: Suíte automatizada com unittest
* **Dado** que o repositório contém arquivos de testes prefixados com `test_`;
* **Quando** o arquivo centralizador [run_tests.py](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/run_tests.py) é executado na raiz do projeto;
* **Então** o Python deve carregar todas as classes que herdam de `unittest.TestCase`;
* **E** reportar no terminal a contagem de testes executados e a mensagem final de aprovação (`OK`).

---

## 2. Testes de Escalonamento de CPU

### História de Usuário:
Como testador do módulo de CPU,
Eu quero cobrir o comportamento de prioridades, preempção de tempo real, realimentação e aging,
Para certificar que as regras de Tanenbaum e requisitos do PDF estão perfeitamente implementadas.

#### Cenário 1: Não-preempção e FIFO para Tempo Real
* **Dado** dois processos carregados com prioridade `0` (tempo real) com tempos de CPU de 3ms e 2ms;
* **Quando** o escalonador inicia a execução;
* **Então** o processo de tempo real mais antigo deve rodar sequencialmente até seu término, sem sofrer preempção por quantum;
* **E** liberar a CPU para o processo de tempo real seguinte na fila.

#### Cenário 2: Preempção de 1ms e feedback para Usuário
* **Dado** um processo de usuário com prioridade inicial 1 e tempo de CPU de 2ms;
* **Quando** o escalonador executa um passo de CPU de 1ms (quantum do sistema);
* **Então** o processo deve ser interrompido, sofrer preempção e ter sua prioridade rebaixada para 2;
* **E** ser colocado no final da fila de prioridade 2.

#### Cenário 3: Promoção por envelhecimento (Aging)
* **Dado** que a fila de prioridade 3 acumula 3 processos de usuário;
* **Quando** o escalonador executa a rotina de envelhecimento (`self._aging()`);
* **Then** o processo mais antigo da fila de prioridade 3 deve ser promovido para a fila de prioridade superior (prioridade 2);
* **E** a contagem de processos na fila de prioridade 3 deve diminuir de forma correspondente.

---

## 3. Testes do Gerenciador de Memória e LRU Local

### História de Usuário:
Como testador de memória principal,
Eu quero validar a separação rígida de partições e o algoritmo de substituição de páginas LRU local,
Para assegurar a integridade dos limites físicos da RAM de 20 frames.

#### Cenário 1: Pré-carga sem custo de falta de página
* **Dado** um processo carregado com uma string de referências inicial;
* **Quando** o kernel executa a admissão e pré-carrega a primeira página lógica;
* **Então** o frame deve ser preenchido, mas o contador de `page_faults` do respectivo processo deve continuar em zero.

#### Cenário 2: Algoritmo LRU Local Puro
* **Dado** um processo de usuário com working set configurado em 4 frames;
* **Quando** a sequência de páginas referenciadas solicita uma página que não está carregada e todos os 4 frames locais estão preenchidos;
* **Então** o gerenciador de memória deve identificar o frame menos recentemente utilizado localmente;
* **E** substituí-lo pela nova página, incrementando corretamente o contador de page faults.

---

## 4. Testes do Gerenciador de Recursos de E/S

### História de Usuário:
Como testador do ResourceManager,
Eu quero certificar que os periféricos disponíveis são alocados de forma mutuamente exclusiva,
Para evitar que múltiplos processos capturem o mesmo hardware concorrentemente.

#### Cenário 1: Bloqueio estático por recursos de E/S
* **Dado** que o sistema possui apenas 1 scanner físico disponível;
* **Quando** o Processo 1 aloca o scanner com sucesso e o Processo 2 solicita o scanner antes de sua liberação;
* **Então** a alocação de E/S para o Processo 2 deve retornar `False` (impedindo a execução);
* **E** o Processo 2 deve ser retido na fila de bloqueados.

---

## 5. Testes do Sistema de Arquivos (Disk e First-Fit)

### História de Usuário:
Como testador do disco simulado,
Eu quero avaliar a gravação First-Fit e as regras exclusivas de deleção entre tempo real e usuário,
Para garantir a integridade dos dados e das permissões simuladas.

#### Cenário 1: Alocação Contígua de Primeiro Ajuste (First-Fit)
* **Dado** um disco lógico com lacunas vazias de blocos nos índices 0-1 e 4-6;
* **Quando** um processo solicita a criação de um arquivo de tamanho 2 blocos;
* **Então** a rotina do disco deve buscar a partir do bloco 0 a primeira sequência contígua com espaço suficiente;
* **E** alocar o arquivo nas primeiras posições (índices 0 e 1).

#### Cenário 2: Permissões de exclusão de arquivos por propriedade
* **Dado** que o Processo 1 (de usuário) criou o arquivo `"A"`;
* **Quando** o Processo 2 (também de usuário) tenta invocar a exclusão do arquivo `"A"`;
* **Então** a operação deve falhar e retornar uma mensagem explícita de rejeição por falta de propriedade;
* **E** quando um processo de tempo real (prioridade 0) tenta deletar o mesmo arquivo `"A"`, a operação deve retornar sucesso imediato.

---

## 6. Testes Adversários de Fuzzing (Robustez de Entrada)

### História de Usuário:
Como auditor do kernel contra dados corrompidos,
Eu quero testar entradas com tipos incorretos ou números excessivamente grandes,
Para assegurar que o kernel não entre em deadlock ou loops infinitos de processamento.

#### Cenário 1: Rejeição de valores booleanos inválidos em E/S
* **Dado** que um processo solicita a quantidade `3` para uso de impressora no arquivo de processos;
* **Quando** o parser interpreta o campo;
* **Então** a função de utilidades deve lançar `InputError` impedindo a conversão de valores diferentes de representações estritamente booleanas equivalentes a 0 ou 1.

#### Cenário 2: Prevenção contra estouro de inteiros por ticks excessivos
* **Dado** que a entrada de CPU time define um tempo de `10**18` ticks;
* **Quando** o parser de processos lê a linha;
* **Então** o parser deve rejeitar o processo com `InputError` indicando que o tempo limite de segurança (1.000.000) foi excedido.

#### Cenário 3: Nomes de arquivos contendo espaços e quebras de linha
* **Dado** que um processo tenta criar um arquivo com o nome `"dados relatorio.txt"`;
* **Quando** a função `_validate_name` valida a chamada;
* **Então** o disco lógico deve recusar a gravação lançando `FileSystemError` para impedir a quebra de layout na impressão final do mapa de ocupação do disco.

---

## 7. Testes de Mitigação de Exploits (Segurança e Isolamento)

### História de Usuário:
Como testador de segurança lógica do pseudo-SO,
Eu quero avaliar cenários de invasão de limites de recursos e caminhos de diretórios,
Para garantir que o sandbox em RAM do simulador é robusto.

#### Cenário 1: Prevenção de Path Traversal no disco
* **Dado** que um processo tenta deletar ou criar arquivos com caminhos como `"../etc/passwd"` ou `"C:/boot.ini"`;
* **Quando** o subsistema de arquivos processa a chamada no disco lógico;
* **Então** o validador do nome do arquivo deve interceptar caracteres de barras e contra-barras;
* **E** retornar falha na operação impedindo a manipulação lógica de arquivos fora do disco em memória.

#### Cenário 2: Isolamento de LRU e vazamento de RAM entre processos
* **Dado** que o Processo 1 e o Processo 2 estão ativos na simulação de memória virtual;
* **Quando** o Processo 1 realiza consecutivas faltas de páginas locais e substituições de frames via LRU local;
* **Então** a contagem de faltas de páginas e a ordem do LRU dos frames do Processo 2 devem permanecer intocadas e isoladas, sem sofrer qualquer interferência ou leak.

#### Cenário 3: Liberação dupla ou sequestro de recursos de E/S
* **Dado** que o Processo 1 alocou impressoras e scanners;
* **Quando** um Processo 2 (que não alocou recursos) tenta invocar a liberação de recursos do sistema;
* **Então** o [ResourceManager](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/ResourceManager.py) deve acusar que o PID 2 não possui alocações ativas no dicionário interno;
* **E** levantar uma exceção `ResourceManagerError`, protegendo as cotas de hardware contra invasões lógicas.
