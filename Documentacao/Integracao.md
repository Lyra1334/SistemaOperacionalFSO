# BDD - Integração Geral do Sistema (Kernel do Pseudo-SO)

Este documento detalha as histórias de comportamento que governam a coordenação e a integração dos subsistemas do kernel (processos, escalonador, memória virtual, recursos de E/S e sistema de arquivos lógica em disco).

---

## 1. Inicialização, Parseamento e Validação de Entrada

### História de Usuário:
Como kernel do pseudo-SO,
Eu quero ler e processar os três arquivos de entrada simultaneamente,
Para que o sistema seja inicializado com uma configuração consistente e livre de corrupções.

#### Cenário 1: Boot bem-sucedido sob configurações válidas
* **Dado** que os arquivos `processes.txt`, `files.txt` e `string.txt` estão presentes e contêm dados sintaticamente corretos;
* **Quando** o ponto de entrada [Main.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Main.py) é acionado com os caminhos dos arquivos;
* **Então** o kernel deve carregar as estruturas de dados de processos, instanciar a fila global no [Escalonador](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py) e formatar o objeto lógico [Disco](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py);
* **E** iniciar o ciclo de clock da CPU retornando código de saída `0` ao fim da execução.

#### Cenário 2: Abortar boot por arquivos de processos e strings desbalanceados
* **Dado** que o arquivo `processes.txt` define 5 processos;
* **Mas** o arquivo `string.txt` contém apenas 4 linhas de sequências de páginas;
* **Quando** o interpretador [ProcessoParser](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Parsers/ProcessoParser.py) inicia a leitura;
* **Então** o parser deve interromper a inicialização levantando uma exceção `ErroEntrada` detalhando que a contagem de processos difere da contagem de strings;
* **E** o programa principal deve encerrar exibindo a mensagem de erro no console.

---

## 2. Interface de Logs e Comunicação com o Usuário (Despachante)

### História de Usuário:
Como despachante do pseudo-SO (Despachante),
Eu quero exibir mensagens padronizadas no terminal a cada troca de contexto ou execução de instruções,
Para que o usuário possa auditar visualmente e de forma fidedigna os passos executados.

#### Cenário 1: Impressão de dados de admissão e troca de contexto de processo
* **Dado** que o escalonador selecionou o Processo 0 para iniciar sua execução;
* **Quando** o ID do processo em execução difere do processo executado no tick anterior;
* **Então** o despachante [Despachante](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Interface/Despachante.py) deve imprimir o cabeçalho descritivo com: PID, Prioridade, Quantidade de frames ocupados e booleanos de utilização de E/S;
* **E** exibir a mensagem `P0 STARTED` indicando o início lógico da execução.

#### Cenário 2: Correção de omissão de cabeçalho de contexto após encerramento de processo
* **Dado** que o Processo 0 terminou sua execução e foi movido para a lista de finalizados;
* **Quando** o escalonador despacha o Processo 1 para rodar em seguida;
* **Então** o escalonador deve forçar a limpeza do rastreador de último processo (`self.ultimoPid = None`);
* **E** o despachante deve imprimir obrigatoriamente as informações de admissão do Processo 1 no console, evitando omitir cabeçalhos sequenciais.

---

## 3. Coordenação entre Escalonador e Memória RAM

### História de Usuário:
Como gerenciador de memória principal,
Eu quero aplicar a partição física rígida de quadros e o teto máximo de working set na admissão,
Para garantir o isolamento físico de memória e que processos operem dentro de suas cotas locais.

#### Cenário 1: Rejeição de working set excedente na admissão de usuário
* **Dado** que um processo de usuário foi lido solicitando um conjunto de trabalho (`working set`) de 15 frames;
* **Quando** o parser realiza o processamento dos dados do processo;
* **Então** o parser deve rejeitar a inicialização do processo levantando um `ErroEntrada`;
* **E** abortar a simulação com erro, sem admitir nenhum processo para execução.

#### Cenário 2: Rejeição de working set excedente na admissão de tempo real
* **Dado** que um processo de tempo real solicita um conjunto de trabalho (`working set`) de 10 frames;
* **Quando** o parser realiza o processamento dos dados do processo;
* **Então** o parser deve rejeitar a inicialização do processo levantando um `ErroEntrada`;
* **E** abortar a simulação com erro na inicialização.

---

## 4. Coordenação de E/S (Escalonador & GerenciadorRecurso)

### História de Usuário:
Como orquestrador de E/S do pseudo-SO,
Eu quero gerenciar a alocação de periféricos exclusivos e controlar processos que aguardam hardware,
Para que conflitos de recursos sejam resolvidos sem causar travamentos no kernel.

#### Cenário 1: Alocação bem-sucedida e bloqueio em caso de recurso ocupado
* **Dado** que o Processo 1 (admitido no tick 0) alocou a única impressora física livre no sistema;
* **Quando** o Processo 2 (admitido no tick 1) chega solicitando também uma impressora;
* **Então** o [GerenciadorRecurso](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorRecurso.py) deve negar a alocação para o Processo 2;
* **E** o escalonador deve mover o Processo 2 para a fila de bloqueados (`aguardando`), exibindo a mensagem descritiva no console.

#### Cenário 2: Liberação de recurso e desbloqueio do processo em espera
* **Dado** que o Processo 2 está bloqueado na fila esperando pela impressora;
* **Quando** o Processo 1 conclui seu tempo de processamento e libera o recurso;
* **Então** o kernel deve desalocar a impressora do Processo 1 e disponibilizá-la novamente;
* **E** no próximo ciclo, o Processo 2 deve alocar a impressora com sucesso e ser movido para a fila de prontos para execução.

---

## 5. Integração com o Sistema de Arquivos (Operações de Disco)

### História de Usuário:
Como gerenciador do sistema de arquivos lógico (GerenciadorSistemaArquivos),
Eu quero processar operações de criação e deleção de arquivos disparadas pelos processos ativos,
Para garantir a permanência de dados e o cumprimento das regras de permissão de disco.

#### Cenário 1: Bloqueio de escrita e deleção para processos rejeitados
* **Dado** que o Processo 3 foi rejeitado na admissão por excesso estático de recursos e foi movido para terminado;
* **Quando** a lista de operações de arquivos tenta disparar uma escrita ou deleção vinculada ao PID 3;
* **Então** o [GerenciadorSistemaArquivos](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorSistemaArquivos.py) deve interceptar a operação;
* **E** negar a ação no disco físico simulado, retornando erro explícito que indica a rejeição prévia do processo.

#### Cenário 2: Modo de compatibilidade com erros do PDF da disciplina
* **Dado** que a simulação está rodando no modo de compatibilidade de gabarito (`self.modoCompatibilidade = True`);
* **Quando** o Processo 1 tenta deletar o arquivo `"E"`, o qual foi documentado incorretamente no PDF original (onde a operação 5 deveria ser uma deleção de um arquivo inexistente que falha);
* **Então** o sistema de arquivos deve executar a regra de compatibilidade e simular a falha exata de remoção do arquivo inexistente `"E"`, mantendo a saída de texto 100% idêntica ao gabarito impresso na página 7 do PDF.

---

## 6. Encerramento e Emissão de Relatórios Finais

### História de Usuário:
Como simulador,
Eu quero emitir na saída padrão o mapa final de ocupação do disco e o balanço de page faults por processo,
Para que o resultado completo da simulação possa ser avaliado.

#### Cenário 1: Geração de relatórios pós-execução
* **Dado** que todos os processos prontos e bloqueados terminaram sua execução na CPU;
* **Quando** a fila global de execução do escalonador se esgota;
* **Então** o kernel deve solicitar ao [GerenciadorMemoria](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorMemoria.py) o total consolidado de faltas de página de cada PID;
* **E** chamar o método `mapaComoTexto` do disco para desenhar a disposição de arquivos em cada bloco;
* **E** imprimir o mapa e as estatísticas de memória na saída padrão exatamente como definidos no layout do trabalho acadêmico.
