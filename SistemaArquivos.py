#A classe não vê os processos, esse check tem que ser feito pelo processador principal
#TODO: definir retornos. por enquanto deixo assim pra gente saber o que tá acontecendo

class arquivos:

    def __init__(self, tamanho:int, blocosOcupados:list):
        #Inicializa a memória já preenchida. Mandar os blocos pré ocupados no seguinte formato:
        # [(X,0,2),(Y,3,1),(Z,5,3)]
        self.disco = ["0" for x in range(tamanho)]
        for blocos in blocosOcupados:
            for i in range(blocos[1],blocos[1]+blocos[2]):
                self.disco[i] = blocos[0]

    def write(self, nome:str, tamanho:int):
        cont = 0    #Contagem de espaços livres seguidos
        start = 0   #Primeiro espaço livre achado do conjunto
        last = None #Nome visto antes do atual

        if nome in self.disco:
            return "ERRO: Documento com mesmo nome"
        #Verifica todos espaços em ordem
        for i in range(len(self.disco)):

            if self.disco[i] == "0":
                cont +=1

                #Se o último não era 0, então esse é o primeiro do conjunto.
                if last != 0:
                    start = i

                #Se a contagem é igual ao tamanho necessário, dá pra escrever já (first-fit)
                if cont == tamanho:
                    #Lista de blocos que vão ser escritos.
                    blocos = [x for x in range(start, start+tamanho)]

                    for x in blocos:
                        self.disco[x] = nome
                    return f"Sucesso, artigo escrito nos blocos {blocos}."
            else:
                cont = 0
            
            last = self.disco[i]
        return "ERRO: Falta de espaço"
    
    def delete(self, nome:str):
        #Se não achou o nome do arquivo, ele não tá lá.
        if self.disco.count(nome) == 0:
            return "ERRO: Arquivo não existe"
        else:
            #Usa compreensão de listas pra deletar o arquivo
            self.disco = [bloco if bloco != nome else "0" for bloco in self.disco]
            return "Sucesso"