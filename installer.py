import os
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from version import VERSION

if sys.platform == "win32":
    DEFAULT_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "KarlCenter")
else:
    DEFAULT_DIR = os.path.expanduser("~/.local/share/KarlCenter")

BG     = "#1a1a1a"
PANEL  = "#2a2a2a"
ACCENT = "#24a148"
TEXT   = "#eeeeee"
MUTED  = "#888888"

TERMS = """\
TERMOS DE USO — Karl Center WhatsApp Bulk Messenger
====================================================

Ao instalar e utilizar este software, você concorda com os seguintes termos:

1. USO RESPONSAVEL
   Esta ferramenta destina-se exclusivamente ao envio de mensagens para contatos que consentiram em recebe-las. O uso para envio de spam ou mensagens nao solicitadas e de responsabilidade exclusiva do usuario.

2. CONFORMIDADE COM O WHATSAPP
   O uso desta ferramenta pode violar os Termos de Servico do WhatsApp, podendo resultar no banimento da sua conta. O autor nao se responsabiliza por qualquer consequencia decorrente do uso indevido.

3. SEM GARANTIAS
   O software e fornecido "como esta", sem garantias de qualquer tipo. O autor nao se responsabiliza por danos diretos ou indiretos resultantes do uso deste software.

4. CODIGO ABERTO
   Este software e de codigo aberto. Voce pode modifica-lo e distribui-lo livremente, desde que mantenha este aviso de termos.

5. DEPENDENCIAS EXTERNAS
   Este software instala automaticamente bibliotecas de terceiros (Selenium, CustomTkinter, WebDriver Manager). Ao aceitar estes termos, voce tambem concorda com as licencas dessas bibliotecas.

Ao marcar "Li e aceito os termos", voce confirma que leu, entendeu e concorda com todas as condicoes acima.
"""


def get_resource(name):
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Karl Center v{VERSION} — Assistente de Instalacao")
        self.geometry("600x480")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.install_path      = tk.StringVar(value=DEFAULT_DIR)
        self.accepted          = tk.BooleanVar(value=False)
        self.create_shortcut   = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.launch_after      = tk.BooleanVar(value=True)

        self._alt_actions = {}
        self.bind_all("<Alt-KeyPress>", self._on_alt_key)

        self._build_chrome()
        self._pages = [
            self._page_welcome,
            self._page_terms,
            self._page_path,
            self._page_installing,
            self._page_done,
        ]
        self.go(0)

    # ── Layout ─────────────────────────────────────────

    def _build_chrome(self):
        hdr = tk.Frame(self, bg="#111111", height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Karl Center", bg="#111111", fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        tk.Label(hdr, text=f"v{VERSION} — Assistente de Instalacao", bg="#111111", fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")

        self._body = tk.Frame(self, bg=BG)
        self._body.pack(fill="both", expand=True, padx=30, pady=14)

        ftr = tk.Frame(self, bg=PANEL, height=56)
        ftr.pack(fill="x", side="bottom")
        ftr.pack_propagate(False)
        tk.Frame(ftr, bg="#3a3a3a", height=1).pack(fill="x")

        self._btn_back = tk.Button(
            ftr, text="<- Voltar", command=self._go_back, underline=3,
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9), relief="flat",
            padx=14, pady=7, cursor="hand2",
            activebackground=PANEL, activeforeground=TEXT)
        self._btn_back.pack(side="left", padx=16, pady=10)

        self._btn_next = tk.Button(
            ftr, text="Proximo ->", command=self._go_next, underline=0,
            bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=20, pady=7, cursor="hand2",
            activebackground="#1a7a38", activeforeground="white")
        self._btn_next.pack(side="right", padx=16, pady=10)

    def _clear(self):
        for w in self._body.winfo_children():
            w.destroy()

    # ── Keyboard mnemonics (Alt+letter) ─────────────────
    # A single <Alt-KeyPress> binding dispatched by keysym, rather than one
    # bind_all() per letter - individual <Alt-x> sequences turned out to be
    # unreliable on Windows without a real Menu widget attached.

    def _on_alt_key(self, event):
        action = self._alt_actions.get(event.keysym.lower())
        if action:
            try:
                action()
            except tk.TclError:
                pass  # widget from a page we've since navigated away from

    def _bind_alt(self, key, callback):
        self._alt_actions[key.lower()] = callback

    def _bind_back_key(self):
        # Invoke the button itself (like the other mnemonic-bound widgets)
        # rather than calling self._go_back() directly, so this still works
        # correctly if the button's command is ever temporarily overridden
        # (e.g. the install-error recovery path).
        self._bind_alt(
            "v", lambda: self._btn_back.invoke() if str(self._btn_back["state"]) == "normal" else None
        )

    def _set_next_key(self, key, action=None, underline=0):
        action = action or self._go_next
        old = getattr(self, "_next_key", None)
        if old and old != key:
            self._alt_actions.pop(old, None)
        self._next_key = key
        self._btn_next.config(underline=underline)
        self._bind_alt(
            key, lambda: action() if str(self._btn_next["state"]) == "normal" else None
        )

    # ── Navigation ─────────────────────────────────────

    def go(self, idx):
        self._current = idx
        self._clear()
        self._bind_back_key()
        self._btn_back.config(command=self._go_back)  # heal any error-recovery override
        if idx == 0:
            self._btn_back.pack_forget()
        else:
            self._btn_back.pack(side="left", padx=16, pady=10)
        self._pages[idx]()
        self._btn_back.config(state="normal" if 0 < idx < 3 else "disabled")
        if idx == 3:
            self._btn_next.config(state="disabled", text="Instalando...")
            self._btn_back.config(state="disabled")
        elif idx == 4:
            self._btn_next.config(text="Concluir ->", state="normal")
            self._set_next_key("c")
        else:
            self._btn_next.config(text="Proximo ->", state="normal")
            self._set_next_key("p")
            if idx == 1 and not self.accepted.get():
                self._btn_next.config(state="disabled")

    def _go_next(self):
        if self._current == 1 and not self.accepted.get():
            return
        if self._current == 4:
            self._finish()
            return
        if self._current < len(self._pages) - 1:
            nxt = self._current + 1
            self.go(nxt)
            if nxt == 3:
                threading.Thread(target=self._run_install, daemon=True).start()

    def _go_back(self):
        if 0 < self._current < 3:
            self.go(self._current - 1)

    # ── Pages ──────────────────────────────────────────

    def _page_welcome(self):
        tk.Label(self._body, text="Bem-vindo ao Karl Center!", bg=BG, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(pady=(24, 6))
        tk.Label(self._body, text="WhatsApp Bulk Messenger", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 11)).pack()
        tk.Frame(self._body, bg="#333", height=1).pack(fill="x", pady=18)
        tk.Label(self._body, justify="center", bg=BG, fg=TEXT, font=("Segoe UI", 10),
                 text=(
                     "Este assistente ira instalar o Karl Center no seu computador.\n\n"
                     "O programa permite enviar mensagens em massa pelo WhatsApp Web,\n"
                     "com interface grafica, controle de delays e registro de envios.\n\n"
                     "Clique em Proximo para continuar."
                 )).pack(pady=8)

    def _page_terms(self):
        tk.Label(self._body, text="Termos de Uso", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 6))
        frm = tk.Frame(self._body, bg=PANEL)
        frm.pack(fill="x")
        sb = tk.Scrollbar(frm)
        sb.pack(side="right", fill="y")
        txt = tk.Text(frm, yscrollcommand=sb.set, bg=PANEL, fg=TEXT,
                      font=("Consolas", 9), relief="flat", wrap="word",
                      padx=10, pady=8, cursor="arrow", height=15)
        txt.insert("1.0", TERMS)
        txt.config(state="disabled")
        txt.pack(fill="x")
        sb.config(command=txt.yview)

        def on_toggle():
            self._btn_next.config(state="normal" if self.accepted.get() else "disabled")

        chk_terms = tk.Checkbutton(
            self._body, text="  Li e aceito os termos de uso", underline=2,
            variable=self.accepted, command=on_toggle,
            bg=BG, fg=TEXT, font=("Segoe UI", 10),
            selectcolor="#333", activebackground=BG, activeforeground=TEXT
        )
        chk_terms.pack(anchor="w", pady=(10, 0))
        self._bind_alt("l", chk_terms.invoke)
        self._btn_next.config(state="normal" if self.accepted.get() else "disabled")

    def _page_path(self):
        tk.Label(self._body, text="Local de Instalacao", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 4))
        tk.Label(self._body, text="Escolha onde o Karl Center sera instalado:",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(self._body, bg=BG)
        row.pack(fill="x")
        tk.Entry(row, textvariable=self.install_path, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 10), relief="flat",
                 insertbackground=TEXT).pack(side="left", fill="x", expand=True,
                                             ipady=6, padx=(0, 8))
        btn_browse = tk.Button(row, text="Procurar...", underline=4,
                  bg="#444", fg=TEXT, relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=6, cursor="hand2",
                  command=self._browse)
        btn_browse.pack(side="right")
        # "r" collides with Windows' reserved system-menu "Restore"
        # accelerator and never reaches the app - "u" (proc-U-rar) instead.
        self._bind_alt("u", btn_browse.invoke)

        tk.Frame(self._body, bg="#333", height=1).pack(fill="x", pady=18)
        chk_shortcut = tk.Checkbutton(
            self._body, text="  Criar atalho na Area de Trabalho", underline=18,
            variable=self.create_shortcut,
            bg=BG, fg=TEXT, font=("Segoe UI", 10),
            selectcolor="#333", activebackground=BG, activeforeground=TEXT
        )
        chk_shortcut.pack(anchor="w")
        self._bind_alt("a", chk_shortcut.invoke)

        chk_start_menu = tk.Checkbutton(
            self._body, text="  Criar atalho no Menu Iniciar", underline=18,
            variable=self.create_start_menu,
            bg=BG, fg=TEXT, font=("Segoe UI", 10),
            selectcolor="#333", activebackground=BG, activeforeground=TEXT
        )
        chk_start_menu.pack(anchor="w")
        self._bind_alt("m", chk_start_menu.invoke)

        tk.Label(self._body,
                 text="É recomendado ter o Google Chrome instalado (o Microsoft Edge é usado como alternativa).",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(14, 0))

    def _page_installing(self):
        tk.Label(self._body, text="Instalando...", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 4))
        self._status_lbl = tk.Label(self._body, text="Iniciando...",
                                    bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self._status_lbl.pack(anchor="w")
        self._pbar = ttk.Progressbar(self._body, mode="indeterminate", length=540)
        self._pbar.pack(pady=8, fill="x")
        self._pbar.start(12)
        self._log = tk.Text(self._body, bg=PANEL, fg="#00ff88",
                            font=("Consolas", 8), relief="flat",
                            state="disabled", padx=8, pady=6, height=14)
        self._log.pack(fill="both", expand=True)

    def _page_done(self):
        tk.Label(self._body, text="Instalacao Concluida!", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 15, "bold")).pack(pady=(30, 10))
        tk.Label(self._body,
                 text=f"Karl Center instalado em:\n{self.install_path.get()}",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(pady=6)
        tk.Frame(self._body, bg="#333", height=1).pack(fill="x", pady=18)
        chk_launch = tk.Checkbutton(
            self._body, text="  Iniciar Karl Center agora", underline=2,
            variable=self.launch_after,
            bg=BG, fg=TEXT, font=("Segoe UI", 10),
            selectcolor="#333", activebackground=BG, activeforeground=TEXT
        )
        chk_launch.pack(anchor="w")
        self._bind_alt("i", chk_launch.invoke)

    # ── Helpers ────────────────────────────────────────

    def _browse(self):
        d = filedialog.askdirectory(title="Escolha o local de instalacao")
        if d:
            self.install_path.set(d)

    def _log_write(self, msg):
        self._log.config(state="normal")
        self._log.insert("end", f"{msg}\n")
        self._log.see("end")
        self._log.config(state="disabled")
        self._status_lbl.config(text=msg[:90])
        self.update_idletasks()

    def _finish(self):
        if self.launch_after.get():
            path = self.install_path.get()
            if sys.platform == "win32":
                os.startfile(os.path.join(path, "KarlCenter.exe"))
            else:
                subprocess.Popen([os.path.join(path, "KarlCenter")], cwd=path)
        self.destroy()

    # ── Installation ───────────────────────────────────

    def _run_install(self):
        try:
            path = self.install_path.get()
            self._log_write(f"Criando diretorio: {path}")
            os.makedirs(path, exist_ok=True)

            self._log_write("Copiando arquivos do programa...")
            shutil.copytree(get_resource("KarlCenter"), path, dirs_exist_ok=True)
            self._log_write("Arquivos copiados.")

            for fname in ("message.txt", "numbers.txt"):
                fpath = os.path.join(path, fname)
                if not os.path.exists(fpath):
                    open(fpath, "w").close()
            self._log_write("Arquivos de dados criados.")

            if self.create_shortcut.get() or self.create_start_menu.get():
                self._log_write("Criando atalhos...")
                self._make_shortcut(path)

            self._pbar.stop()
            self._pbar.config(mode="determinate", value=100)
            self._log_write("Concluido com sucesso!")
            self.after(600, lambda: self.go(4))

        except Exception as e:
            self._pbar.stop()
            self._log_write(f"ERRO: {e}")

            def recover():
                self._btn_next.config(state="disabled", text="Proximo ->", underline=0)
                self._btn_back.config(state="normal", command=lambda: self.go(2))

            self.after(0, recover)

    def _make_shortcut(self, install_path):
        if sys.platform == "win32":
            if self.create_shortcut.get():
                self._create_windows_shortcut(install_path, "Desktop")
            if self.create_start_menu.get():
                self._create_windows_shortcut(install_path, "Programs")
        else:
            exe = os.path.join(install_path, "KarlCenter")
            desktop_entry = (
                f"[Desktop Entry]\n"
                f"Name=Karl Center\n"
                f"Exec={exe}\n"
                f"Path={install_path}\n"
                f"Type=Application\n"
                f"Terminal=false\n"
                f"Comment=Karl Center - WhatsApp Bulk Messenger\n"
            )
            if self.create_start_menu.get():
                apps_dir = os.path.expanduser("~/.local/share/applications")
                os.makedirs(apps_dir, exist_ok=True)
                menu_file = os.path.join(apps_dir, "KarlCenter.desktop")
                with open(menu_file, "w") as f:
                    f.write(desktop_entry)
                os.chmod(menu_file, 0o755)
            if self.create_shortcut.get():
                desktop_file = os.path.expanduser("~/Desktop/KarlCenter.desktop")
                os.makedirs(os.path.dirname(desktop_file), exist_ok=True)
                with open(desktop_file, "w") as f:
                    f.write(desktop_entry)
                os.chmod(desktop_file, 0o755)

    def _create_windows_shortcut(self, install_path, special_folder):
        """special_folder is a .NET Environment.SpecialFolder name, e.g.
        "Desktop" or "Programs" (the Start Menu's per-user Programs folder).
        Resolving it via PowerShell - rather than assuming a fixed path
        like %USERPROFILE%\\Desktop - accounts for folders redirected by
        e.g. OneDrive "Known Folder Move". The existence check also happens
        inside PowerShell, rather than round-tripping an accented path
        (e.g. "Área de Trabalho") back through Python's subprocess text
        decoding."""
        exe = os.path.join(install_path, "KarlCenter.exe")
        ps = (
            f'$folder = [Environment]::GetFolderPath("{special_folder}");'
            f'$lnk = Join-Path $folder "Karl Center.lnk";'
            f'$s=(New-Object -COM WScript.Shell).CreateShortcut($lnk);'
            f'$s.TargetPath="{exe}";'
            f'$s.WorkingDirectory="{install_path}";'
            f'$s.Description="Karl Center - WhatsApp Bulk Messenger";'
            f'$s.Save();'
            'if (-not (Test-Path $lnk)) {'
            '    Write-Error "Shortcut not found after Save(): $lnk";'
            "    exit 1;"
            "}"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as f:
            f.write(ps)
            ps_file = f.name
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file],
            capture_output=True, text=True)
        try:
            os.remove(ps_file)
        except Exception:
            pass
        if result.returncode != 0:
            raise RuntimeError(
                f"Falha ao criar atalho em {special_folder} "
                f"(codigo {result.returncode}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )


if __name__ == "__main__":
    InstallerApp().mainloop()
