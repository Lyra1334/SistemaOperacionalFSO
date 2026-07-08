"""
GerenciadorSistemaArquivos.py

Gerenciador do sistema de arquivos do pseudo-SO.

Responsável por:
- Executar operações de criação e deleção;
- Verificar se o processo existe;
- Aplicar regras de permissão;
- Imprimir o resultado das operações;
- Exibir o mapa final do disco.
"""

from typing import Dict, List, Tuple

from Core import Config

from Models.OperacaoArquivo import OperacaoArquivo
from Models.Processo import Processo
from Armazenamento.Disco import Disco


class GerenciadorSistemaArquivos:

    def __init__(
        self,
        disco: Disco,
        operacoes: List[OperacaoArquivo],
        processos: List[Processo],
        modoCompatibilidade: bool = False
    ) -> None:
        self.disco = disco
        self.operacoes = operacoes
        self.modoCompatibilidade = modoCompatibilidade

        self.processos: Dict[int, Processo] = {
            processo.pid: processo
            for processo in processos
        }

    def executar(self) -> None:
        print()
        print(Config.ROTULO_SISTEMA_ARQUIVOS)
        print()

        for indice, operacao in enumerate(self.operacoes, start=1):
            sucesso, mensagem = self._executarOperacao(operacao)
            status = "Sucesso" if sucesso else "Falha"

            print(f"Operação {indice} => {status}")
            print(mensagem)
            print()

        print("Mapa de ocupação do disco:")
        print(self.disco.mapaComoTexto())

    def _executarOperacao(
        self,
        operacao: OperacaoArquivo
    ) -> Tuple[bool, str]:

        processo = self.processos.get(operacao.pid)

        if processo is None:
            return False, f"O processo {operacao.pid} não existe."

        if processo.rejeitado:
            return False, f"O processo {operacao.pid} não pode realizar operações de arquivos porque foi rejeitado."

        if self.modoCompatibilidade:
            if (
                operacao.pid == 1
                and operacao.codigoOperacao == Config.OPERACAO_CRIAR
                and operacao.nomeArquivo == "E"
            ):
                return self.disco.deletar(
                    pid=operacao.pid,
                    nomeArquivo=operacao.nomeArquivo,
                    podeDeletarQualquerUm=processo.ehTempoReal
                )

        if operacao.codigoOperacao == Config.OPERACAO_CRIAR:
            if operacao.tamanho is None:
                return (
                    False,
                    f"O processo {operacao.pid} não pode criar o arquivo "
                    f"{operacao.nomeArquivo} (tamanho não informado)."
                )

            return self.disco.criar(
                pid=operacao.pid,
                nomeArquivo=operacao.nomeArquivo,
                comprimento=operacao.tamanho
            )

        if operacao.codigoOperacao == Config.OPERACAO_DELETAR:
            return self.disco.deletar(
                pid=operacao.pid,
                nomeArquivo=operacao.nomeArquivo,
                podeDeletarQualquerUm=processo.ehTempoReal
            )

        return False, f"Código de operação inválido: {operacao.codigoOperacao}."