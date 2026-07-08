# BDD - Gerenciamento de Memória

Especificação de comportamento da paginação virtual e LRU local.

## Funcionalidade: Paginação com LRU Local

### - [x] Cenário: Pré-carregamento na admissão
* **Dado** que um processo acaba de ser admitido na fila de prontos
* **Quando** ele solicita sua primeira página (referência inicial)
* **Então** ela é carregada na partição sem gerar falta de página (preload de inicialização)
* **Implementação**: [preload em MemoryManager.py:L35-L45](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/MemoryManager.py#L35-L45)

### - [x] Cenário: Substituição de Página por LRU Local
* **Dado** que o processo P0 tem limite de working set de 4 frames, todos ocupados
* **Quando** P0 solicita uma página que não está em seus frames carregados
* **Então** ocorre uma falta de página e o frame menos utilizado recentemente (LRU) de P0 é substituído
* **Implementação**: [access_page em MemoryManager.py:L72-L103](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/MemoryManager.py#L72-L103)

### - [x] Cenário: Isolamento de Partições de RAM
* **Dado** que a memória física simulada tem 20 frames no total
* **Quando** o sistema é inicializado
* **Então** processos de tempo real ficam limitados a 8 frames dedicados e processos de usuário a 12 frames dedicados
* **Implementação**: [validate_process em MemoryManager.py:L26-L33](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/MemoryManager.py#L26-L33)

### - [x] Cenário: Rejeição de página fora do espaço de endereçamento virtual
* **Dado** que o sistema simula um espaço de endereçamento de 16 bits clássico (64 KB) com páginas de 1 KB (conforme especificação do PDF)
* **Quando** o parser lê uma página fora do intervalo de 0 a 63 (64 páginas virtuais no total)
* **Então** o sistema acusa erro de segmentação levantando `InputError` imediatamente
* **Implementação**: [Validação de limites em ProcessParser.py:L74-L80](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Parsers/ProcessParser.py#L74-L80)
