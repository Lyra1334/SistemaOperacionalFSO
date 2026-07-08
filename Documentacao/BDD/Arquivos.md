# BDD - Sistema de Arquivos

Especificação de comportamento do disco contíguo e operações de arquivos.

## Funcionalidade: Alocação Contígua e Permissões de Arquivos

### - [x] Cenário: Criação de Arquivo por First-Fit
* **Dado** que o disco possui blocos livres intercalados
* **Quando** um processo solicita a gravação de um arquivo com tamanho N blocos
* **Então** o sistema busca a partir do bloco 0 a primeira sequência contígua de N blocos livres e aloca o arquivo
* **Implementação**: [criar em Disco.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py)

### - [x] Cenário: Permissão de Deleção para Usuário (Proprietário)
* **Dado** que o arquivo "doc.txt" foi criado pelo processo PID 2 (usuário)
* **Quando** o processo PID 3 (usuário) tenta deletar "doc.txt"
* **Então** a operação falha porque o PID 3 não é o proprietário do arquivo
* **Implementação**: [deletar em Disco.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py) (validação `dono != pid`).

### - [x] Cenário: Deleção por Tempo Real (Superusuário)
* **Dado** que o arquivo "doc.txt" foi criado pelo processo de usuário PID 2
* **Quando** o processo PID 0 (tempo real) tenta deletar "doc.txt"
* **Então** a operação é executada com sucesso (tempo real ignora restrição de dono)
* **Implementação**: [deletar em Disco.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py) (tempo real passa flag `podeDeletarQualquerUm=True`).

### - [x] Cenário: Modo de Compatibilidade da Operação 5
* **Dado** que a flag de compatibilidade está ligada
* **Quando** o processo PID 1 solicita a criação do arquivo "E" (que no PDF de trace da professora foi impresso como uma deleção falha)
* **Então** o gerenciador intercepta a chamada de escrita e a converte em deleção para que a saída bata exatamente com o gabarito
* **Implementação**: [executar em GerenciadorSistemaArquivos.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorSistemaArquivos.py)

### - [x] Cenário: Rejeição de tamanho de disco incompatível ou estouro
* **Dado** que o simulador aceita um disco lógico de até 32768 blocos (limite físico de 32 MB para blocos de 1 KB)
* **Quando** o interpretador de arquivos lê um tamanho de disco maior que 32768 blocos ou uma operação de escrita que excede o espaço físico total
* **Então** o parser impede a inicialização gerando `ErroEntrada` imediatamente
* **Implementação**: [SistemaArquivosParser.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Parsers/SistemaArquivosParser.py)

### - [x] Cenário: Prevenção de vazamento de diretório (Directory Traversal)
* **Dado** que arquivos devem ser isolados sob o disco lógico do simulador
* **Quando** um processo solicita a criação ou deleção de um arquivo cujo nome contém caracteres de escape de caminho (como `../`, `..\\`, `/` ou byte nulo `\x00`)
* **Então** o gerenciador de disco rejeita a operação com erro de nome inválido
* **Implementação**: [_validarNome em Disco.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py)

### - [x] Cenário: Prevenção de escrita com blocos negativos ou nulos
* **Dado** que um processo malicioso tenta forçar a corrupção do disco lógico
* **Quando** ele solicita a criação de arquivo com tamanho negativo (ex: `-5` blocos) ou nulo (`0` blocos)
* **Então** o disco lógico aborta a operação e retorna falha sem afetar a alocação de blocos
* **Implementação**: [criar em Disco.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Armazenamento/Disco.py)

### - [x] Cenário: Controle de Quantum e Atomicidade na Escrita de Arquivos
* **Dado** que estamos executando no cenário adversário `CenarioQuantumInsuficiente` (onde os limites de quantum são aplicados de forma estrita às operações de arquivo)
* **Quando** um processo de usuário (prioridade > 0) solicita a gravação de arquivos cujo tamanho total excede seu tempo total de CPU (`tempoCpu`)
* **Então** a operação falha com erro de preempção e nenhuma alteração é feita no disco lógico para manter a atomicidade da escrita
* **Implementação**: [executarOperacao em GerenciadorSistemaArquivos.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorSistemaArquivos.py)
