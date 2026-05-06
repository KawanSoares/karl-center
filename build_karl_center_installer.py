import os
import shutil
import subprocess
import sys


def run(cmd):
    print(f"\n$ {' '.join(str(c) for c in cmd)}\n{'─' * 60}")
    subprocess.run(cmd, check=True)


def main():
    print("=" * 60)
    print("  Karl Center — Build KarlCenterInstaller")
    print("=" * 60)

    print("\n[0/4] Limpando builds anteriores...")
    for item in ("build", "dist", "KarlCenter.spec", "KarlCenterInstaller.spec"):
        full = os.path.join(os.getcwd(), item)
        if os.path.isdir(full):
            shutil.rmtree(full, ignore_errors=True)
        elif os.path.isfile(full):
            try:
                os.remove(full)
            except PermissionError:
                print(f"  Aviso: nao foi possivel remover {item} (arquivo em uso?)")

    print("\n[1/4] Instalando dependencias de build...")
    run([sys.executable, "-m", "pip", "install",
         "pyinstaller", "customtkinter", "selenium>=4.6.0"])

    print("\n[2/4] Compilando o app (KarlCenter)...")
    run([sys.executable, "-m", "PyInstaller",
         "--noconfirm", "--onedir", "--windowed",
         "--name", "KarlCenter",
         "--collect-data", "customtkinter",
         "--collect-all", "selenium",
         "--hidden-import", "selenium.webdriver.chrome.webdriver",
         "--hidden-import", "selenium.webdriver.chrome.service",
         "--hidden-import", "selenium.webdriver.chrome.options",
         "--hidden-import", "selenium.webdriver.remote.webdriver",
         "--hidden-import", "selenium.webdriver.support.expected_conditions",
         "--hidden-import", "selenium.webdriver.common.by",
         "--hidden-import", "selenium.webdriver.common.keys",
         "gui_automator.py"])

    print("\n[3/4] Compilando o instalador (KarlCenterInstaller)...")
    sep = ";" if sys.platform == "win32" else ":"
    app_dir = os.path.join("dist", "KarlCenter")
    run([sys.executable, "-m", "PyInstaller",
         "--noconfirm", "--onefile", "--windowed",
         "--name", "KarlCenterInstaller",
         f"--add-data={app_dir}{sep}KarlCenter",
         "installer.py"])

    print("\n[4/4] Limpando arquivos temporarios...")
    for item in ("build", "KarlCenter.spec", "KarlCenterInstaller.spec"):
        full = os.path.join(os.getcwd(), item)
        if os.path.isdir(full):
            shutil.rmtree(full, ignore_errors=True)
        elif os.path.isfile(full):
            try:
                os.remove(full)
            except PermissionError:
                pass

    ext = ".exe" if sys.platform == "win32" else ""
    out = os.path.join("dist", f"KarlCenterInstaller{ext}")
    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"\n{'=' * 60}")
    print(f"  Concluido!")
    print(f"  Instalador: {os.path.abspath(out)}")
    print(f"  Tamanho:    {size_mb:.1f} MB")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
