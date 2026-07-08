# BDD - Gerenciador de Recursos de E/S

Especificação de comportamento de alocação de dispositivos físicos de E/S.

## Funcionalidade: Controle Exclusivo de Recursos

### - [x] Cenário: Bloqueio por Recurso Ocupado
* **Dado** que o processo P1 está utilizando a única impressora física do sistema
* **Quando** o processo P2 tenta alocar uma impressora
* **Então** a alocação falha e P2 é movido para a fila de bloqueados (`waiting`)
* **Implementação**: [Fila waiting no despachante em Scheduler.py:L98-L103](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L98-L103) e [tentativa de alocação no ResourceManager.py:L70-L98](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/ResourceManager.py#L70-L98)

### - [x] Cenário: Rejeição de Processo por Requisito Físico Inválido
* **Dado** que o sistema físico possui apenas 1 scanner
* **Quando** um processo solicita a alocação de 2 scanners
* **Então** o processo é rejeitado na admissão pelo despachante e movido para finalizados
* **Implementação**: [verify_process em ResourceManager.py:L29-L37](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/ResourceManager.py#L29-L37) e [bloqueio de admissão em Scheduler.py:L88-L94](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Scheduling/Scheduler.py#L88-L94)

### - [x] Cenário: Proteção contra liberação de recursos alheios (Impersonation)
* **Dado** que o processo P1 alocou recursos com sucesso e o processo P2 é um agente malicioso
* **Quando** P2 emite uma chamada de liberação tentando forjar o PID de P1
* **Então** o gerenciador de recursos acusa erro `ResourceManagerError` e preserva a alocação do P1 intacta
* **Implementação**: [release em ResourceManager.py:L100-L113](file:///C:/Users/Eduardo/Documents/GitHub/SistemaOperacionalFSO-V2/Managers/ResourceManager.py#L100-L113)
