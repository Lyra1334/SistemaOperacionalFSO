# Limites Máximos Suportados (cenario_limite_maximo)

Este cenário avalia o comportamento do pseudo-SO nos limites exatos suportados pela especificação do sistema, testando a estabilidade das filas de processos, estouro de contadores de CPU, e o comportamento do gerenciador de disco com um disco grande e quase 100% ocupado.

## Limites Máximos Testados
1. **Fila de Processos:** Exatamente **1000** processos criados no `processes.txt` (a especificação diz: *"As filas devem suportar no máximo 1000 processos"*).
2. **Tempo de Processador elevado:** Processo 0 (Tempo Real) solicita **10.000** ticks de CPU (testa se o SO gerencia ticks de CPU altos sem estourar tipos numéricos ou travar ciclos).
3. **Conjunto de Trabalho no Limite:** 
   - P0 solicita 8 frames (limite para TR).
   - P1 solicita 12 frames (limite para usuário).
4. **Sistema de Arquivos no Limite:**
   - Disco de exatamente **1024** blocos.
   - O disco inicia com um segmento ocupado pelo sistema (`SYS`) de **1023** blocos (do bloco 0 ao 1022), deixando exatamente **1 bloco livre** no final (bloco 1023).

## Operações de Arquivo Realizadas
- **Operação 1 (P1 cria A de tamanho 1):** Deve ser alocado com sucesso no bloco 1023 (o disco fica 100% cheio).
- **Operação 2 (P1 tenta criar B de tamanho 2):** Deve falhar por falta de espaço em disco contíguo.
- **Operação 3 (P2 tenta criar C de tamanho 1):** Deve falhar por falta de espaço (disco já está 100% cheio).
- **Operação 4 (P1 deleta A):** Deve liberar o bloco 1023.
- **Operação 5 (P2 cria C de tamanho 1):** Deve ter sucesso, ocupando o bloco 1023 agora livre.

## Comportamento Esperado
- O SO deve inicializar e gerenciar as filas contendo exatamente 1000 processos sem travamentos.
- O tempo elevado de 10.000 ticks do processo de tempo real deve ser executado até o fim (ou decrementado conforme o loop do despachante) sem erros.
- A alocação contígua no bloco 1023 deve funcionar perfeitamente de acordo com o algoritmo First-Fit.
- O mapa final de ocupação do disco deve mostrar o arquivo `SYS` ocupando de 0 a 1022, e o arquivo `C` ocupando o bloco 1023.
