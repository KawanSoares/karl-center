from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib.parse import quote
import os
import random
import sys
import csv
from datetime import datetime

# Configurações padrão
LOG_FILE = "log_report.csv"


class style:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


def split_messages(text):
    chunks, current = [], []
    for line in text.splitlines():
        if line.strip() == "---":
            chunks.append("\n".join(current).strip())
            current = []
        else:
            current.append(line)
    chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def log_result(phone, status, error=""):
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "phone_number", "status", "error"])

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone, status, error]
        )


def run_bulk_messages(
    numbers,
    messages,
    batch_limit,
    contact_min_delay,
    contact_max_delay,
    message_min_delay,
    message_max_delay,
    test_mode=False,
    log_callback=None,
):
    def report(text, color_code=style.RESET):
        if log_callback:
            log_callback(text)
        else:
            print(color_code + text + style.RESET)

    driver = None

    if not test_mode:
        if getattr(sys, "frozen", False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.realpath(__file__))

        try:
            options = ChromeOptions()

            # Only needed on machines where Chrome isn't installed via a
            # standard installer (e.g. Scoop), so Selenium Manager can't
            # auto-detect it.
            custom_binary = os.environ.get("KARL_CENTER_CHROME_PATH")
            if custom_binary:
                options.binary_location = custom_binary

            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument(
                f"--user-data-dir={os.path.join(script_dir, 'chrome_profile')}"
            )
            options.add_argument("--start-maximized")

            report("Iniciando Chrome...")
            driver = webdriver.Chrome(options=options)

        except Exception as chrome_error:
            report(
                f"Chrome indisponível ({chrome_error}). Tentando Edge...",
                style.YELLOW,
            )

            try:
                options = EdgeOptions()
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                options.add_argument(
                    f"--user-data-dir={os.path.join(script_dir, 'edge_profile')}"
                )
                options.add_argument("--start-maximized")

                report("Iniciando Edge...")
                driver = webdriver.Edge(options=options)

            except Exception as edge_error:
                report(f"Erro ao iniciar navegador:\n{edge_error}", style.RED)
                return

        try:
            report("Abrindo WhatsApp Web...")
            driver.get("https://web.whatsapp.com")

            if not log_callback:
                input(
                    style.MAGENTA + "Após fazer login, pressione ENTER..." + style.RESET
                )
            else:
                report("Aguardando login...")

                WebDriverWait(driver, 300).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )

        except Exception as e:
            report(f"Erro ao abrir WhatsApp Web:\n{e}", style.RED)
            driver.quit()
            return

    for idx, number in enumerate(numbers[:batch_limit]):

        report(f"Processando {idx + 1}/{batch_limit}: {number}", style.YELLOW)

        if test_mode:
            report(
                f"[TESTE] {len(messages)} mensagem(ns) enviada(s) para {number}",
                style.CYAN,
            )

            log_result(number, "SIMULATED")

            sleep(random.randint(contact_min_delay, contact_max_delay))
            continue

        try:

            for msg_idx, message in enumerate(messages):

                url = (
                    f"https://web.whatsapp.com/send"
                    f"?phone={number}&text={quote(message)}"
                )

                driver.get(url)

                input_box = WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@contenteditable='true']")
                    )
                )

                sleep(2)

                input_box.send_keys(Keys.ENTER)

                if msg_idx < len(messages) - 1:
                    msg_delay = random.randint(message_min_delay, message_max_delay)

                    report(f"Aguardando {msg_delay}s entre mensagens...")

                    sleep(msg_delay)

            report(f"✅ Sucesso: {number}", style.GREEN)

            log_result(number, "SUCCESS")

            if idx < batch_limit - 1:
                delay = random.randint(contact_min_delay, contact_max_delay)

                report(f"Aguardando {delay} segundos...")

                sleep(delay)

        except Exception as e:

            report(f"❌ Falha: {number}", style.RED)

            log_result(number, "FAILURE", str(e))

    if driver:
        driver.quit()

    report("--- Processo Finalizado ---", style.BLUE)


if __name__ == "__main__":

    with open("message.txt", "r", encoding="utf8") as f:
        msgs = split_messages(f.read())

    with open("numbers.txt", "r") as f:
        nums = [line.strip() for line in f if line.strip()]

    run_bulk_messages(
        nums,
        msgs,
        batch_limit=3,
        contact_min_delay=10,
        contact_max_delay=20,
        message_min_delay=5,
        message_max_delay=10,
    )
