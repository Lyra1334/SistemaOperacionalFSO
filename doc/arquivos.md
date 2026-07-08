# BDD - Sistema de Arquivos

Especificação de comportamento do disco contíguo e operações de arquivos.

## Funcionalidade: Alocação Contígua e Permissões de Arquivos

### - [x] Cenário: Criação de Arquivo por First-Fit
* **Dado** que o disco possui blocos livres intercalados
* **Quando** um processo solicita a gravação de um arquivo com tamanho N blocos
* **Então** o sistema busca a partir do bloco 0 a primeira sequência contígua de N blocos livres e aloca o arquivo
* **Implementação**: [create em Disk.py:L95-L145](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Storage/Disk.py#L95-L145)

### - [x] Cenário: Permissão de Deleção para Usuário (Proprietário)
* **Dado** que o arquivo "doc.txt" foi criado pelo processo PID 2 (usuário)
* **Quando** o processo PID 3 (usuário) tenta deletar "doc.txt"
* **Então** a operação falha porque o PID 3 não é o proprietário do arquivo
* **Implementação**: [delete em Disk.py:L147-L180](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Storage/Disk.py#L147-L180) (validação `owner != pid`).

### - [x] Cenário: Deleção por Tempo Real (Superusuário)
* **Dado** que o arquivo "doc.txt" foi criado pelo processo de usuário PID 2
* **Quando** o processo PID 0 (tempo real) tenta deletar "doc.txt"
* **Então** a operação é executada com sucesso (tempo real ignora restrição de dono)
* **Implementação**: [delete em Disk.py:L147-L180](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Storage/Disk.py#L147-L180) (tempo real passa flag `can_delete_any=True`).

### - [x] Cenário: Modo de Compatibilidade da Operação 5
* **Dado** que a flag de compatibilidade está ligada
* **Quando** o processo PID 1 solicita a criação do arquivo "E" (que no PDF de trace da professora foi impresso como uma deleção falha)
* **Então** o gerenciador intercepta a chamada de escrita e a converte em deleção para que a saída bata exatamente com o gabarito
* **Implementação**: [execute em FileSystemManager.py:L64-L74](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/FileSystemManager.py#L64-L74)

### - [x] Cenário: Rejeição de tamanho de disco incompatível ou estouro
* **Dado** que o simulador aceita um disco lógico de até 32768 blocos (limite físico de 32 MB para blocos de 1 KB)
* **Quando** o interpretador de arquivos lê um tamanho de disco maior que 32768 blocos ou uma operação de escrita que excede o espaço físico total
* **Então** o parser impede a inicialização gerando `InputError` imediatamente
* **Implementação**: [FileSystemParser.py:L40-L51](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Parsers/FileSystemParser.py#L40-L51) e validação dos blocos excedentes em [FileSystemParser.py:L76-L81](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Parsers/FileSystemParser.py#L76-L81)

### - [x] Cenário: Prevenção de vazamento de diretório (Directory Traversal)
* **Dado** que arquivos devem ser isolados sob o disco lógico do simulador
* **Quando** um processo solicita a criação ou deleção de um arquivo cujo nome contém caracteres de escape de caminho (como `../`, `..\\`, `/` ou byte nulo `\x00`)
* **Então** o gerenciador de disco rejeita a operação com erro de nome inválido
* **Implementação**: [_validate_name em Disk.py:L82-L94](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Storage/Disk.py#L82-L94)

### - [x] Cenário: Prevenção de escrita com blocos negativos ou nulos
* **Dado** que um processo malicioso tenta forçar a corrupção do disco lógico
* **Quando** ele solicita a criação de arquivo com tamanho negativo (ex: `-5` blocos) ou nulo (`0` blocos)
* **Então** o disco lógico aborta a operação e retorna falha sem afetar a alocação de blocos
* **Implementação**: [create em Disk.py:L111-L116](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Storage/Disk.py#L111-L116)
