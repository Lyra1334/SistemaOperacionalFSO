class arquivos:

    def __init__(self, tamanho:int, blocosOcupados:list):
        #Inicializa a memória já preenchida. Mandar os blocos pré ocupados no seguinte formato:
        # [(X,0,2),(Y,3,1),(Z,5,3)]
        self.disco = [0 for x in range(tamanho)]
        for blocos in blocosOcupados:
            for i in range(blocos[1],blocos[1]+blocos[2]):
                self.disco[i] = blocos[0]

    def write(self, nome:str, tamanho:int):
        espaco_verificado = False
        for i in range(len(self.disco)):
            if i == "0":
                espaco_verificado = True