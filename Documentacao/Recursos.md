# BDD - Gerenciador de Recursos de E/S

Especificação de comportamento de alocação de dispositivos físicos de E/S.

## Funcionalidade: Controle Exclusivo de Recursos

### - [x] Cenário: Bloqueio por Recurso Ocupado
* **Dado** que o processo P1 está utilizando a única impressora física do sistema
* **Quando** o processo P2 tenta alocar uma impressora
* **Então** a alocação falha e P2 é movido para a fila de bloqueados (`aguardando`)
* **Implementação**: [_admitirNovosProcessos em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py) e [alocar em GerenciadorRecurso.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorRecurso.py)

### - [x] Cenário: Rejeição de Processo por Requisito Físico Inválido
* **Dado** que o sistema físico possui apenas 1 scanner
* **Quando** um processo solicita a alocação de 2 scanners
* **Então** o processo é rejeitado na admissão pelo despachante e movido para finalizados
* **Implementação**: [verificarProcesso em GerenciadorRecurso.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorRecurso.py) e [_admitirNovosProcessos em Escalonador.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Escalonamento/Escalonador.py)

### - [x] Cenário: Proteção contra liberação de recursos alheios (Impersonation)
* **Dado** que o processo P1 alocou recursos com sucesso e o processo P2 é um agente malicioso
* **Quando** P2 emite uma chamada de liberação tentando forjar o PID de P1
* **Então** o gerenciador de recursos acusa erro `ErroGerenciadorRecurso` e preserva a alocação do P1 intacta
* **Implementação**: [liberar em GerenciadorRecurso.py](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Gerenciadores/GerenciadorRecurso.py)
