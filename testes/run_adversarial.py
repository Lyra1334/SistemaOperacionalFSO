import os
import subprocess
import sys

SCENARIOS = [
    "cenario_otimo",
    "cenario_estouro_memoria",
    "cenario_acesso_memoria_proibido",
    "cenario_recursos_indisponiveis",
    "cenario_conflito_pid",
    "cenario_limite_maximo"
]

def run_scenarios():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    adversarios_dir = os.path.join(base_dir, "cenarios_adversarios")
    
    print("=== EXECUTANDO CENÁRIOS ADVERSÁRIOS E GERANDO LOGS ===")
    
    for scenario in SCENARIOS:
        scenario_path = os.path.join(adversarios_dir, scenario)
        
        processes_file = os.path.join(scenario_path, "processes.txt")
        files_file = os.path.join(scenario_path, "files.txt")
        string_file = os.path.join(scenario_path, "string.txt")
        log_file = os.path.join(scenario_path, "saida_simulada.log")
        
        if not os.path.exists(processes_file):
            print(f"[-] Cenário {scenario} não possui os arquivos de entrada.")
            continue
            
        print(f"\n[+] Executando: {scenario}")
        
        # Executa o pseudo-SO
        cmd = [
            sys.executable,
            os.path.join(base_dir, "..", "Main.py"),
            processes_file,
            files_file,
            string_file
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Junta stdout e stderr
        output = result.stdout
        if result.stderr:
            output += "\n--- STDERR ---\n" + result.stderr
            
        # Grava a saída simulada no log
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(output)
            
        print(f"[+] Log gravado em: {os.path.basename(scenario_path)}/saida_simulada.log")
        # Mostra as primeiras 5 linhas e últimas 5 linhas de cada log para acompanhamento rápido
        lines = output.strip().split("\n")
        print("--- Resumo do Log ---")
        if len(lines) <= 10:
            print("\n".join(lines))
        else:
            print("\n".join(lines[:5]))
            print("...")
            print("\n".join(lines[-5:]))
        print("--------------------")

if __name__ == "__main__":
    run_scenarios()
