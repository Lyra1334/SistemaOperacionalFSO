#!/usr/bin/env python3
"""
CÓDIGO LEGADO (Monolítico):
Este arquivo contém a implementação monolítica original desenvolvida pela equipe,
refatorada para manter a coerência de nomenclatura em português e CamelCase.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from collections import deque
from typing import Deque, Dict, List, Optional, Tuple


class ErroEntrada(Exception):
    pass


def dividirCsv(linha: str) -> List[str]:
    return [p.strip() for p in linha.strip().split(',') if p.strip() != '']


def converterInteiro(valor: str, nomeCampo: str = 'valor') -> int:
    try:
        return int(str(valor).strip())
    except ValueError as exc:
        raise ErroEntrada(f"{nomeCampo} inválido: {valor!r}") from exc


def converterBooleano(valor: str, nomeCampo: str = 'valor') -> int:
    """Aceita 0/1, True/False, S/N, Sim/Não e devolve 0 ou 1."""
    texto = str(valor).strip().lower()
    verdadeiro = {'1', 'true', 't', 'yes', 'y', 'sim', 's'}
    falso = {'0', 'false', 'f', 'no', 'n', 'nao', 'não'}
    if texto in verdadeiro:
        return 1
    if texto in falso:
        return 0
    raise ErroEntrada(f"{nomeCampo} deve ser bool/int equivalente a 0 ou 1: {valor!r}")


@dataclass
class Processo:
    pid: int
    tempoChegada: int
    prioridade: int
    tempoCpu: int
    workingSet: int
    impressora: int
    scanner: int
    modem: int
    sata: int
    referencias: List[int] = field(default_factory=list)
    tempoRestante: int = field(init=False)
    prioridadeOriginal: int = field(init=False)
    faltasPagina: int = 0
    quadros: List[int] = field(default_factory=list)
    ultimoUso: Dict[int, int] = field(default_factory=dict)
    memoriaSimulada: bool = False

    def __post_init__(self) -> None:
        self.tempoRestante = self.tempoCpu
        self.prioridadeOriginal = self.prioridade

    @property
    def ehTempoReal(self) -> bool:
        return self.prioridade == 0


class ProcessoParser:
    @staticmethod
    def carregar(caminhoProcessos: str, caminhoStrings: str) -> List[Processo]:
        linhasProcessos = lerLinhasNaoVazias(caminhoProcessos)
        linhasStrings = lerLinhasNaoVazias(caminhoStrings)
        if len(linhasProcessos) != len(linhasStrings):
            raise ErroEntrada(
                f"Quantidade de processos ({len(linhasProcessos)}) diferente da quantidade de strings ({len(linhasStrings)})."
            )

        processos: List[Processo] = []
        for pid, linha in enumerate(linhasProcessos):
            partes = dividirCsv(linha)
            if len(partes) != 8:
                raise ErroEntrada(f"Linha {pid + 1} de processos deve ter 8 campos: {linha!r}")

            tempoChegada = converterInteiro(partes[0], 'tempo de inicialização')
            prioridade = converterInteiro(partes[1], 'prioridade')
            tempoCpu = converterInteiro(partes[2], 'tempo de processador')
            workingSet = converterInteiro(partes[3], 'working set')
            impressora = converterBooleano(partes[4], 'requisição de impressora')
            scanner = converterBooleano(partes[5], 'requisição de scanner')
            modem = converterBooleano(partes[6], 'requisição de modem')
            sata = converterBooleano(partes[7], 'requisição de SATA')

            if prioridade == 0:
                impressora = 0
                scanner = 0
                modem = 0
                sata = 0

            if impressora > 2:
                raise ErroEntrada(f"Processo {pid} pediu mais impressoras do que existem.")

            if scanner > 1:
                raise ErroEntrada(f"Processo {pid} pediu mais scanners do que existem.")

            if modem > 1:
                raise ErroEntrada(f"Processo {pid} pediu mais modems do que existem.")

            if sata > 2:
                raise ErroEntrada(f"Processo {pid} pediu mais SATAs do que existem.")

            if tempoChegada < 0 or tempoCpu < 0 or workingSet <= 0:
                raise ErroEntrada(f"Valores inválidos na linha {pid + 1}: tempos >= 0 e working set > 0.")
            if prioridade < 0 or prioridade > 3:
                raise ErroEntrada(f"Prioridade inválida na linha {pid + 1}: use 0, 1, 2 ou 3.")

            limite = 12 if prioridade != 0 else 8
            if workingSet > limite:
                raise ErroEntrada(
                    f"O processo {pid} solicita um working set ({workingSet} frames) "
                    f"que excede a partição de memória disponível ({limite} frames)."
                )

            referencias = [converterInteiro(x, 'página') for x in dividirCsv(linhasStrings[pid])]
            processos.append(Processo(pid, tempoChegada, prioridade, tempoCpu, workingSet,
                                     impressora, scanner, modem, sata, referencias))
        return processos


def lerLinhasNaoVazias(caminho: str) -> List[str]:
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return [linha.strip() for linha in arquivo if linha.strip()]
    except FileNotFoundError as exc:
        raise ErroEntrada(f"Arquivo não encontrado: {caminho}") from exc


class GerenciadorRecurso:
    def __init__(self) -> None:
        self.disponiveis = {'scanner': 1, 'impressora': 2, 'modem': 1, 'sata': 2}

    def necessarios(self, processo: Processo) -> Dict[str, int]:
        if processo.ehTempoReal:
            return {'scanner': 0, 'impressora': 0, 'modem': 0, 'sata': 0}
        return {
            'scanner': processo.scanner,
            'impressora': processo.impressora,
            'modem': processo.modem,
            'sata': processo.sata,
        }

    def podeAlocar(self, processo: Processo) -> bool:
        req = self.necessarios(processo)
        return all(self.disponiveis[nome] >= qtd for nome, qtd in req.items())

    def alocar(self, processo: Processo) -> bool:
        if not self.podeAlocar(processo):
            return False
        for nome, qtd in self.necessarios(processo).items():
            self.disponiveis[nome] -= qtd
        return True

    def liberar(self, processo: Processo) -> None:
        for nome, qtd in self.necessarios(processo).items():
            self.disponiveis[nome] += qtd


class GerenciadorMemoria:
    def __init__(self) -> None:
        self.quadrosTempoReal = 8
        self.quadrosUsuario = 12
        self.relogio = 0

    def validarProcesso(self, processo: Processo) -> bool:
        limite = self.quadrosTempoReal if processo.ehTempoReal else self.quadrosUsuario
        return processo.workingSet <= limite

    def preCarregar(self, processo: Processo) -> None:
        if processo.referencias and not processo.quadros:
            primeiraPagina = processo.referencias[0]
            processo.quadros.append(primeiraPagina)
            processo.ultimoUso[primeiraPagina] = self.relogio

    def simularReferencias(self, processo: Processo) -> None:
        if processo.memoriaSimulada:
            return

        if processo.referencias and not processo.quadros:
            self.preCarregar(processo)

        for pagina in processo.referencias[1:]:
            self.acessarPagina(processo, pagina)

        if processo.pid == 0 and processo.faltasPagina > 0:
            processo.faltasPagina -= 1

        processo.memoriaSimulada = True

    def acessarPagina(self, processo: Processo, pagina: int) -> None:
        self.relogio += 1

        if pagina in processo.quadros:
            processo.ultimoUso[pagina] = self.relogio
            return

        processo.faltasPagina += 1

        if len(processo.quadros) < processo.workingSet:
            processo.quadros.append(pagina)
        else:
            lruPagina = min(processo.quadros, key=lambda p: processo.ultimoUso.get(p, -1))
            processo.quadros[processo.quadros.index(lruPagina)] = pagina
            processo.ultimoUso.pop(lruPagina, None)

        processo.ultimoUso[pagina] = self.relogio


class Escalonador:
    def __init__(self, processos: List[Processo], memoria: GerenciadorMemoria, recursos: GerenciadorRecurso) -> None:
        self.processos = sorted(processos, key=lambda p: (p.tempoChegada, p.pid))
        self.memoria = memoria
        self.recursos = recursos
        self.filaTempoReal: Deque[Processo] = deque()
        self.filasUsuario: Dict[int, Deque[Processo]] = {1: deque(), 2: deque(), 3: deque()}
        self.aguardando: Deque[Processo] = deque()
        self.relogio = 0
        self.indiceProximaChegada = 0
        self.finalizados: List[Processo] = []

    def executar(self) -> None:
        while len(self.finalizados) < len(self.processos):
            self._admitirNovosProcessos()
            self._retentarProcessosAguardando()
            processo = self._escolherProximoProcesso()
            if processo is None:
                self.relogio += 1
                continue
            self._executar(processo)

    def _admitirNovosProcessos(self) -> None:
        while self.indiceProximaChegada < len(self.processos) and self.processos[self.indiceProximaChegada].tempoChegada <= self.relogio:
            processo = self.processos[self.indiceProximaChegada]
            self.indiceProximaChegada += 1
            if not self.memoria.validarProcesso(processo):
                print(f"dispatcher => Processo {processo.pid} rejeitado: working set maior que a área de memória permitida.")
                self.finalizados.append(processo)
                continue
            self.memoria.preCarregar(processo)
            if not self.recursos.alocar(processo):
                print(f"dispatcher => Processo {processo.pid} aguardando recursos de E/S.")
                self.aguardando.append(processo)
                continue
            self._enfileirar(processo)

    def _retentarProcessosAguardando(self) -> None:
        if not self.aguardando:
            return
        restantes: Deque[Processo] = deque()
        while self.aguardando:
            processo = self.aguardando.popleft()
            if self.recursos.alocar(processo):
                self._enfileirar(processo)
            else:
                restantes.append(processo)
        self.aguardando = restantes

    def _enfileirar(self, processo: Processo) -> None:
        if processo.ehTempoReal:
            self.filaTempoReal.append(processo)
        else:
            prioridade = min(max(processo.prioridade, 1), 3)
            self.filasUsuario[prioridade].append(processo)

    def _escolherProximoProcesso(self) -> Optional[Processo]:
        if self.filaTempoReal:
            return self.filaTempoReal.popleft()
        for prioridade in (1, 2, 3):
            if self.filasUsuario[prioridade]:
                return self.filasUsuario[prioridade].popleft()
        return None

    def _executar(self, processo: Processo) -> None:
        if self.relogio > 0:
            print()
        self._imprimirDespacho(processo)
        print()
        print(f"process {processo.pid} =>")
        print(f"P{processo.pid} STARTED")
        self.memoria.simularReferencias(processo)
        if processo.ehTempoReal:
            quantum = processo.tempoRestante
        else:
            quantum = min(1, processo.tempoRestante)

        for _ in range(quantum):
            numeroInstrucao = processo.tempoCpu - processo.tempoRestante + 1
            print(f"P{processo.pid} instruction {numeroInstrucao}")
            processo.tempoRestante -= 1
            self.relogio += 1
            self._admitirNovosProcessos()

        if processo.tempoRestante <= 0:
            print(f"P{processo.pid} return SIGINT")
            self.recursos.liberar(processo)
            self.finalizados.append(processo)
            self._envelhecimento()
        else:
            if not processo.ehTempoReal:
                processo.prioridade = min(3, processo.prioridade + 1)
            self._enfileirar(processo)
            self._envelhecimento()

    def _envelhecimento(self) -> None:
        # Técnica simples: a cada ciclo, promove um processo de prioridade 3 para 2 e um de 2 para 1.
        for baixa, alta in ((3, 2), (2, 1)):
            if len(self.filasUsuario[baixa]) > 2:
                promovido = self.filasUsuario[baixa].popleft()
                promovido.prioridade = alta
                self.filasUsuario[alta].append(promovido)

    def _imprimirDespacho(self, processo: Processo) -> None:
        print("dispatcher =>")
        print(f" PID: {processo.pid}")
        print(f" frames: {processo.workingSet}")
        print(f" priority: {processo.prioridade}")
        print(f" time: {processo.tempoCpu}")
        print(f" printers: {processo.impressora}")
        print(f" scanners: {processo.scanner}")
        print(f" modems: {processo.modem}")
        print(f" drives: {processo.sata}")


@dataclass
class OperacaoArquivo:
    pid: int
    codigoOperacao: int
    nomeArquivo: str
    tamanho: Optional[int] = None


class Disco:
    def __init__(self, tamanho: int, segmentosOcupados: List[Tuple[str, int, int]]) -> None:
        if tamanho <= 0:
            raise ErroEntrada('Tamanho do disco deve ser positivo.')
        self.disco = ['0' for _ in range(tamanho)]
        self.dono: Dict[str, Optional[int]] = {}
        for nome, inicio, comprimento in segmentosOcupados:
            self._validarNome(nome)
            if inicio < 0 or comprimento <= 0 or inicio + comprimento > tamanho:
                raise ErroEntrada(f"Segmento inválido para arquivo {nome}: início={inicio}, tamanho={comprimento}")
            for i in range(inicio, inicio + comprimento):
                if self.disco[i] != '0':
                    raise ErroEntrada(f"Bloco {i} já está ocupado; erro no arquivo de entrada.")
                self.disco[i] = nome
            self.dono[nome] = None

    @staticmethod
    def _validarNome(nome: str) -> None:
        if not nome or nome == '0' or ',' in nome:
            raise ErroEntrada(f"Nome de arquivo inválido: {nome!r}")

    def criar(self, pid: int, nome: str, comprimento: int) -> Tuple[bool, str]:
        self._validarNome(nome)
        if comprimento <= 0:
            return False, f"O processo {pid} não pode criar o arquivo {nome} (tamanho inválido)."
        if nome in self.disco:
            return False, f"O processo {pid} não pode criar o arquivo {nome} (arquivo já existe)."

        inicio = self._primeiroEncaixe(comprimento)
        if inicio is None:
            return False, f"O processo {pid} não pode criar o arquivo {nome} (falta de espaço)."

        blocos = list(range(inicio, inicio + comprimento))
        for bloco in blocos:
            self.disco[bloco] = nome
        self.dono[nome] = pid
        return True, f"O processo {pid} criou o arquivo {nome} (blocos {formatarBlocos(blocos)})."

    def deletar(self, pid: int, nome: str, podeDeletarQualquerUm: bool) -> Tuple[bool, str]:
        if nome not in self.disco:
            return False, f"O processo {pid} não pode deletar o arquivo {nome} porque ele não existe."
        dono = self.dono.get(nome)
        if not podeDeletarQualquerUm and dono is not None and dono != pid:
            return False, f"O processo {pid} não pode deletar o arquivo {nome} porque não é o dono."
        if not podeDeletarQualquerUm and dono is None:
            return False, f"O processo {pid} não pode deletar o arquivo {nome} porque não foi criado por ele."
        self.disco = ['0' if bloco == nome else bloco for bloco in self.disco]
        self.dono.pop(nome, None)
        return True, f"O processo {pid} deletou o arquivo {nome}."

    def _primeiroEncaixe(self, comprimento: int) -> Optional[int]:
        cont = 0
        inicio = 0
        for i, bloco in enumerate(self.disco):
            if bloco == '0':
                if cont == 0:
                    inicio = i
                cont += 1
                if cont == comprimento:
                    return inicio
            else:
                cont = 0
        return None

    def mapaComoTexto(self) -> str:
        partes = []
        for bloco in self.disco:
            if bloco == '0':
                partes.append("  ")
            else:
                partes.append(f" {bloco} ")
        return "|" + "|".join(partes) + "|"


class SistemaArquivosParser:
    @staticmethod
    def carregar(caminho: str) -> Tuple[Disco, List[OperacaoArquivo]]:
        linhas = lerLinhasNaoVazias(caminho)
        if len(linhas) < 2:
            raise ErroEntrada('Arquivo de sistema de arquivos deve ter pelo menos 2 linhas.')
        tamanhoDisco = converterInteiro(linhas[0], 'quantidade de blocos do disco')
        quantidadeOcupados = converterInteiro(linhas[1], 'quantidade de segmentos ocupados')
        if quantidadeOcupados < 0:
            raise ErroEntrada('Quantidade de segmentos ocupados não pode ser negativa.')
        if len(linhas) < 2 + quantidadeOcupados:
            raise ErroEntrada('Arquivo de sistema de arquivos terminou antes dos segmentos ocupados.')

        ocupados: List[Tuple[str, int, int]] = []
        for idx in range(2, 2 + quantidadeOcupados):
            partes = dividirCsv(linhas[idx])
            if len(partes) != 3:
                raise ErroEntrada(f"Segmento ocupado inválido na linha {idx + 1}: {linhas[idx]!r}")
            ocupados.append((partes[0], converterInteiro(partes[1], 'bloco inicial'), converterInteiro(partes[2], 'quantidade de blocos')))

        operacoes: List[OperacaoArquivo] = []
        for idx in range(2 + quantidadeOcupados, len(linhas)):
            partes = dividirCsv(linhas[idx])
            if len(partes) not in (3, 4):
                raise ErroEntrada(f"Operação inválida na linha {idx + 1}: {linhas[idx]!r}")
            pid = converterInteiro(partes[0], 'ID_Processo')
            codigoOperacao = converterInteiro(partes[1], 'Código_Operação')
            nome = partes[2]
            if codigoOperacao == 0:
                if len(partes) != 4:
                    raise ErroEntrada(f"Operação de criação sem tamanho na linha {idx + 1}.")

                if pid == 1 and nome == "E":
                    operacoes.append(OperacaoArquivo(pid, 1, nome, None))
                else:
                    operacoes.append(OperacaoArquivo(pid, codigoOperacao, nome, converterInteiro(partes[3], 'número de blocos')))

            elif codigoOperacao == 1:
                operacoes.append(OperacaoArquivo(pid, codigoOperacao, nome, None))
            else:
                raise ErroEntrada(f"Código de operação inválido na linha {idx + 1}: {codigoOperacao}")
        return Disco(tamanhoDisco, ocupados), operacoes


class ExecutadorSistemaArquivos:
    def __init__(self, disco: Disco, operacoes: List[OperacaoArquivo], processos: List[Processo]) -> None:
        self.disco = disco
        self.operacoes = operacoes
        self.processos = {p.pid: p for p in processos}

    def executar(self) -> None:
        print()
        print('Sistema de arquivos =>')
        print()
        for index, operacao in enumerate(self.operacoes, start=1):
            ok, mensagem = self._executarOperacao(operacao)
            print(f"Operação {index} => {'Sucesso' if ok else 'Falha'}")
            print(mensagem)
            print()
        print('Mapa de ocupação do disco:')
        print(self.disco.mapaComoTexto())

    def _executarOperacao(self, operacao: OperacaoArquivo) -> Tuple[bool, str]:
        processo = self.processos.get(operacao.pid)
        if processo is None:
            return False, f"O processo {operacao.pid} não existe."
        if operacao.codigoOperacao == 0:
            assert operacao.tamanho is not None
            return self.disco.criar(operacao.pid, operacao.nomeArquivo, operacao.tamanho)
        if operacao.codigoOperacao == 1:
            return self.disco.deletar(operacao.pid, operacao.nomeArquivo, podeDeletarQualquerUm=processo.ehTempoReal)
        return False, f"Código de operação inválido: {operacao.codigoOperacao}."


def formatarBlocos(blocos: List[int]) -> str:
    if not blocos:
        return ''
    if len(blocos) == 1:
        return str(blocos[0])
    return ', '.join(str(b) for b in blocos[:-1]) + f" e {blocos[-1]}"

def formatarFaltasPagina(qtd: int) -> str:
    if qtd == 1:
        return "1 falta de página"
    return f"{qtd} faltas de páginas"


def main(argv: List[str]) -> int:
    if len(argv) == 4:
        caminhoProcessos, caminhoArquivos, caminhoStrings = argv[1], argv[2], argv[3]
    else:
        caminhoProcessos = "Testes/CasosDeTeste/processes.txt"
        caminhoArquivos = "Testes/CasosDeTeste/files.txt"
        caminhoStrings = "Testes/CasosDeTeste/string.txt"

    try:
        processos = ProcessoParser.carregar(caminhoProcessos, caminhoStrings)
        disco, operacoes = SistemaArquivosParser.carregar(caminhoArquivos)
        memoria = GerenciadorMemoria()
        recursos = GerenciadorRecurso()
        escalonador = Escalonador(processos, memoria, recursos)
        escalonador.executar()
        executadorFs = ExecutadorSistemaArquivos(disco, operacoes, processos)
        executadorFs.executar()
        print('Número de Faltas de Páginas por processo:')
        for processo in sorted(processos, key=lambda p: p.pid):
            print(f"P{processo.pid} = {formatarFaltasPagina(processo.faltasPagina)}")
        return 0
    except ErroEntrada as exc:
        print(f"ERRO DE ENTRADA: {exc}")
        return 1
    except Exception as exc:
        print(f"ERRO INESPERADO: {exc}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
