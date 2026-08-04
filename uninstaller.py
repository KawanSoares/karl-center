import os
import subprocess
import sys
import tempfile
import tkinter as tk

from version import VERSION

BG     = "#1a1a1a"
PANEL  = "#2a2a2a"
DANGER = "#c0392b"
TEXT   = "#eeeeee"
MUTED  = "#888888"

UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\KarlCenter"


def get_install_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_special_folder(name):
    """Resolves a .NET Environment.SpecialFolder (e.g. "Desktop", "Programs")
    via PowerShell, so redirected folders (e.g. OneDrive "Known Folder Move")
    resolve correctly instead of assuming a fixed %USERPROFILE% path."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f'[Environment]::GetFolderPath("{name}")'],
        capture_output=True, text=True)
    path = result.stdout.strip()
    return path if result.returncode == 0 and path else None


class UninstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Karl Center v{VERSION} — Desinstalar")
        self.geometry("480x340")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.install_dir = get_install_dir()
        self._page_confirm()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _page_confirm(self):
        self._clear()
        tk.Label(self, text="Desinstalar Karl Center", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(24, 10))
        tk.Label(
            self, justify="left", bg=BG, fg=MUTED, font=("Segoe UI", 10),
            text=(
                "Isso ira remover permanentemente:\n\n"
                f"  •  {self.install_dir}\n"
                "  •  Atalho na Area de Trabalho (se existir)\n"
                "  •  Atalho no Menu Iniciar (se existir)\n\n"
                "Esta acao nao pode ser desfeita."
            ),
        ).pack(padx=30, pady=6, fill="x")

        btns = tk.Frame(self, bg=BG)
        btns.pack(pady=28)
        tk.Button(
            btns, text="Cancelar", command=self.destroy,
            bg=PANEL, fg=TEXT, relief="flat", padx=20, pady=8,
            cursor="hand2", activebackground=PANEL, activeforeground=TEXT,
        ).pack(side="left", padx=8)
        tk.Button(
            btns, text="Desinstalar", command=self._do_uninstall,
            bg=DANGER, fg="white", relief="flat", padx=20, pady=8,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            activebackground="#96281b", activeforeground="white",
        ).pack(side="left", padx=8)

    def _page_working(self):
        self._clear()
        tk.Label(self, text="Desinstalando...", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(60, 10))
        tk.Label(self, text="Esta janela pode ser fechada.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack()

    def _do_uninstall(self):
        self._page_working()
        self.update_idletasks()

        desktop = get_special_folder("Desktop")
        programs = get_special_folder("Programs")

        lines = [
            "@echo off",
            "taskkill /f /im KarlCenter.exe >nul 2>nul",
            "timeout /t 2 /nobreak >nul",
        ]
        if desktop:
            lnk = os.path.join(desktop, "Karl Center.lnk")
            lines.append(f'del /f /q "{lnk}" >nul 2>nul')
        if programs:
            lnk = os.path.join(programs, "Karl Center.lnk")
            lines.append(f'del /f /q "{lnk}" >nul 2>nul')
        lines.append(f'reg delete "HKCU\\{UNINSTALL_KEY}" /f >nul 2>nul')
        lines.append(f'rmdir /s /q "{self.install_dir}"')
        lines.append('(goto) 2>nul & del "%~f0"')

        bat_path = os.path.join(tempfile.gettempdir(), "karlcenter_uninstall.bat")
        with open(bat_path, "w", encoding="mbcs") as f:
            f.write("\r\n".join(lines) + "\r\n")

        subprocess.Popen(
            ["cmd", "/c", bat_path],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        self.after(400, self.destroy)


if __name__ == "__main__":
    UninstallerApp().mainloop()
