import os
import subprocess
import sys

CENARIOS = [
    "CenarioOtimo",
    "CenarioEstouroMemoria",
    "CenarioAcessoMemoriaProibido",
    "CenarioRecursosIndisponiveis",
    "CenarioConflitoPid",
    "CenarioLimiteMaximo"
]

def executar_cenarios():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    adversarios_dir = os.path.join(base_dir, "CenariosAdversarios")
    
    print("=== EXECUTANDO CENÁRIOS ADVERSÁRIOS E GERANDO LOGS ===")
    
    for cenario in CENARIOS:
        caminho_cenario = os.path.join(adversarios_dir, cenario)
        
        arquivo_processos = os.path.join(caminho_cenario, "processes.txt")
        arquivo_arquivos = os.path.join(caminho_cenario, "files.txt")
        arquivo_strings = os.path.join(caminho_cenario, "string.txt")
        arquivo_log = os.path.join(caminho_cenario, "saida_simulada.log")
        
        if not os.path.exists(arquivo_processos):
            print(f"[-] Cenário {cenario} não possui os arquivos de entrada.")
            continue
            
        print(f"\n[+] Executando: {cenario}")
        
        # Executa o pseudo-SO
        cmd = [
            sys.executable,
            os.path.join(base_dir, "..", "Main.py"),
            arquivo_processos,
            arquivo_arquivos,
            arquivo_strings
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Junta stdout e stderr
        output = result.stdout
        if result.stderr:
            output += "\n--- STDERR ---\n" + result.stderr
            
        # Grava a saída simulada no log
        with open(arquivo_log, "w", encoding="utf-8") as f:
            f.write(output)
            
        print(f"[+] Log gravado em: {os.path.basename(caminho_cenario)}/saida_simulada.log")
        # Mostra as primeiras 5 linhas e últimas 5 linhas de cada log para acompanhamento rápido
        linhas = output.strip().split("\n")
        print("--- Resumo do Log ---")
        if len(linhas) <= 10:
            print("\n".join(linhas))
        else:
            print("\n".join(linhas[:5]))
            print("...")
            print("\n".join(linhas[-5:]))
        print("--------------------")

if __name__ == "__main__":
    executar_cenarios()
