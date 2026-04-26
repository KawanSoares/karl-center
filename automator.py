from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib.parse import quote
import os
import random
import csv
from datetime import datetime

# Configurações padrão
LOG_FILE = "log_report.csv"

class style():
    RED = '\033[31m'; GREEN = '\033[32m'; YELLOW = '\033[33m'
    BLUE = '\033[34m'; MAGENTA = '\033[35m'; CYAN = '\033[36m'; RESET = '\033[0m'

def log_result(phone, status, error=""):
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "phone_number", "status", "error"])
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone, status, error])

def run_bulk_messages(numbers, message, batch_limit, min_delay, max_delay, test_mode=False, log_callback=None):
    """Função principal que pode ser chamada pela GUI ou via terminal"""
    def report(text, color_code=style.RESET):
        if log_callback:
            log_callback(text)
        else:
            print(color_code + text + style.RESET)

    driver = None
    message_encoded = quote(message)

    if not test_mode:
        try:
            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            script_dir = os.path.dirname(os.path.realpath(__file__))
            options.add_argument(f"--user-data-dir={os.path.join(script_dir, 'chrome_profile')}")
            
            driver = webdriver.Chrome(options=options)
            report("Abrindo WhatsApp Web...")
            driver.get('https://web.whatsapp.com')
            
            if not log_callback:
                input(style.MAGENTA + "Após logar, pressione ENTER no terminal..." + style.RESET)
            else:
                report("Aguardando login (detectando painel lateral)...")
                while True:
                    try:
                        driver.find_element(By.XPATH, '//*[@id="side"]')
                        break
                    except:
                        sleep(2)
        except Exception as e:
            report(f"Erro ao iniciar Chrome: {e}", style.RED)
            return

    for idx, number in enumerate(numbers[:batch_limit]):
        report(f"Processando {idx+1}/{batch_limit}: {number}", style.YELLOW)
        
        if test_mode:
            report(f"[TESTE] Mensagem enviada para {number}", style.CYAN)
            log_result(number, "SIMULATED")
            sleep(random.randint(min_delay, max_delay))
            continue

        try:
            url = f'https://web.whatsapp.com/send?phone={number}&text={message_encoded}'
            driver.get(url)
            input_box = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            sleep(2)
            input_box.send_keys(Keys.ENTER)
            report(f"✅ Sucesso: {number}", style.GREEN)
            log_result(number, "SUCCESS")
            
            if idx < batch_limit - 1:
                delay = random.randint(min_delay, max_delay)
                report(f"Aguardando {delay}s...")
                sleep(delay)
        except Exception as e:
            report(f"❌ Falha: {number}", style.RED)
            log_result(number, "FAILURE", str(e))

    if driver:
        driver.quit()
    report("--- Processo Finalizado ---", style.BLUE)

if __name__ == "__main__":
    # Lógica original para funcionamento via comando
    with open("message.txt", "r", encoding="utf8") as f: msg = f.read()
    with open("numbers.txt", "r") as f:
        nums = [line.strip() for line in f.read().splitlines() if line.strip()]
    
    run_bulk_messages(nums, msg, batch_limit=3, min_delay=10, max_delay=20)