from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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


def _wait_input_box(driver):
    return WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
    )


def _last_visible(elements):
    """Some elements (e.g. the send button) share the same icon between
    the regular chat compose bar and the attachment-preview overlay, and
    DOM order doesn't reliably match which one is actually on screen. Only
    one is normally visible at a time, so filter by that instead."""
    visible = [el for el in elements if el.is_displayed()]
    return visible[-1] if visible else elements[-1]


def _send_via_reload(driver, number, text):
    """Opens WhatsApp's send link with the message prefilled via URL, then
    presses Enter. Reliable for multi-line text, but reloads the page for
    every message."""
    url = f"https://web.whatsapp.com/send?phone={number}&text={quote(text)}"
    driver.get(url)

    input_box = _wait_input_box(driver)
    sleep(2)
    input_box.send_keys(Keys.ENTER)


def _type_text(driver, input_box, text):
    """Types text into a contenteditable box, sending newlines as
    Shift+Enter so they insert a line break instead of triggering an early
    send. Does not press the final Enter - callers decide how to submit."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            input_box.send_keys(line)
        if i < len(lines) - 1:
            ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(
                Keys.SHIFT
            ).perform()


def _send_via_typing(driver, text):
    """Types directly into the already-open chat, without reloading the
    page, then presses Enter to send."""
    input_box = _wait_input_box(driver)
    sleep(2)
    _type_text(driver, input_box, text)
    input_box.send_keys(Keys.ENTER)


_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


# NOTE: not currently called - run_bulk_messages raises before reaching
# this for attachment messages. Left in place for whoever picks this back
# up: the caption box and send button in WhatsApp Web's attachment-preview
# overlay share identical markup with the regular chat's own compose box
# and send button (no distinguishing attribute found so far), so the two
# couldn't be told apart reliably. Everything up to opening the preview
# and attaching the file itself was working.
def _send_attachment(driver, file_path, caption):
    """Attaches a file (image/document) to the currently open chat and
    sends it with an optional caption. WhatsApp Web routes images/videos
    and documents through separate attach-menu items and file inputs, so
    the file is classified by extension first."""
    is_image = os.path.splitext(file_path)[1].lower() in _IMAGE_EXTENSIONS

    attach_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[@data-icon='plus' or @data-icon='plus-rounded']")
        ),
        "botão de anexar (clip)",
    )
    attach_button.click()

    if is_image:
        # The image/video file input already exists in the DOM as soon as
        # the attach menu opens. Using it directly - without ever clicking
        # the "Fotos e vídeos" menu item - avoids triggering WhatsApp's own
        # click handler, which calls .click() on this same input. Chrome
        # still honors that as a real user gesture (it happens within the
        # activation window left by the attach-button click above) and
        # opens a native OS file dialog Selenium can't see or dismiss.
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@type='file'][contains(@accept, 'image')]")
            ),
            "input de arquivo (imagem)",
        )[-1]
    else:
        menu_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@role='menuitem'][@aria-label='Documento']")
            ),
            "item de menu 'Documento'",
        )
        driver.execute_script("arguments[0].click();", menu_item)
        sleep(1)
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//input[@type='file']")),
            "input de arquivo (documento)",
        )[-1]

    file_input.send_keys(os.path.abspath(file_path))

    caption_box = _last_visible(
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@contenteditable='true']")
            ),
            "caixa de legenda",
        )
    )
    sleep(2)
    if caption:
        _type_text(driver, caption_box, caption)

    send_button = _last_visible(
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[@data-icon='wds-ic-send-filled']")
            ),
            "botão de enviar",
        )
    )
    # A coordinate-based click can land on an overlapping layout element
    # instead of the icon itself, depending on window size. A JS click
    # dispatches directly to the element regardless of what visually
    # overlaps it.
    driver.execute_script("arguments[0].click();", send_button)
    sleep(2)


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
    reload_between_messages=False,
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

            if not reload_between_messages:
                driver.get(f"https://web.whatsapp.com/send?phone={number}")

            for msg_idx, message in enumerate(messages):

                if message["attachment"]:
                    # Sending attachments reliably requires distinguishing
                    # WhatsApp Web's attachment-preview caption/send controls
                    # from the regular chat's, which turned out to share
                    # identical markup in this build and couldn't be told
                    # apart consistently. Disabled until that's solved -
                    # see _send_attachment, which is otherwise ready to use.
                    raise RuntimeError(
                        "Envio de anexos (imagens/documentos) ainda não é "
                        "suportado de forma confiável. Remova o anexo desta "
                        "mensagem ou envie apenas texto."
                    )
                elif reload_between_messages:
                    _send_via_reload(driver, number, message["text"])
                else:
                    _send_via_typing(driver, message["text"])

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
        msgs = [{"text": text, "attachment": None} for text in split_messages(f.read())]

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
