from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

# === CONFIGURATION ===
TEST_MODE = True           # ✅ Set True to simulate, False for real WhatsApp
BATCH_LIMIT = 3            # Max messages per run
MIN_DELAY = 10             # Min seconds between messages
MAX_DELAY = 20             # Max seconds between messages
LOG_FILE = "log_report.csv"

# Chrome options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")

# Fix: Use a local folder in the project directory for Windows compatibility
script_dir = os.path.dirname(os.path.realpath(__file__))
user_data_path = os.path.join(script_dir, "chrome_user_data")
options.add_argument(f"--user-data-dir={user_data_path}")

os.system("")

# Colors for printing
class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

print(style.BLUE)
print("**********************************************************")
print("**********************************************************")
print("***** ******")
print("***** THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
print("***** This tool was built by PadoSensei        ******")
print("***** https://github.com/PadoSensei         ******")
print("***** ******")
print("**********************************************************")
print("**********************************************************")
print(style.RESET)

# Read message
if not os.path.exists("message.txt"):
    with open("message.txt", "w", encoding="utf8") as f:
        f.write("Test message")

with open("message.txt", "r", encoding="utf8") as f:
    message = f.read()

print(style.YELLOW + '\nThis is your message-')
print(style.GREEN + message)
print("\n" + style.RESET)
message_encoded = quote(message)

# Read numbers
numbers = []
if os.path.exists("numbers.txt"):
    with open("numbers.txt", "r") as f:
        for line in f.read().splitlines():
            if line.strip() != "":
                numbers.append(line.strip())

total_number = len(numbers)
print(style.RED + f'We found {total_number} numbers in the file' + style.RESET)

# Setup CSV logging
if not os.path.isfile(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "phone_number", "status", "error"])

def log_result(phone, status, error=""):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone, status, error])

# Load already processed
processed = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 3:
                processed.add(row[1])

print(style.CYAN + f"Skipping {len(processed)} numbers already processed." + style.RESET)
unprocessed = [n for n in numbers if n not in processed]
print(style.YELLOW + f"{len(unprocessed)} numbers left to process." + style.RESET)

driver = None

if not TEST_MODE:
    try:
        # In modern Selenium, we don't need ChromeDriverManager if Selenium is updated
        driver = webdriver.Chrome(options=options)
        print('Once your browser opens up sign in to WhatsApp Web')
        driver.get('https://web.whatsapp.com')
        input(style.MAGENTA + "AFTER logging into WhatsApp Web is complete and your chats are visible, press ENTER..." + style.RESET)
    except Exception as e:
        print(style.RED + f"Error starting Chrome: {e}" + style.RESET)
        exit()

# Message sending loop
for idx, number in enumerate(unprocessed[:BATCH_LIMIT]):
    number = number.strip()
    if not number: continue

    print(style.YELLOW + f'{idx+1}/{min(len(unprocessed), BATCH_LIMIT)} => Sending to {number}.' + style.RESET)

    if TEST_MODE:
        print(style.CYAN + f"[TEST] Would send to {number}" + style.RESET)
        log_result(number, "SIMULATED")
        sleep(random.randint(MIN_DELAY, MAX_DELAY))
        continue

    try:
        url = f'https://web.whatsapp.com/send?phone={number}&text={message_encoded}'
        driver.get(url)
        
        # Wait for the message input box to appear
        input_box = WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        sleep(2) # Extra breathing room for the UI
        input_box.send_keys(Keys.ENTER)
        
        print(style.GREEN + f'Message sent to: {number}' + style.RESET)
        log_result(number, "SUCCESS")
        
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(style.CYAN + f"Waiting {delay}s..." + style.RESET)
        sleep(delay)
        
    except Exception as e:
        print(style.RED + f'Failed for {number}: {str(e)[:50]}...' + style.RESET)
        log_result(number, "FAILURE", str(e))

if driver:
    driver.quit()

# === SUMMARY ===
successes = 0
failures = 0
with open(LOG_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        if len(row) >= 3:
            if row[2] == "SUCCESS": successes += 1
            elif row[2] == "FAILURE": failures += 1

print(style.BLUE + "\n========== SUMMARY ==========" + style.RESET)
print(style.GREEN + f" Successes: {successes}" + style.RESET)
print(style.RED + f" Failures: {failures}" + style.RESET)
print(style.BLUE + "=============================\n" + style.RESET)