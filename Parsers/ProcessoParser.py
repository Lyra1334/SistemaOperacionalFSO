"""
ProcessoParser.py

Lê e valida Processes.txt e String.txt.
"""

from typing import List

from Core import Config

from Core.Erros import ErroEntrada
from Models.Processo import Processo
from Core.Utils import converterInteiro, converterBooleano, lerLinhasNaoVazias, dividirCsv


class ProcessoParser:

    @staticmethod
    def carregar(caminhoProcessos: str, caminhoStrings: str) -> List[Processo]:
        linhasProcessos = lerLinhasNaoVazias(caminhoProcessos)
        linhasStrings = lerLinhasNaoVazias(caminhoStrings)

        if len(linhasProcessos) > 1000:
            raise ErroEntrada(
                f"Quantidade de processos ({len(linhasProcessos)}) excede o limite do sistema (máximo 1000)."
            )

        if len(linhasProcessos) != len(linhasStrings):
            raise ErroEntrada(
                f"Quantidade de processos ({len(linhasProcessos)}) diferente "
                f"da quantidade de strings ({len(linhasStrings)})."
            )

        processos: List[Processo] = []

        for pid, linha in enumerate(linhasProcessos):
            try:
                partes = dividirCsv(linha)

                if len(partes) != 8:
                    raise ErroEntrada(
                        f"Linha {pid + 1} de processos deve ter 8 campos."
                    )

                tempoChegada = converterInteiro(partes[0], "tempo de inicialização")
                prioridade = converterInteiro(partes[1], "prioridade")
                tempoCpu = converterInteiro(partes[2], "tempo de processador")
                wsSolicitado = converterInteiro(partes[3], "working set")
                limite = Config.QUADROS_MEMORIA_USUARIO if prioridade != 0 else Config.QUADROS_MEMORIA_TEMPO_REAL
                if wsSolicitado > limite:
                    raise ErroEntrada(
                        f"O processo {pid} solicita um working set ({wsSolicitado} frames) "
                        f"que excede a partição de memória disponível ({limite} frames)."
                    )
                workingSet = wsSolicitado

                impressora = converterBooleano(partes[4], "requisição de impressora")
                scanner = converterBooleano(partes[5], "requisição de scanner")
                modem = converterBooleano(partes[6], "requisição de modem")
                sata = converterBooleano(partes[7], "requisição de SATA")

                if tempoChegada < 0:
                    raise ErroEntrada("Tempo de inicialização não pode ser negativo.")
                if tempoChegada > 1000000:
                    raise ErroEntrada("Tempo de inicialização muito grande.")

                if tempoCpu <= 0:
                    raise ErroEntrada("Tempo de processador deve ser maior que zero.")
                if tempoCpu > 1000000:
                    raise ErroEntrada("Tempo de processador muito grande.")

                if workingSet <= 0:
                    raise ErroEntrada("Working set deve ser maior que zero.")

                if prioridade < Config.PRIORIDADE_TEMPO_REAL or prioridade > Config.MAX_PRIORIDADE_USUARIO:
                    raise ErroEntrada("Prioridade deve ser 0, 1, 2 ou 3.")

                if prioridade == Config.PRIORIDADE_TEMPO_REAL:
                    if impressora > 0 or scanner > 0 or modem > 0 or sata > 0:
                        raise ErroEntrada("requer mais recursos do que o possúido pelo sistema.")
                    impressora = 0
                    scanner = 0
                    modem = 0
                    sata = 0

                referencias = []
                for paginaStr in dividirCsv(linhasStrings[pid]):
                    pagina = converterInteiro(paginaStr, "página")
                    if pagina < 0:
                        raise ErroEntrada(f"Número de página não pode ser negativo: {pagina}")
                    
                    # Limitação teórica de endereçamento virtual de 16 bits (máximo 64 páginas de 1 KB).
                    if pagina > 63:
                        raise ErroEntrada(f"Número de página excede o limite de endereçamento virtual de 16 bits (máximo 63): {pagina}")
                    
                    referencias.append(pagina)

                processos.append(
                    Processo(
                        pid=pid,
                        tempoChegada=tempoChegada,
                        prioridade=prioridade,
                        tempoCpu=tempoCpu,
                        workingSet=workingSet,
                        impressora=impressora,
                        scanner=scanner,
                        modem=modem,
                        sata=sata,
                        referencias=referencias
                    )
                )
            except ErroEntrada as e:
                p = Processo(
                    pid=pid,
                    tempoChegada=0,
                    prioridade=3,
                    tempoCpu=1,
                    workingSet=1,
                    impressora=0,
                    scanner=0,
                    modem=0,
                    sata=0,
                    referencias=[]
                )
                p.rejeitado = True
                msg = str(e)
                if "working set" in msg.lower():
                    p.motivoRejeicao = "working set maior que a área de memória permitida."
                elif "recurso" in msg.lower() or "impressora" in msg.lower() or "scanner" in msg.lower() or "modem" in msg.lower() or "sata" in msg.lower():
                    p.motivoRejeicao = "requer mais recursos do que o possúido pelo sistema."
                elif "página" in msg.lower() or "limite de endereçamento" in msg.lower():
                    p.motivoRejeicao = "acesso de memória fora dos limites (Segmentation Fault)."
                else:
                    p.motivoRejeicao = "requer mais recursos do que o possúido pelo sistema."
                processos.append(p)

        return processos