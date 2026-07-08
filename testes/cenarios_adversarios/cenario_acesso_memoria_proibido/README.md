# Acesso de Memória Proibido (cenario_acesso_memoria_proibido)

Este cenário avalia o comportamento do Gerenciador de Memória do pseudo-SO ao lidar com acessos a páginas virtuais absurdas ou que estejam fora dos limites do espaço de endereçamento virtual de 16 bits suportado.

## Fundamentação Teórica
- Um endereçamento de 16 bits permite no máximo $2^{16} = 65.536$ bytes de memória virtual (64 KB).
- Como o tamanho de cada página é de 1 KB (1024 bytes), o espaço de endereçamento virtual é composto por exatamente 64 páginas virtuais (numeradas de 0 a 63).
- Qualquer referência a páginas com ID maior ou igual a 64 representa uma violação grave de limite de endereçamento (Out of Bounds / Segmentation Fault).

## Abusos Cometidos
- **P0 (Tempo Real):** Contém as páginas **64** e **100** em sua string de referência.
- **P1 (Usuário):** Contém a página **999** em sua string de referência.

## Comportamento Esperado
O Gerenciador de Memória deve detectar que as referências a páginas excedem o limite de endereçamento virtual [0..63]. Em vez de provocar um travamento geral do pseudo-SO (como um IndexError em Python ou um NullPointerException), o sistema operacional deve encerrar o processo transgressor com um erro adequado de violação de acesso à memória (Segmentation Fault) e liberar os recursos previamente alocados a ele.
