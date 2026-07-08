# Simulador de Pseudo-Sistema Operacional (PseudoSO) - Grupo 09

Este repositório contém um simulador completo de um Pseudo-Sistema Operacional (PseudoSO) em Python, projetado para demonstrar os conceitos fundamentais de gerência de CPU, memória virtual, recursos de E/S e sistema de arquivos lógico em disco.

## Equipe de Desenvolvimento

- Celio Junio de Freitas Eduardo - 211010350
- Marina Silva Lyra - 222001313
- Ramon Oliveira de Azevedo - 242039630

---

## Funcionamento Detalhado dos Módulos do Kernel

O kernel é dividido em subcomponentes autônomos que cooperam de forma integrada. Abaixo está a descrição detalhada do funcionamento e as decisões de design de cada módulo:

---

### 1. Boot, Carga e Inicialização Segura (Main, Parsers, Config, Utils, Erros)

1. **Ponto de Entrada e Orquestração (Main.py)**:
  - Quando o simulador é inicializado, o módulo principal Main.py lê os caminhos dos arquivos da linha de comando, instancia as tabelas físicas do sistema (disco, gerenciador de recursos e memória) e passa o controle para o escalonador. Se houver falhas críticas nos arquivos de entrada (arquivos ausentes ou layouts corrompidos), o boot é abortado de forma controlada.
2. **Carga e Filtragem de Entrada (ProcessoParser.py & SistemaArquivosParser.py)**:
  - O parser lê concorrentemente os arquivos processes.txt (parâmetros de processos) e string.txt (referências de páginas de memória).
  - **Tratamento de Processos Inválidos**: Se um processo possuir parâmetros inválidos (como working set inválido, páginas fora do limite de 63, prioridade incorreta ou tempos de CPU negativos/excessivos), o parser não interrompe o boot do Kernel. Ele instancia o objeto do processo normalmente, mas com a flag rejeitado = True e grava o motivo específico no campo motivoRejeicao. Isso impede que o simulador inteiro sofra crash antes mesmo de iniciar a execução devido a um único processo mal formatado.
3. **Parametrização Física (Config.py)**:
  - Centraliza todas as constantes físicas do hardware simulado (limite de 8 frames de memória de tempo real, 12 de usuário, quantitativos de E/S físicos da placa-mãe, e o quantum básico de CPU).
4. **Conversão Segura e Exceções (Utils.py & Erros.py)**:
  - Utilitários auxiliam na conversão de tipos de dados de strings brutas para inteiros ou booleanos. Erros sintáticos no parser geral de arquivos disparam ErroEntrada, isolando problemas físicos nos arquivos de entrada de problemas semânticos de parâmetros dos processos.

Essa separação rígida entre falhas críticas do sistema (que impedem o boot) e falhas lógicas nos arquivos de parâmetros de processos impede que o simulador sofra quedas por erros em linhas individuais. O sistema inicializa de forma estável e rejeita processos maliciosos sob demanda.

---

### 2. Gerenciamento e Admissão de Processos (Modelo de Processo, Admissão/Validação)

1. **Retenção Inicial (Fora das Filas)**:
  - Quando o SO inicia, os processos não são enviados diretamente para as filas de execução (prontos ou bloqueados). Eles são carregados em uma lista de espera global (self.processos), ordenados estritamente pelo seu tempo de chegada (tempoChegada).
2. **O "Daemon" de Validação (Fase de Admissão)**:
  - A cada tick de clock, a rotina _admitirNovosProcessos do escalonador age como um daemon interceptador. Um processo só sai da lista global de espera e avança para a tentativa de alocação de recursos se ele passar sequencialmente por três portões de validação estritos:
    - **Portão 1: Validação de Parâmetros (Parser)**: Avalia se o processo foi previamente marcado como inválido no parser por parâmetros corrompidos. Se sim, ele é descartado imediatamente.
    - **Portão 2: Validação de Memória (RAM)**: O GerenciadorMemoria valida se o workingSet do processo cabe na partição reservada física (12 frames para usuário, 8 para tempo real) e se a sua string de referências não possui páginas fora do limite de endereçamento virtual de 63 frames. Se falhar, é rejeitado por Segmentation Fault ou Working Set Excedente.
    - **Portão 3: Validação de Dispositivos (E/S)**: O GerenciadorRecurso analisa se a solicitação estática de periféricos do processo não excede o limite físico total da máquina (ex: pedir 3 impressoras onde só existem 2 físicas). Se exceder, é rejeitado por Recursos Insuficientes.
3. **Alocação Prévia Garantida**:
  - Apenas os processos que passaram ilesos por todos os portões de validação prosseguem para a tentativa de alocação física de hardware.
    - Se os recursos solicitados estiverem ocupados por outro processo ativo, ele é enviado para a fila de Bloqueados (aguardando).
    - Se os recursos forem alocados com sucesso, ele é enviado para a respectiva fila de Prontos (Real-Time ou Feedback).

Esse fluxo garante que nenhum processo inválido ou com parâmetros impossíveis chegue a entrar nas filas de execução do escalonador. O validador de admissão limpa a carga de trabalho de modo que os processos nas filas de prontos tenham execução e isolamento de recursos garantidos.

---

### 3. Escalonamento de CPU (Fila de Tempo Real, Feedback de Usuário e Aging)

1. **Prioridade Absoluta e FIFO para Tempo Real (Prioridade 0)**:
  - Processos de tempo real são inseridos na filaTempoReal. Eles possuem prioridade estrita de execução: a CPU nunca executa um processo de usuário se houver algum processo de tempo real na fila de prontos. O escalonamento é FIFO clássico (não preemptivo por quantum), rodando o processo até o esgotamento do seu tempo de CPU.
2. **Realimentação Multinível (Feedback) e Time-sharing para Usuários (Prioridades 1, 2 e 3)**:
  - Processos de usuário rodam com quantum fixo de 1ms (USER_QUANTUM). Ao término do tick, se o processo não concluiu, ele sofre preempção por quantum. Sua prioridade dinâmica é reduzida (rebaixamento de fila) e ele é enviado ao final da fila de prioridade inferior (feedback), garantindo compartilhamento justo do processador.
3. **Promoção de Processos Antigos (Aging)**:
  - Para evitar starvation (onde processos nas filas inferiores de prioridade 2 e 3 nunca rodam devido à constante chegada de novos processos de prioridade superior), o escalonador executa a rotina _envelhecimento() a cada ciclo. Processos que esperam há muito tempo sem CPU têm sua prioridade temporariamente promovida em 1 nível.

Com essa estratégia, o escalonador concilia tempo de resposta imediato para tarefas críticas de tempo real com distribuição justa do processador para processos de usuário, evitando starvation através do envelhecimento periódico.

---

### 4. Gerenciamento de Memória Virtual (LRU Local e Particionamento Rígido)

1. **Isolamento Rígido de Memória RAM**:
  - A memória física de 20 frames é estaticamente particionada: a partição de Tempo Real detém 8 frames e a partição de Usuário detém 12 frames. Processos de uma partição nunca podem alocar quadros lógicos da partição oposta.
2. **Conjunto de Trabalho (Working Set) e Pré-carga**:
  - Cada processo executa com um limite rígido de quadros lógicos na RAM definido pelo seu conjunto de trabalho (workingSet). Na admissão do processo, a primeira página lógica da string de referências é pré-carregada na RAM, gerando a primeira falta de página do processo.
3. **Algoritmo de Substituição LRU Local**:
  - Quando ocorre uma falta de página (Page Fault) e o processo já atingiu seu teto de working set físico, o GerenciadorMemoria busca e substitui a página menos recentemente utilizada (LRU) dentro dos quadros pertencentes exclusivamente àquele processo.

A paginação puramente local com partições estáticas de RAM evita interferências mútuas de paginação (thrashing). Um processo com acessos excessivos consome apenas sua cota local de frames, sem prejudicar o desempenho de outros processos.

---

### 5. Gerenciamento de Recursos de E/S (Exclusão Mútua e Bloqueios)

1. **Tabelas Físicas de Controle de Hardware**:
  - O GerenciadorRecurso gerencia o inventário de dispositivos disponíveis: 2 impressoras, 1 scanner, 1 modem e 2 drives SATA.
2. **Alocação Exclusiva (Exclusão Mútua)**:
  - Na admissão, se o processo requer periféricos, o gerenciador verifica a disponibilidade física. Se livres, decrementa os contadores e associa o hardware ao PID do processo. Processos de tempo real (Prioridade 0) são proibidos pelo design de solicitar recursos de E/S.
3. **Fila de Bloqueados e Liberação no Término**:
  - Se algum periférico solicitado estiver ocupado, a alocação falha e o processo entra na fila de bloqueados (aguardando) marcando a flag bloqueadoPorRecurso = True. No encerramento do processo que detém o periférico, os recursos são liberados e os processos bloqueados são acordados na ordem de fila.

A alocação estática exclusiva na admissão previne deadlocks de hardware durante a execução. O desvio dos processos bloqueados para fora da fila de prontos maximiza a utilização do processador, impedindo que a CPU gaste ciclos esperando pela liberação de periféricos.

---

### 6. Sistema de Arquivos Lógico em Disco (First-Fit, Propriedade e Quantum Rígido)

1. **Gravação Contígua por Primeiro Ajuste (First-Fit)**:
  - Arquivos são gravados em blocos contíguos no disco simulado. Ao solicitar a gravação, a rotina busca do bloco 0 em diante pela primeira sequência contígua de blocos vazios com tamanho suficiente.
2. **Verificação de Propriedade de Deleção (Owner Check)**:
  - Cada arquivo em disco registra o PID do processo proprietário. A exclusão de um arquivo só é concedida se o PID solicitante for o proprietário original. Processos de tempo real (Prioridade 0) agem como administradores de sistema (superusuários) e ignoram essa validação, podendo deletar qualquer arquivo do disco.
3. **Atomicidade Total Sob Quantum de CPU Insuficiente**:
  - Se a soma dos tamanhos das criações de arquivos solicitadas por um processo de usuário exceder o seu tempo de execução de CPU total (tempoCpu), a operação de gravação falha por completo por esgotamento prematuro do tempo de vida útil do processo.
  - **Garantia de Não-Corrupção**: Para assegurar a atomicidade da operação de E/S, a gravação é abortada antes de iniciar e nenhum bloco do disco lógico é modificado, impedindo arquivos inconsistentes ou corrompidos de permanecerem gravados devido à preempção do processo.

O sistema de arquivos concilia alocação contígua com segurança. A verificação de propriedade impede exclusões indevidas de dados alheios, enquanto a validação de quantum/vida de CPU impede que arquivos fiquem inconsistentes se o processo sofrer preempção no meio da gravação.

---

## Executando o Simulador do PseudoSO

Para rodar a simulação principal do pseudo-sistema operacional, use o script `Main.py` passando os caminhos dos três arquivos de entrada de sua escolha:

```bash
python Main.py <caminho_processes.txt> <caminho_files.txt> <caminho_string.txt>
```

### Exemplo de Comando com Cenário Padrão:

```bash
python Main.py Testes/CenariosAdversarios/CenarioOtimo/processes.txt Testes/CenariosAdversarios/CenarioOtimo/files.txt Testes/CenariosAdversarios/CenarioOtimo/string.txt
```

### Dica para Edições e Testes Consecutivos Rápidos:

Se você estiver realizando modificações sucessivas para testar novos comportamentos, **não é necessário criar novos arquivos ou mudar os argumentos de comando de execução**.
Basta abrir e alterar diretamente o conteúdo dos arquivos de entrada que já estão configurados no cenário de teste que você está executando (por exemplo, editando os arquivos na pasta `Testes/CenariosAdcionais/` ou `Testes/CenariosAdversarios/CenarioOtimo/`). Copie e cole os novos dados diretamente sobre os arquivos existentes e execute novamente o simulador apontando para o mesmo caminho. Neste caso, basta executar o comando desse jeito que já funcionará.

```bash
python Main.py
```

---

## Suíte de Testes Automatizada

O projeto conta com uma suíte de testes de unidade e integração automatizada.

### 1. Executar a Suíte de Testes Unitários

Para validar todas as regras lógicas de admissão, paginação LRU, escalonamento, exploits de segurança e fuzzing de entrada:

```bash
python ExecutarTestes.py
```

O console exibirá o progresso detalhado de cada teste e terminará com:

```text
Todos os testes passaram com sucesso!
```

### 2. Gerar Logs dos Cenários Adversários

Para rodar todos os cenários lógicos (como ótimos, estouro de memória, acesso proibido a RAM, conflito de PID e quantum insuficiente) e atualizar os arquivos de saída `.log` correspondentes:

```bash
python Testes/ExecutarCenariosAdversarios.py
```

Os arquivos de relatórios serão gerados nas pastas dos respectivos cenários (ex: `Testes/CenariosAdversarios/CenarioQuantumInsuficiente/saida_simulada.log`).

---

## Parametrização e Modificação do Hardware

Caso queira alterar propriedades físicas do PseudoSO (como quantidade de RAM, quantidade de periféricos físicos ou tamanho do quantum), altere as constantes declaradas no arquivo de configuração global **[Config.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Config.py)**:

- `QUADROS_MEMORIA_TEMPO_REAL = 8` (Cota física de frames para tempo real)
- `QUADROS_MEMORIA_USUARIO = 12` (Cota física de frames para usuário)
- `QTD_IMPRESSORA = 2` (Quantidade de impressoras instaladas)
- `USER_QUANTUM = 1` (Tempo de fatia de processador concedido a processos de usuário)

---

## Histórias de Comportamento (BDD)

O sistema foi modelado seguindo diretrizes de Arquitetura de Software no modelo **Ágil**, respectivamente utilizando TDD e BDD. Em relação ao segundo, todas as histórias necessárias foram agrupadas em `Documentacao/BDD`.

- **[Documentação Funcional em BDD](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/BDD/)**
