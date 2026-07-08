# Documentação Baseada em BDD (Histórias de Comportamento)

Este diretório contém a documentação funcional do pseudo-SO estruturada no formato **BDD (Dado / Quando / Então)**. O objetivo é mapear claramente os requisitos da especificação e facilitar a visualização de como as regras de negócio foram implementadas pela equipe.

### Mapeamento de Módulos e Histórias:

- [Escalonamento de CPU](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Escalonador.md): Políticas de escalonamento (FIFO de tempo real, realimentação de usuário), aging, logs de dispatcher e rejeições de processos.
- [Gerenciamento de Memória](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Memoria.md): Paginação virtual local usando LRU e isolamento de frames (tempo real vs. usuário).
- [Sistema de Arquivos](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Arquivos.md): Alocação contígua em disco por First-Fit, regras de propriedade de arquivo para deleção e o modo de compatibilidade para erros do gabarito da especificação.
- [Gerenciador de Recursos de E/S](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Recursos.md): Controle de alocação de dispositivos exclusivos (scanners, impressoras, modems, drives SATA) e gerenciamento de processos bloqueados na fila de espera.
- [Integração Geral do Kernel](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Integracao.md): Mapeamento detalhado do boot, leitura de arquivos simultâneos, ciclo de vida integrado de hardware/CPU, logs do despachante e mapa de encerramento.
- [Suíte de Testes e Robustez](file:///C:/Users/Eduardo/Documents/SistemaOperacionalFSO-V3/Documentacao/Testes.md): Histórias de comportamento que definem o ecossistema de testes unitários automatizados, validação de fuzzing adversarial e blindagem contra exploits lógicos de segurança.
