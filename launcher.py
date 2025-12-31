import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import time
import webbrowser
import os
import signal
import socket
import threading
from pathlib import Path
import argparse

# Tentar importar psutil, mas aceitar fallback
try:
    import psutil
except Exception:
    psutil = None

class SistemaCaixaLauncher:
    """Launcher melhorado:
    - Inicia o servidor em subprocess (isolado)
    - Start não bloqueante (usa Thread)
    - Tenta portas subsequentes se a inicial falhar
    - Grava logs em 'launcher.log' e pid/porta em 'app.pid'
    - Encerra árvore de processos via psutil quando disponível, com fallback
    """

    MAX_PORT_TRIES = 50
    START_TIMEOUT = 5  # segundos para esperar o servidor responder

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Caixa")
        self.root.geometry("400x330")
        self.root.resizable(False, False)

        # Definir paths
        base = Path(__file__).parent
        self.base_dir = str(base)
        self.log_path = base / "launcher.log"
        self.pid_path = base / "app.pid"

        # Definir ícone da janela
        self.set_window_icon()

        # Centralizar janela na tela
        self.center_window()

        # Variáveis de controle
        self.app_process = None
        self.selected_port = None
        self.port = 5001
        self.is_running = False
        self.starting = False
        self.log_file = None
        self._extracted_app_path = None

        # Configurar estilo
        self.setup_styles()

        # Criar interface
        self.create_widgets()

        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Iniciar aplicação automaticamente, sem bloquear a UI
        self.root.after(100, self.start_application_threaded)

    def set_window_icon(self):
        """Define o ícone da janela e da barra de tarefas"""
        try:
            icon_paths = [
                os.path.join(getattr(sys, '_MEIPASS', ''), 'logo.ico'),
                os.path.join(os.path.dirname(__file__), 'logo.ico'),
                os.path.join(os.getcwd(), 'logo.ico')
            ]

            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    print(f"Icone carregado de: {icon_path}")
                    return

            print("Aviso: logo.ico nao encontrado em nenhum local")

        except Exception as e:
            print(f"Aviso: Nao foi possivel carregar o icone: {e}")

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Link.TLabel', font=('Arial', 9), foreground='blue')

    def create_widgets(self):
        """Cria os widgets da interface"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Sistema de Controle de Caixa", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.open_button = ttk.Button(
            button_frame,
            text="🌐 Abrir Página Web",
            command=self.open_web_page,
            state='disabled'
        )
        self.open_button.pack(pady=5, fill=tk.X, padx=20)

        self.close_button = ttk.Button(
            button_frame,
            text="❌ Fechar Aplicação",
            command=lambda: self.stop_application(force=True),
            state='disabled'
        )
        self.close_button.pack(pady=5, fill=tk.X, padx=20)

        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=10, fill=tk.X)

        self.status_label = ttk.Label(info_frame, text="Iniciando...", style='Status.TLabel')
        self.status_label.pack(pady=5)

        self.url_label = ttk.Label(info_frame, text="", style='Status.TLabel')
        self.url_label.pack(pady=5)

        github_link = ttk.Label(info_frame, text="🔗 Desenvolvido por Sávio Gabriel", style='Link.TLabel', cursor="hand2")
        github_link.pack(pady=10)
        github_link.bind("<Button-1>", lambda e: self.open_github())

    def open_github(self):
        webbrowser.open("https://github.com/santos-savio")

    def is_port_available(self, port):
        """Checa rapidamente se a porta parece livre fazendo bind local.
        Ainda assim, podem ocorrer races; é apenas um filtro rápido."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    def start_application_threaded(self):
        """Inicia o processo em uma thread para não bloquear a UI"""
        if self.is_running or self.starting:
            return

        # Verifica se já existe uma instância via pid
        if self.check_existing_instance():
            return

        self.starting = True
        self.status_label.config(text="Iniciando aplicacao...", style='Status.TLabel')
        self.open_button.config(state='disabled')
        self.close_button.config(state='disabled')

        t = threading.Thread(target=self._try_ports_and_start, daemon=True)
        t.start()

    def _try_ports_and_start(self):
        base_dir = self.base_dir

        # Criar arquivo de log (append) quando iniciar
        try:
            logf = open(self.log_path, 'ab')
            self.log_file = logf
        except Exception as e:
            logf = None
            print(f"Aviso: nao foi possivel abrir launcher.log: {e}")

        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        tried = 0
        for port in range(self.port, self.port + self.MAX_PORT_TRIES):
            tried += 1

            # Se parece ocupada, pule rapido
            if not self.is_port_available(port):
                continue

            # Single-EXE: inicia o proprio executavel (frozen) ou o proprio script (dev) em modo servidor
            if getattr(sys, 'frozen', False):
                cmd = [
                    sys.executable,
                    '--server',
                    '--host', '127.0.0.1',
                    '--port', str(port),
                    '--no-browser',
                ]
                cwd = base_dir
            else:
                script_path = os.path.abspath(__file__)
                cmd = [
                    sys.executable,
                    script_path,
                    '--server',
                    '--host', '127.0.0.1',
                    '--port', str(port),
                    '--no-browser',
                ]
                cwd = base_dir

            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=cwd or base_dir,
                    stdout=logf or subprocess.DEVNULL,
                    stderr=logf or subprocess.DEVNULL,
                    creationflags=creationflags
                )
                self.app_process = proc

                # Esperar servidor
                if self.wait_for_server(host='127.0.0.1', port=port, timeout=self.START_TIMEOUT):
                    # Sucesso
                    self.selected_port = port
                    self.is_running = True
                    self.starting = False
                    try:
                        self._write_pid(proc.pid, port)
                    except Exception:
                        pass

                    self.root.after(0, lambda: self._on_started(port))
                    return
                else:
                    # falhou: mata e tenta proxima
                    self._terminate_proc(proc)
                    self.app_process = None
                    continue

            except Exception as e:
                print(f"Erro ao tentar iniciar app em porta {port}: {e}")
                continue

        # Se chegou aqui, não conseguiu iniciar
        self.starting = False
        self.root.after(0, lambda: self.show_error("Nenhuma porta livre encontrada ou o servidor falhou ao iniciar. Verifique launcher.log para detalhes."))

    def wait_for_server(self, host: str, port: int, timeout: int = 5) -> bool:
        """Espera até o servidor aceitar conexão TCP"""
        start = time.time()
        while time.time() - start < timeout:
            # Se iniciamos um processo e ele morreu, falhou
            if self.app_process and self.app_process.poll() is not None:
                return False
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return True
            except OSError:
                time.sleep(0.2)
        return False

    def _on_started(self, port: int):
        self.status_label.config(text="✅ Aplicacao rodando", style='Success.TLabel')
        self.url_label.config(text=f"📍 http://127.0.0.1:{port}")
        self.open_button.config(state='normal')
        self.close_button.config(state='normal')
        # abrir navegador automaticamente
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
        except Exception:
            pass

    def open_web_page(self):
        if self.is_running or self.selected_port:
            webbrowser.open(f'http://127.0.0.1:{self.selected_port or self.port}')
        else:
            messagebox.showwarning("Aviso", "A aplicacao nao esta rodando!")

    def _write_pid(self, pid: int, port: int):
        try:
            with open(self.pid_path, 'w') as f:
                f.write(f"{pid}\n{port}\n")
        except Exception as e:
            print(f"Aviso: nao foi possivel gravar pid: {e}")

    def _read_pid(self):
        try:
            with open(self.pid_path, 'r') as f:
                parts = f.read().splitlines()
                if not parts:
                    return None, None
                pid = int(parts[0])
                port = int(parts[1]) if len(parts) > 1 else None
                return pid, port
        except Exception:
            return None, None

    def _remove_pid(self):
        try:
            if self.pid_path.exists():
                self.pid_path.unlink()
        except Exception:
            pass

    def check_existing_instance(self) -> bool:
        """Checa se ja existe instancia via arquivo PID. Se existir e estiver viva, adota-a."""
        pid, port = self._read_pid()
        if pid is None:
            return False

        # Se psutil disponível, verifica existência do processo
        if psutil:
            try:
                if psutil.pid_exists(pid):
                    p = psutil.Process(pid)
                    if p.is_running():
                        # Assume que é a mesma app; adota
                        self.is_running = True
                        self.selected_port = port
                        self.root.after(0, lambda: self._on_started(port))
                        return True
            except Exception:
                pass

        # Fallback: tenta conectar na porta armazenada
        if port:
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                    self.is_running = True
                    self.selected_port = port
                    self.root.after(0, lambda: self._on_started(port))
                    return True
            except Exception:
                pass

        # Se chegou aqui, o PID/porta não representam uma instância viva
        try:
            self._remove_pid()
        except Exception:
            pass
        return False

    def _terminate_proc(self, proc: subprocess.Popen):
        """Tenta encerrar o processo e seus filhos; usa psutil se disponível."""
        if proc is None:
            return
        try:
            pid = proc.pid
            if psutil:
                try:
                    p = psutil.Process(pid)
                    children = p.children(recursive=True)
                    for c in children:
                        c.terminate()
                    _, alive = psutil.wait_procs(children, timeout=3)
                    for c in alive:
                        c.kill()
                    p.terminate()
                    try:
                        p.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        p.kill()
                except psutil.NoSuchProcess:
                    pass
            else:
                # fallback: tenta terminar e matar
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        except Exception:
            pass

    def stop_application(self, force: bool = False):
        """Para a aplicação Flask (subprocess) usando PID se possível"""
        # Se houver pid file, prioriza usar ele
        pid, port = self._read_pid()
        if pid:
            # tenta encerrar processo externo
            try:
                if psutil and psutil.pid_exists(pid):
                    p = psutil.Process(pid)
                    try:
                        children = p.children(recursive=True)
                        for c in children:
                            c.terminate()
                        _, alive = psutil.wait_procs(children, timeout=3)
                        for c in alive:
                            c.kill()
                        p.terminate()
                        try:
                            p.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            p.kill()
                    except psutil.NoSuchProcess:
                        pass
                else:
                    # fallback: tenta sinalizar pelo pid
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Erro ao encerrar por pid: {e}")
            finally:
                self._remove_pid()

        # Se temos um processo criado por nós, tenta encerrar também
        if self.app_process:
            try:
                self._terminate_proc(self.app_process)
            except Exception:
                pass
            self.app_process = None

        # Atualizar estado
        self.is_running = False
        self.starting = False

        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None

        # Remover arquivo temporário extraído de app.py (se criado)
        if getattr(self, '_extracted_app_path', None):
            try:
                os.remove(self._extracted_app_path)
            except Exception:
                pass
            self._extracted_app_path = None

        self.status_label.config(text="🛑 Aplicacao encerrada", style='Status.TLabel')
        self.url_label.config(text="")
        self.open_button.config(state='disabled')
        self.close_button.config(state='disabled')

        # fecha a janela após um pequeno atraso
        self.root.after(300, self.root.quit)

    def on_closing(self):
        """Evento de fechamento da janela"""
        if self.is_running or self.app_process:
            if messagebox.askyesno("Confirmar", "Deseja encerrar a aplicacao web?"):
                self.stop_application(force=True)
            else:
                return
        else:
            self.root.quit()

    def show_error(self, message):
        self.status_label.config(text=f"❌ {message}", style='Error.TLabel')
        self.open_button.config(state='disabled')
        self.close_button.config(state='disabled')
        try:
            messagebox.showerror("Erro", message)
        except Exception:
            print("Erro: ", message)


def run_server(args):
    from app import create_app
    import webbrowser as _webbrowser

    app = create_app()

    if not args.no_browser:
        def _open_browser():
            time.sleep(1.0)
            _webbrowser.open(f'http://{args.host}:{args.port}')
        threading.Thread(target=_open_browser, daemon=True).start()

    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port,
        use_reloader=False,
    )


def run_gui():
    root = tk.Tk()
    app = SistemaCaixaLauncher(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicacao encerrada pelo usuario")
    except Exception as e:
        print(f"Erro na interface: {e}")
    finally:
        # Garantir que todos os processos sejam encerrados
        if 'app' in locals() and app.is_running:
            app.stop_application()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--no-browser', action='store_true')

    args, _ = parser.parse_known_args()

    if args.server:
        run_server(args)
    else:
        run_gui()

if __name__ == "__main__":
    main()
