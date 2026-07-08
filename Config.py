# Memória
TOTAL_MEMORY_FRAMES = 20
REALTIME_MEMORY_FRAMES = 8
USER_MEMORY_FRAMES = 12
FRAME_SIZE_KB = 1

# Escalonamento
REALTIME_PRIORITY = 0
MAX_USER_PRIORITY = 3
USER_QUANTUM = 1          # ms
MAX_PROCESSES = 1000

# Recursos de E/S
TOTAL_SCANNERS = 1
TOTAL_PRINTERS = 2
TOTAL_MODEMS = 1
TOTAL_SATA_DRIVES = 2

# Sistema de Arquivos
FREE_BLOCK = "0"
CREATE_OPERATION = 0
DELETE_OPERATION = 1

# Diretórios padrão
DEFAULT_PROCESSES_FILE = "testes/casosDeTeste/processes.txt"
DEFAULT_FILESYSTEM_FILE = "testes/casosDeTeste/files.txt"
DEFAULT_REFERENCES_FILE = "testes/casosDeTeste/string.txt"

# Mensagens
DISPATCHER_LABEL = "dispatcher =>"
FILESYSTEM_LABEL = "Sistema de arquivos =>"
PAGEFAULT_LABEL = "Número de Faltas de Páginas por processo:"

# Modos de leitura do Parser de Entrada
ENABLE_PDF_COMPATIBILITY = True