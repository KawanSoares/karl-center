import glob
import os
import shutil
import subprocess
import sys


def run(cmd):
    print(f"\n$ {' '.join(str(c) for c in cmd)}\n{'─' * 60}")
    subprocess.run(cmd, check=True)


def get_linux_python():
    """
    PyInstaller requer libpythonX.Y.so.1.0 no disco.
    O Python do sistema no Debian/Ubuntu frequentemente nao a inclui,
    mesmo com Py_ENABLE_SHARED=1, pois o .so nao e empacotado separadamente.
    Usa como fallback um Python do pyenv compilado com --enable-shared.
    """
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    full_ver = ".".join(str(v) for v in sys.version_info[:3])

    if glob.glob(f"/usr/**/libpython{ver}.so.1.0", recursive=True):
        return sys.executable

    pyenv_dir = os.path.expanduser("~/.pyenv/versions")
    if os.path.isdir(pyenv_dir):
        for entry in sorted(os.listdir(pyenv_dir), reverse=True):
            if entry.startswith(ver):
                candidate = os.path.join(pyenv_dir, entry, "bin", "python3")
                lib = os.path.join(pyenv_dir, entry, "lib", f"libpython{ver}.so.1.0")
                if os.path.exists(candidate) and os.path.exists(lib):
                    print(f"  Usando Python {entry} do pyenv (shared lib disponivel).")
                    return candidate

    pyenv = shutil.which("pyenv") or os.path.expanduser("~/.pyenv/bin/pyenv")
    if os.path.exists(pyenv):
        print(f"  Instalando Python {full_ver} com --enable-shared via pyenv...")
        env = {**os.environ, "PYTHON_CONFIGURE_OPTS": "--enable-shared"}
        result = subprocess.run([pyenv, "install", "-s", full_ver], env=env)
        if result.returncode == 0:
            candidate = os.path.expanduser(f"~/.pyenv/versions/{full_ver}/bin/python3")
            if os.path.exists(candidate):
                return candidate

    print(f"""
  ERRO: libpython{ver}.so.1.0 nao encontrada no sistema.
  PyInstaller precisa do Python compilado com --enable-shared.

  Instale o pyenv e recompile o Python:
    curl https://pyenv.run | bash
    source ~/.zshrc
    PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install {full_ver}
    pyenv local {full_ver}
    python build_karl_center_installer.py
""")
    sys.exit(1)


def main():
    is_windows = sys.platform == "win32"
    python_exe = sys.executable if is_windows else get_linux_python()

    print("=" * 60)
    print("  Karl Center — Build KarlCenterInstaller")
    print(f"  Plataforma: {'windows' if is_windows else 'linux'}")
    print("=" * 60)

    ext = ".exe" if is_windows else ""

    print("\n[0/5] Limpando builds anteriores...")
    for item in (
        "build",
        "dist",
        "KarlCenter.spec",
        "KarlCenterUninstaller.spec",
        "KarlCenterInstaller.spec",
    ):
        full = os.path.join(os.getcwd(), item)
        if os.path.isdir(full):
            shutil.rmtree(full, ignore_errors=True)
        elif os.path.isfile(full):
            try:
                os.remove(full)
            except PermissionError:
                print(f"  Aviso: nao foi possivel remover {item} (arquivo em uso?)")

    print("\n[1/5] Instalando dependencias de build...")
    run(
        [
            python_exe,
            "-m",
            "pip",
            "install",
            "pyinstaller",
            "customtkinter",
            "selenium>=4.6.0",
        ]
    )

    print("\n[2/5] Compilando o app (KarlCenter)...")
    run(
        [
            python_exe,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onedir",
            "--windowed",
            "--name",
            "KarlCenter",
            "--collect-data",
            "customtkinter",
            "--collect-all",
            "selenium",
            "--hidden-import",
            "selenium.webdriver.chrome.webdriver",
            "--hidden-import",
            "selenium.webdriver.chrome.service",
            "--hidden-import",
            "selenium.webdriver.chrome.options",
            "--hidden-import",
            "selenium.webdriver.remote.webdriver",
            "--hidden-import",
            "selenium.webdriver.support.expected_conditions",
            "--hidden-import",
            "selenium.webdriver.common.by",
            "--hidden-import",
            "selenium.webdriver.common.keys",
            "gui_automator.py",
        ]
    )

    print("\n[3/5] Compilando o desinstalador (KarlCenterUninstaller)...")
    run(
        [
            python_exe,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name",
            "KarlCenterUninstaller",
            "uninstaller.py",
        ]
    )

    print("\n[4/5] Compilando o instalador (KarlCenterInstaller)...")
    sep = ";" if is_windows else ":"
    app_dir = os.path.join("dist", "KarlCenter")
    uninstaller_exe = os.path.join("dist", f"KarlCenterUninstaller{ext}")
    run(
        [
            python_exe,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name",
            "KarlCenterInstaller",
            f"--add-data={app_dir}{sep}KarlCenter",
            f"--add-data={uninstaller_exe}{sep}.",
            "installer.py",
        ]
    )

    print("\n[5/5] Limpando arquivos temporarios...")
    for item in (
        "build",
        "KarlCenter.spec",
        "KarlCenterUninstaller.spec",
        "KarlCenterInstaller.spec",
    ):
        full = os.path.join(os.getcwd(), item)
        if os.path.isdir(full):
            shutil.rmtree(full, ignore_errors=True)
        elif os.path.isfile(full):
            try:
                os.remove(full)
            except PermissionError:
                pass

    out = os.path.join("dist", f"KarlCenterInstaller{ext}")
    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"\n{'=' * 60}")
    print(f"  Concluido!")
    print(f"  Instalador: {os.path.abspath(out)}")
    print(f"  Tamanho:    {size_mb:.1f} MB")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
