import os
import subprocess
import time
import platform

services = [
    {"name": "Catálogo Service",   "folder": "catalogo-service",   "port": 8001},
    {"name": "Usuários Service",   "folder": "usuarios-service",   "port": 8002},
    {"name": "Pedidos Service",    "folder": "pedidos-service",    "port": 8003},
    {"name": "Estoque Service",    "folder": "estoque-service",    "port": 8004},
    {"name": "Pagamento Service",  "folder": "pagamento-service",  "port": 8005},
]

print("🚀 Iniciando todos os Microserviços (Linux)...\n")

for service in services:
    folder = service["folder"]
    name = service["name"]
    port = service["port"]

    if not os.path.exists(folder):
        print(f"⚠️  Pasta não encontrada: {folder}")
        continue

    print(f"🔹 Iniciando {name} na porta {port}...")

    run_cmd = f"cd {folder} && echo '=== {name} - Porta {port} ===' && pip install -r requirements.txt && uvicorn main:app --reload --port {port}"

    try:
        subprocess.Popen(['gnome-terminal', '--title', name, '--', 'bash', '-c', f"{run_cmd}; exec bash"])
    except FileNotFoundError:
        try:
            subprocess.Popen(['xterm', '-T', name, '-e', f"{run_cmd}; bash"])
        except FileNotFoundError:
            print(f"⚠️  Não foi possível abrir terminal para {name}.")

    time.sleep(1.8)

print("\n✅ Todos os serviços iniciados no Linux!")